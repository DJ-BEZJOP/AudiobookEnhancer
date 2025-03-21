# scripts/analyze_audio.py
import os
import sys
import config
import utils

def analyze_audio(transcript_file, description_file):
    # Check if files exist
    for file in [transcript_file, description_file]:
        if not os.path.exists(file):
            print(f"Error: file {file} not found!")
            return

    # Extract chunk number from transcript filename (e.g., "chunk_1_transcript.txt" -> "chunk_1")
    chunk_name = os.path.splitext(os.path.basename(transcript_file))[0].replace("_transcript", "")

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

    # Create prompts for scenes
    prompt_scenes_first = f"""
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
    prompt_scenes_second = f"""
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

    # Create prompts for sounds
    prompt_sounds_first = f"""
    Analyze the provided audiobook transcription (first half, from {start_first} to {end_first} seconds) and fanfic description. Identify key moments where sound effects can enhance the atmosphere. For each moment:
    1. Reason about the content in detail (free-form analysis).
    2. Describe the sound suggestion using this template:
       Sound [timestamp]:
       - Location: [e.g., forest]
       - Context: [e.g., character hears a rustle]
       - Event: [e.g., twig snapping]
       - Mood: [e.g., suspenseful]
       - Suggested Sound: [e.g., rustling leaves, loud crash]
       - Duration: [e.g., 2-5 seconds]
       - Description: [short explanation why this sound fits]
    Fanfic Description:
    {description_content}
    Transcription (first half):
    {'\n'.join(first_half)}
    Output your reasoning and sound suggestions for this part.
    """
    prompt_sounds_second = f"""
    Analyze the provided audiobook transcription (second half, from {start_second} to {end_second} seconds) and fanfic description. Identify key moments where sound effects can enhance the atmosphere. For each moment:
    1. Reason about the content in detail (free-form analysis).
    2. Describe the sound suggestion using this template:
       Sound [timestamp]:
       - Location: [e.g., forest]
       - Context: [e.g., character hears a rustle]
       - Event: [e.g., twig snapping]
       - Mood: [e.g., suspenseful]
       - Suggested Sound: [e.g., rustling leaves, loud crash]
       - Duration: [e.g., 2-5 seconds]
       - Description: [short explanation why this sound fits]
    Fanfic Description:
    {description_content}
    Transcription (second half):
    {'\n'.join(second_half)}
    Output your reasoning and sound suggestions for this part.
    """

    # Make sure output folder exists
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    # Send requests to Gemini for scenes
    print(f"Processing scenes for {chunk_name} (first half)...")
    response_scenes_first = utils.send_gemini_request(prompt_scenes_first)
    if response_scenes_first:
        scenes_file_first = os.path.join(config.OUTPUT_DIR, f'{chunk_name}_scenes_part1.txt')
        with open(scenes_file_first, 'w', encoding='utf-8') as f:
            f.write(response_scenes_first)
        print(f"Scenes (first half) saved to {scenes_file_first}")
    else:
        print("Failed to process scenes (first half).")

    print(f"Processing scenes for {chunk_name} (second half)...")
    response_scenes_second = utils.send_gemini_request(prompt_scenes_second)
    if response_scenes_second:
        scenes_file_second = os.path.join(config.OUTPUT_DIR, f'{chunk_name}_scenes_part2.txt')
        with open(scenes_file_second, 'w', encoding='utf-8') as f:
            f.write(response_scenes_second)
        print(f"Scenes (second half) saved to {scenes_file_second}")
    else:
        print("Failed to process scenes (second half).")

    # Send requests to Gemini for sounds
    print(f"Processing sounds for {chunk_name} (first half)...")
    response_sounds_first = utils.send_gemini_request(prompt_sounds_first)
    if response_sounds_first:
        sounds_file_first = os.path.join(config.OUTPUT_DIR, f'{chunk_name}_sounds_part1.txt')
        with open(sounds_file_first, 'w', encoding='utf-8') as f:
            f.write(response_sounds_first)
        print(f"Sounds (first half) saved to {sounds_file_first}")
    else:
        print("Failed to process sounds (first half).")

    print(f"Processing sounds for {chunk_name} (second half)...")
    response_sounds_second = utils.send_gemini_request(prompt_sounds_second)
    if response_sounds_second:
        sounds_file_second = os.path.join(config.OUTPUT_DIR, f'{chunk_name}_sounds_part2.txt')
        with open(sounds_file_second, 'w', encoding='utf-8') as f:
            f.write(response_sounds_second)
        print(f"Sounds (second half) saved to {sounds_file_second}")
    else:
        print("Failed to process sounds (second half).")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze_audio.py <transcript_file> <description_file>")
        sys.exit(1)
    transcript_file = sys.argv[1]
    description_file = sys.argv[2]
    analyze_audio(transcript_file, description_file)