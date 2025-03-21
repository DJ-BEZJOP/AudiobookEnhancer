# scripts/analyze_scenes.py
import os
import sys
import config
import utils

def analyze_scenes(transcript_file, description_file):
    # Check if files exist
    for file in [transcript_file, description_file]:
        if not os.path.exists(file):
            print(f"Error: file {file} not found!")
            return

    # Read the description and transcription
    with open(description_file, 'r', encoding='utf-8') as f:
        description_content = f.read()
    with open(transcript_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Split into two parts
    total_lines = len(lines)
    half = (total_lines + 1) // 2  # Rounds up if odd
    first_half = lines[:half]
    second_half = lines[half:]

    # Get timestamps for each part
    def get_timestamp(line):
        try:
            return int(line.split(']:')[0][1:])
        except:
            return None
    start_first = get_timestamp(first_half[0])
    end_first = get_timestamp(first_half[-1])
    start_second = get_timestamp(second_half[0])
    end_second = get_timestamp(second_half[-1])
    if None in [start_first, end_first, start_second, end_second]:
        print("Error: Couldn’t read timestamps.")
        return

    # Create prompts for Gemini
    prompt_first = f"""
    Analyze the provided audiobook transcription (first half, from {start_first} to {end_first} seconds) and fanfic description. Break the text into logical scenes (100-600 seconds each). For each scene:
    1. Reason about the content in detail (free-form analysis).
    2. Describe the scene using this template:
       Scene [start-end]:
       - Location: [e.g., spaceship]
       - Characters: [e.g., Twilight Sparkle]
       - Events: [e.g., engine failure]
       - Mood: [e.g., tense]
       - Atmosphere: [e.g., chaotic]
       - Scene Dynamics: [e.g., fast-paced]
       - Description: [short summary]
       - Music Recommendation: [e.g., Yes, dramatic music; No, too short]
    Fanfic Description:
    {description_content}
    Transcription (first half):
    {'\n'.join(first_half)}
    Output your reasoning and scene descriptions for this part.
    """
    prompt_second = f"""
    Analyze the provided audiobook transcription (second half, from {start_second} to {end_second} seconds) and fanfic description. Break the text into logical scenes (100-600 seconds each). For each scene:
    1. Reason about the content in detail (free-form analysis).
    2. Describe the scene using this template:
       Scene [start-end]:
       - Location: [e.g., spaceship]
       - Characters: [e.g., Twilight Sparkle]
       - Events: [e.g., engine failure]
       - Mood: [e.g., tense]
       - Atmosphere: [e.g., chaotic]
       - Scene Dynamics: [e.g., fast-paced]
       - Description: [short summary]
       - Music Recommendation: [e.g., Yes, dramatic music; No, too short]
    Fanfic Description:
    {description_content}
    Transcription (second half):
    {'\n'.join(second_half)}
    Output your reasoning and scene descriptions for this part.
    """

    # Make sure output folder exists
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    # Send requests to Gemini
    print("Processing first half...")
    response_first = utils.send_gemini_request(prompt_first)
    if response_first:
        with open(os.path.join(config.OUTPUT_DIR, 'scenes_part1.txt'), 'w', encoding='utf-8') as f:
            f.write(response_first)
        print("First half saved to output/scenes_part1.txt")
    else:
        print("Failed to process first half.")

    print("Processing second half...")
    response_second = utils.send_gemini_request(prompt_second)
    if response_second:
        with open(os.path.join(config.OUTPUT_DIR, 'scenes_part2.txt'), 'w', encoding='utf-8') as f:
            f.write(response_second)
        print("Second half saved to output/scenes_part2.txt")
    else:
        print("Failed to process second half.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze_scenes.py <transcript_file> <description_file>")
        sys.exit(1)
    transcript_file = sys.argv[1]
    description_file = sys.argv[2]
    analyze_scenes(transcript_file, description_file)