"""
Visual Novel Story Generator
Main entry point - orchestrates story collection and generation
"""

import os
from story_collector import collect_story_input, save_story_json, load_story_json
from story_generator import generate_story_from_json
from script_generator import generate_script_rpy_file
from process_story import generate_all_images

if __name__ == "__main__":
    print("=" * 60)
    print("Visual Novel Story Generator")
    print("=" * 60)
    
    story_data = collect_story_input()
    
    save_story_json(story_data)

    generate_story_from_json("user_story_input.json")

    generate_script_rpy_file("generated_story.txt")

    generate_all_images("generated_story.txt", "VN_Creator/game/images/")

    print("Your Visual Novel Game is ready to launch")






