import json
import os
import sys

# Try to import the generate_image function from your existing script
try:
    from ImageGeneration import generate_image
except ImportError:
    print("Error: Could not find 'ImageGeneration.py'.")
    print("Make sure this script is in the same directory as 'ImageGeneration.py'.")
    sys.exit(1)

# Try to import dotenv, which is required by ImageGeneration.py
try:
    import dotenv
except ImportError:
    print("Error: The 'python-dotenv' package is not installed.")
    print("Please install it by running: pip install python-dotenv")
    sys.exit(1)

# ---------------------

def create_prompt_for_scene(scene: dict, style: str) -> str:
    """
    Constructs a detailed, comma-separated prompt for the image generation AI
    based on the scene's data.
    """
    prompt_parts = []

    # 1. Style (from the style_bible)
    prompt_parts.append(style)

    # 2. Background / Setting
    bg = scene.get('bg', {})
    prompt_parts.append(f"Background: {bg.get('location', 'unknown location')}, {bg.get('time', 'unknown time')}")

    # 3. Characters (This is the format you requested)
    char_descs = []
    for char in scene.get('characters', []):
        # Combines the key and pose for a full description
        char_desc = f"{char.get('name', 'character')} ({char.get('look_key', '')}, pose: {char.get('pose', '')})"
        char_descs.append(char_desc)

    if char_descs:
        prompt_parts.append("Characters: " + ", ".join(char_descs))

    # 4. Camera (This is the format you requested)
    prompt_parts.append(f"Camera: {scene.get('camera', 'medium shot')}")

    # 5. Mood (This is the format you requested)
    prompt_parts.append(f"Mood: {scene.get('mood', 'neutral')}")

    # Join all parts into a single string
    return ", ".join(prompt_parts)


def generate_all_images(story_data, output):

    # Load the story JSON
    try:
        with open(story_data, 'r') as f:
            story_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Story file not found at '{story_data}'")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON from '{story_data}'. Check for syntax errors.")
        return

    # Get the global style and all scenes
    style = story_data.get('style_bible', 'anime')
    scenes = story_data.get('scenes', [])

    if not scenes:
        print("No scenes found in the story file.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output, exist_ok=True)

    # Loop through each scene and generate an image
    print("Generating image (this may take a moment)...")

    for scene in scenes:
        scene_id = scene.get('id', 'unknown_scene')

        # 1. Create the detailed prompt
        prompt = create_prompt_for_scene(scene, style)

        # 2. Define the output path
        output_path = os.path.join(output, f"{scene_id}.png")

        # 3. Call your generate_image function
        try:
            generate_image(prompt, output_path)
        except Exception as e:
            print(f"Error while generating image for {scene_id}: {e}")
            # Continue to the next scene even if one fails
            continue

    print("\n--- Image generation complete! ---")