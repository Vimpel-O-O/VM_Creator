"""
Story Input Collector Module
Handles collecting story details from user and saving/loading JSON files
"""

import json


def collect_story_input():
    """
    Interactive function that asks questions and collects story details.
    Returns a dictionary with story information.
    """
    print("=" * 60)
    print("Story Input Collector")
    print("=" * 60)
    print("\nAnswer the following questions about your story:\n")
    
    story_data = {}
    
    # 1. Story narrative
    print("1. Enter your story narrative:")
    print("   (Describe the plot, characters, and key events)")
    print("   (Press Enter once to skip, or Enter on an empty line when finished)\n")
    
    story_lines = []
    first_line = input()
    if first_line.strip() == "":
        # Skip if first line is empty
        story_data["narrative"] = "up to you"
    else:
        story_lines.append(first_line)
        # Continue collecting lines until empty line
        while True:
            line = input()
            if line.strip() == "":
                break
            story_lines.append(line)
        story_data["narrative"] = "\n".join(story_lines)
    
    # 2. Genre
    print("\n2. What genre or theme? (e.g., mystery, romance, sci-fi, drama)")
    print("   (Press Enter for 'up to you')")
    genre_input = input("Genre: ").strip()
    story_data["genre"] = genre_input if genre_input else "up to you"
    
    # 3. Art style
    print("\n3. Preferred art style? (e.g., anime, watercolor, realistic, cyberpunk)")
    print("   (Press Enter for 'up to you')")
    art_style_input = input("Art style: ").strip()
    story_data["art_style"] = art_style_input if art_style_input else "up to you"
    
    # 4. Number of scenes
    print("\n4. How many scenes? (recommended: 8-12)")
    print("   (Press Enter for 'up to you')")
    num_scenes_input = input("Number of scenes: ").strip()
    if num_scenes_input:
        try:
            story_data["num_scenes"] = int(num_scenes_input)
        except ValueError:
            story_data["num_scenes"] = "up to you"
            print("   Invalid number, using 'up to you'")
    else:
        story_data["num_scenes"] = "up to you"
    
    # 5. Main character
    print("\n5. Main character details:")
    print("   (Press Enter for 'up to you')")
    main_character = {}
    char_name = input("   Character name: ").strip()
    main_character["name"] = char_name if char_name else "up to you"
    
    char_desc = input("   Character description (appearance, personality): ").strip()
    main_character["description"] = char_desc if char_desc else "up to you"
    
    story_data["main_character"] = main_character
    
    # 6. Additional characters (optional)
    print("\n6. Additional characters? (Enter character name or press Enter to skip)")
    additional_chars = []
    while True:
        char_name = input("   Character name (or press Enter to finish): ").strip()
        if not char_name:
            break
        char_desc = input(f"   Description for {char_name}: ").strip()
        if char_desc:
            additional_chars.append({"name": char_name, "description": char_desc})
    
    if additional_chars:
        story_data["additional_characters"] = additional_chars
    
    # 7. Mood
    print("\n7. Overall mood or tone? (e.g., tense, melancholic, mysterious, hopeful)")
    print("   (Press Enter for 'up to you')")
    mood_input = input("Mood: ").strip()
    story_data["mood"] = mood_input if mood_input else "up to you"
    
    print("\n" + "=" * 60)
    print("✅ Story input collected successfully!")
    print("=" * 60)
    
    return story_data


def save_story_json(story_data, filename="user_story_input.json"):
    """Save story data to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(story_data, f, indent=2, ensure_ascii=False)
    print(f"\n📁 Story saved to: {filename}")
    print("\nYou can now use this JSON file to generate images!")
    return filename


def load_story_json(filename="user_story_input.json"):
    """Load story data from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found!")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: {filename} is not valid JSON!")
        return None

