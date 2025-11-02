import os
import sys
import requests
from dotenv import load_dotenv
from PIL import Image

def generate_image(prompt: str, out_path: str = "out.png"):
    load_dotenv()
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing STABILITY_API_KEY in environment or .env")

    url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*",
    }

    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
        "aspect_ratio": (None, "16:9"),
    }

    resp = requests.post(url, headers=headers, files=files, timeout=120)
    if resp.status_code != 200:
        try:
            print("Error:", resp.status_code, resp.json())
        except Exception:
            print("Error:", resp.status_code, resp.text[:500])
        resp.raise_for_status()

    # Save original result
    with open(out_path, "wb") as f:
        f.write(resp.content)

    # Resize to target game size
    try:
        img = Image.open(out_path)
        img = img.resize((1920, 1080), Image.LANCZOS)
        img.save(out_path)
    except Exception as e:
        print("Warning: Could not resize image:", e)

    return out_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ImageGen.py \"your prompt here\" [out.png]")
        sys.exit(1)

    prompt = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) >= 3 else "Images/out.png"
    path = generate_image(prompt, out_path)
    print(f"Saved image to {path}")