import os, json
from dotenv import load_dotenv

# === Load .env explicitly from project root ===
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(ROOT, ".env")
print(f"🧭 Loading .env from: {ENV_PATH}")
load_dotenv(dotenv_path=ENV_PATH, override=True)

from stability_client import render_scene

print("🔍 STABILITY_API_KEY loaded? ", bool(os.getenv("STABILITY_API_KEY")))

# load sample.json
data = json.load(open(os.path.join(ROOT, "sample.json"), "r", encoding="utf-8"))
style_bible = data["style_bible"]
scenes = data["scenes"]

out_dir = os.path.join(ROOT, "cdn")

print("Starting offline render test...\n")
preload = scenes[:3]

for sc in preload:
    path = render_scene(sc, style_bible, refs=None, out_dir=out_dir, force=True)
    print(f"{sc['id']}  ->  {path}")

print("\n✅ Done! Check the 'cdn' folder for scene_s001.png etc.")
