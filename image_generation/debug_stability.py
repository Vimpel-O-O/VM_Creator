import os, requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("STABILITY_API_KEY")

url = "https://api.stability.ai/v2beta/stable-image/generate/core"

headers = {
    "Authorization": f"Bearer {key}",
    "Accept": "image/*",       
}

fields = {
    "prompt": "anime watercolor, neon street at night, visual novel background, no text, no captions",
    "width": "768",
    "height": "432",
    "cfg_scale": "7",
    "steps": "30",
    "output_format": "png",
    "seed": "12345",
}

files = {k: (None, v) for k, v in fields.items()}

print("🧠 Sending request (multipart) to Stability v2beta/core...")
r = requests.post(url, headers=headers, files=files, timeout=90)

print("Status:", r.status_code)
ct = r.headers.get("Content-Type","")
print("Content-Type:", ct)

if r.status_code == 200 and "image" in ct.lower():
    out = os.path.join(os.path.dirname(__file__), "..", "cdn", "debug_core.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(r.content)
    print("✅ Saved:", os.path.abspath(out))
else:
    print("❌ Body (first 400):", r.text[:400])
