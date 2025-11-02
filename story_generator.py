"""
Story Generator Module
Handles Gemini API integration for generating stories from JSON input
"""

import os
from story_collector import load_story_json

# Default API key (can be overridden by environment variable)
GEMINI_API_KEY = "AIzaSyDm8xnOTpl1tik0ScuS9Z9H5q6dn9oETFw"


def format_json_for_gemini(story_data):
    """
    Format the story JSON data into a prompt for Gemini, 
    specifically requesting the output in a structured JSON format 
    suitable for a visual novel script.
    """
    
    # 1. Start with the instruction for the output format
    prompt = "Generate a complete visual novel story that strictly adheres to the JSON format specified below. "
    prompt += "The entire output MUST be a single, valid JSON object.\n\n"
    
    # 2. Define the desired JSON structure (or provide an example)
    prompt += "### REQUIRED JSON FORMAT ###\n"
    prompt += "{\n"
    prompt += '  "style_bible": "...",\n'
    prompt += '  "scenes": [\n'
    prompt += '    {\n'
    prompt += '      "id": "s###",\n'
    prompt += '      "bg": {"location": "...", "time": "..."},\n'
    prompt += '      "characters": [\n'
    prompt += '        {"name":"...", "look_key":"...", "pose":"..."}\n'
    prompt += '      ],\n'
    prompt += '      "camera": "...",\n'
    prompt += '      "mood": "...",\n'
    prompt += '      "dialogue": ["..."]\n'
    prompt += '    }\n'
    prompt += '    // ... more scenes\n'
    prompt += '  ]\n'
    prompt += '}\n\n'
    
    # 3. Add the story specifications (similar to your original function)
    prompt += "### STORY SPECIFICATIONS ###\n"

    # Set the overall 'style_bible' based on 'art_style' and a default VN framing
    art_style = story_data.get("art_style")
    if art_style and art_style != "up to you":
        prompt += f"**Overall Visual Style (`style_bible`):** Use the art style '{art_style}' combined with a 'VN framing'.\n"
    else:
        prompt += "**Overall Visual Style (`style_bible`):** Choose an appropriate anime-style for a Visual Novel and include 'VN framing'.\n"


    # Add narrative if provided
    if story_data.get("narrative") and story_data["narrative"] != "up to you":
        prompt += f"\n**Story Idea/Narrative:** {story_data['narrative']}\n"
    
    # Add genre
    if story_data.get("genre") and story_data["genre"] != "up to you":
        prompt += f"**Genre:** {story_data['genre']}\n"
    
    # Add number of scenes (guide for scene count)
    if story_data.get("num_scenes") and story_data["num_scenes"] != "up to you":
        prompt += f"**Target Number of Scenes:** Approximately {story_data['num_scenes']} scenes.\n"
    
    # Add main character
    if story_data.get("main_character"):
        char = story_data["main_character"]
        prompt += "\n**Main Character:**\n"
        if char.get("name") and char["name"] != "up to you":
            prompt += f"- Name: {char['name']}\n"
        if char.get("description") and char["description"] != "up to you":
            prompt += f"- Description/Look Key: {char['description']} (Use this to create the `look_key` for this character)\n"
    
    # Add additional characters
    if story_data.get("additional_characters"):
        prompt += "\n**Additional Characters:**\n"
        for char in story_data["additional_characters"]:
            name = char.get('name', 'Character')
            desc = char.get('description', '')
            prompt += f"- Name: {name}, Description/Look Key: {desc}\n"
    
    # Add mood
    if story_data.get("mood") and story_data["mood"] != "up to you":
        prompt += f"\n**Primary Mood/Tone:** {story_data['mood']}\n"
    else:
        prompt += "\n**Primary Mood/Tone:** Maintain an engaging and consistent mood throughout the narrative.\n"
    
    # 4. Final instructions for content details
    prompt += "\n### CONTENT GUIDELINES ###\n"
    prompt += "* **`look_key`**: Use brief, descriptive tags (e.g., 'short silver hair, yellow raincoat, blue scarf') that remain consistent for each character throughout the story.\n"
    prompt += "* **`bg`**: Provide clear, specific `location` and `time` (e.g., 'neon street', 'rain night').\n"
    prompt += "* **`camera`**: Use standard shots (e.g., 'close up', 'medium shot', 'long shot', 'full body').\n"
    prompt += "* **`dialogue`**: Ensure the story has compelling character development and plot progression, with dialogue broken down into sequential lines in the array with having each character name before each row.\n"
    prompt += "* **Scene Flow**: Ensure the scenes transition logically and tell a complete, engaging story."
    prompt += (
    "\n\n### OUTPUT REQUIREMENTS ###\n"
    "* Output ONLY the JSON object itself.\n"
    "* DO NOT wrap it in code blocks, backticks, or Markdown fences.\n"
    "* Begin directly with '{' and end with '}'."
    )
    prompt += (
        "\n### SIMPLICITY & ACCESSIBILITY RULES ###\n"
        "* Keep the story easy to understand for all ages (teen to adult).\n"
        "* Avoid overly complex vocabulary, philosophical themes, or abstract narration.\n"
        "* Keep sentences short, natural, and emotionally clear.\n"
        "* Focus on clarity, emotion, and readable pacing rather than heavy descriptions.\n"
    )
    
    return prompt

def generate_story_with_gemini(story_data, api_key=None):
    """
    Send story data to Gemini API and generate a complete story.
    Returns: (generated_story, error_message)
    """
    
    import google.generativeai as genai 
    # Get API key from parameter, environment variable, or use default
    api_key = GEMINI_API_KEY
    
    if not api_key:
        return None, "Gemini API key not found."
    
    try:
        # Initialize client with API key
        #client = genai.Client(api_key=api_key)

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Format prompt
        prompt = format_json_for_gemini(story_data)

        print(f"\n🤖 Generating story with Gemini...")
        print("This may take a moment...\n")
        
        response = model.generate_content(prompt)    
        
        if not response:
            return None, "Could not generate content with any Gemini model. Please check your API key."
        
        generated_story = response.text
        
        if generated_story:
            return generated_story, None
        else:
            return None, "Gemini returned an empty response."
            
    except Exception as e:
        return None, f"Gemini API error: {str(e)}"


def save_generated_story(story_text, filename="generated_story.txt"):
    """Save generated story to text file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(story_text)
    print(f"📄 Generated story saved to: {filename}")
    return filename


def generate_story_from_json(json_filename="user_story_input.json", api_key=None):
    """
    Main function: Load JSON, generate story with Gemini, and save it.
    """
    print("=" * 60)
    print("Story Generation with Gemini")
    print("=" * 60)
    
    # Load JSON file
    print(f"\n📂 Loading {json_filename}...")
    story_data = load_story_json(json_filename)
    
    if not story_data:
        return False
    
    print("✅ JSON file loaded successfully!")
    
    # Get API key if not provided
    if not api_key:
        api_key = GEMINI_API_KEY
       
    # Generate story
    generated_story, error = generate_story_with_gemini(story_data, api_key)
    
    if generated_story:
        # Save story
        save_generated_story(generated_story)
        
        print("\n" + "=" * 60)
        print("✅ Story Generated Successfully!")
        print("=" * 60)
        print(f"\nFull story saved to: generated_story.txt")
        return True
    else:
        print(f"\n❌ Failed to generate story: {error}")
        return False

