# scripts/export_csv.py
import os
import sys
import re
import config
import utils

def seconds_to_vegas_time(seconds):
    """Преобразует секунды в формат HH:MM:SS:FF для Vegas Pro."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:00"  # Добавляем:00 для кадров

def export_csv(chunk_name, scenes_part1_file, scenes_part2_file, sounds_part1_file, sounds_part2_file):
    # Check if all files exist
    for file in [scenes_part1_file, scenes_part2_file, sounds_part1_file, sounds_part2_file]:
        if not os.path.exists(file):
            print(f"Error: file {file} not found!")
            return

    # Read the scene and sound files
    with open(scenes_part1_file, 'r', encoding='utf-8') as f:
        scenes_part1 = f.read()
    with open(scenes_part2_file, 'r', encoding='utf-8') as f:
        scenes_part2 = f.read()
    with open(sounds_part1_file, 'r', encoding='utf-8') as f:
        sounds_part1 = f.read()
    with open(sounds_part2_file, 'r', encoding='utf-8') as f:
        sounds_part2 = f.read()

    # Prompt for music regions (start, end, length, name in seconds)
    prompt_music = f"""
    Analyze the two scene description files below. Reason about them freely, then output a list of regions for music with start, end, length (in seconds), and name. Format it like this:
    Start,End,Length,Name
    0,335,335,Calm - Exposition
    335,498,163,Tense - System Failure
    Put the list inside triple backticks (```) like this:
    ```
    Start,End,Length,Name
    0,335,335,Calm - Exposition
    ```
    Scene descriptions part 1:
    {scenes_part1}
    Scene descriptions part 2:
    {scenes_part2}
    """

    # Prompt for sound markers (position, name in seconds)
    prompt_sounds = f"""
    Analyze the two sound description files below. Reason about them freely, then output a list of markers for sounds with timestamps in seconds (e.g., 150). Format it like this:
    Position,Name
    150,Metallic Clang - Engine Bang
    180,Rustling Leaves - Suspense
    Put the list inside triple backticks (```) like this:
    ```
    Position,Name
    150,Metallic Clang - Engine Bang
    ```
    Sound descriptions part 1:
    {sounds_part1}
    Sound descriptions part 2:
    {sounds_part2}
    """

    # Make sure output folder exists
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    # Process music regions
    print(f"Creating music regions for {chunk_name}...")
    response_music = utils.send_gemini_request(prompt_music)
    if response_music:
        match = re.search(r'```(.*?)```', response_music, re.DOTALL)
        if match:
            region_text = match.group(1).strip()
            lines = region_text.splitlines()
            header = lines[0]  # "Start,End,Length,Name"
            output_lines = [header.replace(',', '\t')]
            for line in lines[1:]:
                if ',' in line:
                    start, end, length, name = line.rsplit(',', 3)  # rsplit для корректного разделения, если в имени есть запятые
                    start_vegas = seconds_to_vegas_time(int(start))
                    end_vegas = seconds_to_vegas_time(int(end))
                    length_vegas = seconds_to_vegas_time(int(length))
                    output_lines.append(f"{start_vegas}\t{end_vegas}\t{length_vegas}\t{name}")
            music_file = os.path.join(config.OUTPUT_DIR, f'{chunk_name}_markers_music.txt')
            with open(music_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            print(f"Music regions saved to {music_file}")
        else:
            print("No region list found in music response.")
    else:
        print("Failed to get music regions response.")

    # Process sound markers
    print(f"Creating sound markers for {chunk_name}...")
    response_sounds = utils.send_gemini_request(prompt_sounds)
    if response_sounds:
        match = re.search(r'```(.*?)```', response_sounds, re.DOTALL)
        if match:
            marker_text = match.group(1).strip()
            lines = marker_text.splitlines()
            header = lines[0]  # "Position,Name"
            output_lines = [header.replace(',', '\t')]
            for line in lines[1:]:
                if ',' in line:
                    time, name = line.split(',', 1)
                    time_vegas = seconds_to_vegas_time(int(time))
                    output_lines.append(f"{time_vegas}\t{name}")
            sounds_file = os.path.join(config.OUTPUT_DIR, f'{chunk_name}_markers_sounds.txt')
            with open(sounds_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            print(f"Sound markers saved to {sounds_file}")
        else:
            print("No marker list found in sounds response.")
    else:
        print("Failed to get sound markers response.")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python export_csv.py <chunk_name> <scenes_part1_file> <scenes_part2_file> <sounds_part1_file> <sounds_part2_file>")
        sys.exit(1)
    chunk_name = sys.argv[1]
    scenes_part1_file = sys.argv[2]
    scenes_part2_file = sys.argv[3]
    sounds_part1_file = sys.argv[4]
    sounds_part2_file = sys.argv[5]
    export_csv(chunk_name, scenes_part1_file, scenes_part2_file, sounds_part1_file, sounds_part2_file)