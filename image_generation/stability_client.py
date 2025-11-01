# server/stability_client.py
import os, time, json, base64, hashlib
from typing import Optional, Dict, Any
import requests
from PIL import Image, ImageDraw
from dotenv import load_dotenv

# ==== load .env from project root explicitly ====
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(ROOT, ".env"), override=True)

# Primary: stable SDXL v1 JSON endpoint
STAB_URL_V1 = os.getenv(
    "STABILITY_URL_V1",
    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
)
# Fallback: v2beta/core (multipart + Accept: image/*)
STAB_URL_V2BETA = os.getenv(
    "STABILITY_URL_V2BETA",
    "https://api.stability.ai/v2beta/stable-image/generate/core",
)

API_KEY  = os.getenv("STABILITY_API_KEY")
TIMEOUT  = int(os.getenv("STABILITY_TIMEOUT", "60"))
RETRIES  = int(os.getenv("STABILITY_RETRIES", "3"))

WIDTH, HEIGHT = 1024, 576
CFG, STEPS = 7.0, 30


def _hash_int(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16) % 10**9


def build_prompt(scene: Dict[str, Any], style_bible: str) -> str:
    ch_bits = []
    for c in scene.get("characters", []):
        lk = c.get("look_key") or c.get("name", "")
        pose = c.get("pose", "")
        ch_bits.append(f"{lk} {('pose: '+pose) if pose else ''}".strip())
    ch = ", ".join(ch_bits) if ch_bits else "no characters"
    bg = scene.get("bg", {})
    mood = scene.get("mood", "")
    cam  = scene.get("camera", "")
    return (
        f"{style_bible}. visual novel composition, clean background, no text, no captions. "
        f"Camera: {cam}. Mood: {mood}. "
        f"Background: {bg.get('location','')}, {bg.get('time','')}. "
        f"Characters: {ch}."
    )


def _mock_image(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new("RGB", (1280, 720), (32, 32, 44))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), text[:500], fill=(230, 230, 240))
    img.save(path)


# ---------- SDXL v1 (JSON) ----------
def _post_v1_sdxl(prompt: str, seed: int) -> Optional[bytes]:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "text_prompts": [{"text": prompt, "weight": 1.0}],
        "width": WIDTH,
        "height": HEIGHT,
        "cfg_scale": CFG,
        "steps": STEPS,
        "samples": 1,
        "seed": seed,
    }
    r = requests.post(STAB_URL_V1, headers=headers, json=payload, timeout=TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        arts = data.get("artifacts", [])
        if arts and arts[0].get("base64"):
            return base64.b64decode(arts[0]["base64"])
    return None


# ---------- v2beta/core (multipart) ----------
def _post_v2beta_core(prompt: str, seed: int) -> Optional[bytes]:
    """
    Требует multipart/form-data и Accept: image/*
    Поля шлём как files={name: (None, value)}.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "image/*",
    }
    fields = {
        "prompt": prompt,
        "output_format": "png",
        "width": str(WIDTH),
        "height": str(HEIGHT),
        "seed": str(seed),
        "steps": str(STEPS),
        "cfg_scale": str(CFG),
    }
    files = {k: (None, v) for k, v in fields.items()}
    r = requests.post(STAB_URL_V2BETA, headers=headers, files=files, timeout=TIMEOUT)

    if r.status_code == 200 and "image" in r.headers.get("Content-Type", "").lower():
        return r.content

    try:
        j = r.json()
        b64 = j.get("image")
        if not b64 and isinstance(j.get("artifacts"), list) and j["artifacts"]:
            b64 = j["artifacts"][0].get("base64")
        if b64:
            return base64.b64decode(b64)
    except Exception:
        pass
    return None


# ---------- Public API ----------
def render_scene(
    scene: Dict[str, Any],
    style_bible: str,
    refs: Optional[Dict[str, Any]] = None,
    out_dir: str = os.path.join(os.path.dirname(__file__), "..", "cdn"),
    force: bool = False
) -> Optional[str]:
    assert "id" in scene, "scene must have an 'id'"
    sid = scene["id"]

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.abspath(os.path.join(out_dir, f"scene_{sid}.png"))
    if os.path.exists(out_path) and not force:
        return out_path

    names = "-".join(sorted([c.get("name","") for c in scene.get("characters", [])]))
    base = f"{names}|{scene.get('camera','')}|{scene.get('mood','')}|{scene.get('bg',{})}|{sid}"
    seed = scene.get("seed") or (_hash_int(base) % 1_000_000_000)
    prompt = build_prompt(scene, style_bible)

    if not API_KEY:
        print(f"⚠️  No STABILITY_API_KEY → MOCK for {sid}")
        _mock_image(out_path, f"[MOCK]\n{sid}\n{prompt}")
        return out_path

    print(f"🔵 Rendering {sid} (seed={seed}) via Stability SDXL v1 ...")
    for attempt in range(1, RETRIES + 1):
        try:
            blob = _post_v1_sdxl(prompt, seed)
            if blob:
                with open(out_path, "wb") as f:
                    f.write(blob)
                print(f"✅ Done {sid} -> {out_path}")
                return out_path
            time.sleep(0.6 * attempt)
        except Exception:
            time.sleep(0.6 * attempt)

    print(f"🟣 Trying v2beta/core for {sid} ...")
    for attempt in range(1, RETRIES + 1):
        try:
            blob = _post_v2beta_core(prompt, seed)
            if blob:
                with open(out_path, "wb") as f:
                    f.write(blob)
                print(f"✅ Done (v2beta) {sid} -> {out_path}")
                return out_path
            time.sleep(0.6 * attempt)
        except Exception:
            time.sleep(0.6 * attempt)

    print(f"⚠️  Fallback to MOCK for {sid}")
    _mock_image(out_path, f"[FAILED→MOCK]\n{sid}\n{prompt[:180]}")
    return out_path
