import time
import os

# Define the output directory
CDN_DIR = "cdn"


def render_scene(scene: dict, style_bible: str) -> str:
    """
    Mock function for P3.
    This simulates the Stability AI rendering process.
    """

    # Create the cdn directory if it doesn't exist
    os.makedirs(CDN_DIR, exist_ok=True)

    scene_id = scene['id']
    filename = f"scene_{scene_id}.png"
    output_path = os.path.join(CDN_DIR, filename)

    print(f"[Worker] Rendering scene {scene_id}...")

    # --- This is the mock "work" ---

    # NEW: ADD THIS IF/ELSE BLOCK TO SIMULATE A FAILURE
    if scene_id == "s002":
        print(f"[Worker] !!! SIMULATING A FAILURE FOR SCENE {scene_id} !!!")
        time.sleep(1)  # Simulate a short attempt
        raise Exception(f"Simulated render failure for {scene_id}")
    else:
        # Simulate a 3-second render time for others
        time.sleep(3)

        # --- End mock "work" ---

    # Create a dummy file to simulate the final image
    try:
        with open(output_path, 'wb') as f:
            f.write(b"")
        print(f"[Worker] ...Finished rendering {scene_id}. Saved to {output_path}")
        return filename
    except Exception as e:
        print(f"[Worker] ERROR rendering {scene_id}: {e}")
        raise e