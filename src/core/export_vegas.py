# src/core/export_vegas.py
import os
import sys
import re
import logging
import time

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import config
from src.utils import api

# Set up logging
logger = logging.getLogger('export_vegas')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/export_vegas.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.handlers = [file_handler, stream_handler]


def milliseconds_to_vegas_time(milliseconds):
    """Преобразует миллисекунды в формат HH:MM:SS:FF для Vegas Pro."""
    total_seconds = milliseconds // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    frames = (milliseconds % 1000) // 33  # Примерно 30 fps
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"


def export_vegas(chunk_name, music_files, sound_files):
    """Экспортирует регионы музыки и маркеры звуков для Vegas Pro."""
    logger.info(f"Starting export for chunk: {chunk_name}")
    print(f"Starting export for chunk: {chunk_name}")

    # Split file lists
    music_file_list = music_files.split(',')
    sound_file_list = sound_files.split(',')

    # Filter existing files and log missing ones
    music_files_existing = []
    for file in music_file_list:
        if os.path.exists(file):
            music_files_existing.append(file)
        else:
            logger.warning(f"Music file not found, skipping: {file}")
            print(f"Warning: Music file not found, skipping: {file}")

    sound_files_existing = []
    for file in sound_file_list:
        if os.path.exists(file):
            sound_files_existing.append(file)
        else:
            logger.warning(f"Sound file not found, skipping: {file}")
            print(f"Warning: Sound file not found, skipping: {file}")

    # Check if we have any files to process
    if not music_files_existing and not sound_files_existing:
        logger.error("No valid music or sound files found to process")
        print("Error: No valid music or sound files found to process")
        return

    # Read music and sound files
    music_content = []
    for i, file in enumerate(music_files_existing, 1):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                music_content.append(f"Music analysis part {i}:\n{content}")
                logger.info(f"Loaded music file: {file}")
        except Exception as e:
            logger.error(f"Failed to read music file {file}: {e}")
            print(f"Error: Failed to read music file {file}: {e}")

    sound_content = []
    for i, file in enumerate(sound_files_existing, 1):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                sound_content.append(f"Sound analysis part {i}:\n{content}")
                logger.info(f"Loaded sound file: {file}")
        except Exception as e:
            logger.error(f"Failed to read sound file {file}: {e}")
            print(f"Error: Failed to read sound file {file}: {e}")

    # Load prompts
    try:
        with open('prompts/export_vegas/music_regions.txt', 'r', encoding='utf-8') as f:
            music_prompt_template = f.read()
        with open('prompts/export_vegas/sound_markers.txt', 'r', encoding='utf-8') as f:
            sounds_prompt_template = f.read()
        logger.info("Prompts loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"Prompt file not found: {e}")
        print(f"Error: Prompt file not found: {e}")
        return

    # Prepare prompts only if we have content
    music_prompt = music_prompt_template.format(music_parts='\n\n'.join(music_content)) if music_content else ""
    sounds_prompt = sounds_prompt_template.format(sound_parts='\n\n'.join(sound_content)) if sound_content else ""

    # Create output directory
    output_dir = os.path.join(config.OUTPUT_DIR, chunk_name, 'export_vegas')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    # Process music regions if there is content
    if music_content:
        start_time = time.time()
        logger.info("Sending music prompt to Gemini...")
        print("Sending music prompt to Gemini...")
        response_music = api.send_gemini_request(music_prompt)
        if response_music:
            logger.info("Received music response from Gemini")
            match = re.search(r'```(.*?)```', response_music, re.DOTALL)
            if match:
                region_text = match.group(1).strip()
                lines = region_text.splitlines()
                header = lines[0]  # "Start,End,Length,Name"
                output_lines = [header.replace(',', '\t')]
                for line in lines[1:]:
                    if ',' in line:
                        start, end, length, name = line.rsplit(',', 3)
                        start_ms = int(start)
                        end_ms = int(end)
                        length_ms = int(length)
                        start_vegas = milliseconds_to_vegas_time(start_ms)
                        end_vegas = milliseconds_to_vegas_time(end_ms)
                        length_vegas = milliseconds_to_vegas_time(length_ms)
                        output_lines.append(f"{start_vegas}\t{end_vegas}\t{length_vegas}\t{name}")
                music_file = os.path.join(output_dir, 'music_regions.txt')
                with open(music_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(output_lines))
                logger.info(f"Music regions saved to {music_file}")
                print(f"Music regions saved to {music_file}")
            else:
                logger.error("No valid region list in music response")
                print("Error: No valid region list in music response")
        else:
            logger.error("Failed to get music response from Gemini")
            print("Error: Failed to get music response from Gemini")

    # Process sound markers if there is content
    if sound_content:
        logger.info("Sending sound prompt to Gemini...")
        print("Sending sound prompt to Gemini...")
        response_sounds = api.send_gemini_request(sounds_prompt)
        if response_sounds:
            logger.info("Received sound response from Gemini")
            match = re.search(r'```(.*?)```', response_sounds, re.DOTALL)
            if match:
                marker_text = match.group(1).strip()
                lines = marker_text.splitlines()
                header = lines[0]  # "Position,Name"
                output_lines = [header.replace(',', '\t')]
                for line in lines[1:]:
                    if ',' in line:
                        position, name = line.split(',', 1)
                        time_ms = int(position)
                        time_vegas = milliseconds_to_vegas_time(time_ms)
                        output_lines.append(f"{time_vegas}\t{name}")
                sounds_file = os.path.join(output_dir, 'sound_markers.txt')
                with open(sounds_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(output_lines))
                logger.info(f"Sound markers saved to {sounds_file}")
                print(f"Sound markers saved to {sounds_file}")
            else:
                logger.error("No valid marker list in sounds response")
                print("Error: No valid marker list in sounds response")
        else:
            logger.error("Failed to get sound response from Gemini")
            print("Error: Failed to get sound response from Gemini")

    end_time = time.time()
    duration = int(end_time - start_time)
    logger.info(f"Export completed for {chunk_name}. Took {duration} seconds.")
    print(f"Export completed for {chunk_name}. Took {duration} seconds.")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python src/core/export_vegas.py <chunk_name> <music_files> <sound_files>")
        print(
            "Example: python src/core/export_vegas.py chunk_1_sol_6_7 \"output/chunk_1_sol_6_7/music_analysis/part1.txt,output/chunk_1_sol_6_7/music_analysis/part2.txt\" \"output/chunk_1_sol_6_7/sounds_analysis/part1.txt,output/chunk_1_sol_6_7/sounds_analysis/part2.txt\"")
        sys.exit(1)
    chunk_name = sys.argv[1]
    music_files = sys.argv[2]
    sound_files = sys.argv[3]
    export_vegas(chunk_name, music_files, sound_files)