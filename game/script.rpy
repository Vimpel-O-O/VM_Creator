# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

init python:
    import requests
    import os

    IMAGE_DIR = os.path.join(renpy.config.gamedir, "images")

    def download_image(url, filename):
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)

        path = os.path.join(IMAGE_DIR, filename)
        r = requests.get(url, timeout=15)
        with open(path, "wb") as f:
            f.write(r.content)
        return path

    def send_to_api(prompt):
        url = "http://127.0.0.1:5000/generate"
        resp = requests.post(url, json={"prompt": prompt}, timeout=15)
        data = resp.json()

        text = data.get("text", "")
        image_url = data.get("image_url")

        image_path = None
        if image_url:
            image_path = download_image(image_url, "scene_1.png")

        return text, image_path

default prompt_text = ""
# The game starts here.

label start:
    call screen prompt_screen
    "Loading..."
    $ story_text, img_path = send_to_api(prompt_text)
    if img_path:
        show expression Image(img_path) as bg
    "[story_text]"
    return
