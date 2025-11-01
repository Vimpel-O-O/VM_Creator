"""
Visual Novel Story Generator
Main entry point - orchestrates story collection and generation
"""




import os
from story_collector import collect_story_input, save_story_json, load_story_json
from story_generator import generate_story_from_json

if __name__ == "__main__":
    print("=" * 60)
    print("Visual Novel Story Generator")
    print("=" * 60)
    

    # Step 1: Collect story input
    story_data = collect_story_input()
    
    # Step 2: Save to JSON file
    save_story_json(story_data)
    
    # Step 3: Generate story with Gemini
    generate_story_from_json("user_story_input.json")

   







