# generate_script_rpy_file.py
import os, re, json, hashlib, textwrap
from pathlib import Path
from dotenv import load_dotenv

# Optional Gemini client (install: pip install google-generativeai)
try:
    import google.generativeai as genai
except ImportError:
    genai = None


def _strip_code_fences(txt: str) -> str:
    """Pull out the first {...} block, in case the input is fenced with ```json ... ```."""
    if "```" in txt:
        # extract the first JSON-looking block
        m = re.search(r"\{.*\}", txt, flags=re.S)
        if m:
            return m.group(0)
    return txt


def _hex_color_for_name(name: str) -> str:
    """Deterministic pretty-ish color per character."""
    h = hashlib.md5(name.encode()).hexdigest()
    # Use 3 bytes, brighten a bit
    r = int(h[0:2], 16); g = int(h[2:4], 16); b = int(h[4:6], 16)
    r = (r + 128) // 2; g = (g + 128) // 2; b = (b + 128) // 2
    return f"#{r:02x}{g:02x}{b:02x}"


def _abbr(name: str, existing: set) -> str:
    """
    Very small helper to make Ren'Py variable names: alex -> a, jony -> j, collide safely.
    """
    cand = name.strip().split()[0].lower()[0]
    if cand not in existing:
        return cand
    # fallback: next letters, then full name letters
    for ch in name.lower():
        if ch.isalpha() and ch not in existing:
            return ch
    # final fallback
    i = 2
    base = re.sub(r"[^a-z]", "", name.lower()) or "c"
    cand = base
    while cand in existing:
        cand = f"{base}{i}"
        i += 1
    return cand


def _local_fallback_rpy(story: dict) -> str:
    """
    Deterministic converter (no LLM). Rule set:
    - Define a Character for each unique name in story['scenes'][*]['characters'].
    - For each scene id sNNN -> `show NNNN`
    - Dialogue rules:
        * If a line starts with "Name: ..." and Name matches a defined character -> that speaker says it.
        * Else the FIRST character in that scene says it (so it's not narrator text).
    """
    # Collect characters
    names = []
    for sc in story.get("scenes", []):
        for ch in sc.get("characters", []):
            nm = ch.get("name", "").strip()
            if nm and nm not in names:
                names.append(nm)

    # Build var names & colors
    var_for = {}
    used = set()
    lines = []

    for nm in names:
        var = _abbr(nm, used)
        used.add(var)
        var_for[nm] = var
        color = _hex_color_for_name(nm)
        lines.append(f"define {var} = Character('{nm}', color=\"{color}\")")

    if lines:
        lines.append("")  # spacer

    lines.append("label start:")
    lines.append("")

    # Scenes
    for sc in story.get("scenes", []):
        sid = sc.get("id", "")
        # map s001 -> 0001
        m = re.search(r"(\d+)", sid)
        img_id = f"{int(m.group(1)):04d}" if m else sid
        lines.append(f"    show {img_id}")
        lines.append("")

        scene_chars = [c.get("name", "").strip() for c in sc.get("characters", []) if c.get("name")]
        default_speaker = var_for.get(scene_chars[0], None) if scene_chars else None

        for raw in sc.get("dialogue", []):
            text = raw.strip()
            # Try "Name: text"
            m = re.match(r"^\s*([A-Z][A-Za-z0-9_ ]{0,30})\s*:\s*(.+)$", text)
            if m:
                nm, content = m.group(1).strip(), m.group(2).strip()
                if nm in var_for:
                    lines.append(f'    {var_for[nm]} "{content}"')
                    continue
            # Default to first listed character if available; else narrator
            if default_speaker:
                lines.append(f'    {default_speaker} "{text}"')
            else:
                lines.append(f'    "{text}"')
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _gemini_prompt_template() -> str:
    # Clear, strict instructions; output ONLY Ren'Py code.
    return textwrap.dedent("""
    You are a Ren'Py Visual Novel writer.

    Convert the provided JSON scene spec into a single .rpy script with:
    1) One Character definition per unique character name:  define <var> = Character('<Name>', color="#RRGGBB")
       - Use short lowercase variable names derived from names (e.g., Alex->a, Jony->j). Ensure uniqueness.
    2) A single `label start:` section that plays all scenes in order.
    3) For each scene id like "s001", emit `show s001`.
    4) Dialogue rules:
       - If a line starts with "Name: ..." and Name matches a defined character, that character speaks.
       - Otherwise, the FIRST character listed in that scene speaks that line (not narrator text).
    5) No explanations, no Markdown, no backticks — output ONLY valid Ren'Py script text.
    6) do not use special chars like: "%"

    Keep spacing like:

    define a = Character('Alex', color="#c8ffc8")
    define j = Character('Jony', color="#c8c8ff")

    label start:

        show s001

        a "First line..."
        J "Second line..."

        show s002

        a "Reply..."

    Now convert this JSON:
    """ ).strip()


def _call_gemini(json_text: str) -> str:
    if genai is None:
        raise RuntimeError("google-generativeai not installed. Run: pip install google-generativeai")
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY (or GEMINI_API_KEY) in your environment/.env")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.5-pro")  # adjust if you use a different model
    prompt = _gemini_prompt_template() + "\n\n" + json_text

    resp = model.generate_content(prompt)
    out = resp.text or ""
    # Strip any accidental code fences
    out = re.sub(r"^```.*?\n|\n```$", "", out, flags=re.S)
    return out.strip() + ("\n" if not out.endswith("\n") else "")


def generate_script_rpy_file(input_txt_path: str,
                             out_path: str = "VN_Creator/game/script.rpy",
                             prefer_gemini: bool = True) -> str:
    """
    Reads the text file containing your JSON (possibly fenced), generates a Ren'Py script,
    and writes it to `out_path`. Returns the script text.

    Set prefer_gemini=False to force the local deterministic converter.
    """
    raw = Path(input_txt_path).read_text(encoding="utf-8")
    json_str = _strip_code_fences(raw)

    try:
        story = json.loads(json_str)
    except json.JSONDecodeError:
        # If it's not clean JSON (e.g., had comments), try to call Gemini directly.
        story = None

    script = None
    if prefer_gemini and genai is not None:
        try:
            # Use Gemini on the raw JSON text when available
            script = _call_gemini(json_str)
        except Exception as e:
            print(f"[warn] Gemini failed ({e}); falling back to local converter.")

    if script is None:
        if story is None:
            raise ValueError("Could not parse JSON and Gemini is disabled/unavailable.")
        script = _local_fallback_rpy(story)

    Path(out_path).write_text(script, encoding="utf-8")
    return script


if __name__ == "__main__":
    # Example usage:
    # python generate_script_rpy_file.py
    demo_in = "generated_story.txt"  # your txt that contains the JSON you pasted
    if Path(demo_in).exists():
        rpy = generate_script_rpy_file(demo_in, out_path="VN_Creator/game/script.rpy", prefer_gemini=True)
        print("Wrote:", "game/script_auto.rpy")
        print("\n--- preview ---\n")
        print("\n".join(rpy.splitlines()[:40]))
    else:
        print("Place your JSON-in-a-text-file at ./story.txt and rerun.")