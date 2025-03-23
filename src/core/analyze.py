# src/core/analyze.py
import os
import sys
import logging
import time
import shutil

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import config
from src.utils import api

# Create a specific logger for this script
logger = logging.getLogger('analyze')
logger.setLevel(logging.INFO)

# File handler for logging to file
file_handler = logging.FileHandler('logs/analyze.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Stream handler for logging to terminal
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Clear existing handlers and add both
logger.handlers = []
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def analyze_audio(transcript_file, description_file, num_parts=2):
    """
    Analyzes the audiobook transcription and description to identify scenes and sounds.

    Args:
        transcript_file (str): Path to the transcription file (e.g., output/chunk_1_sol_6_7/transcript.txt).
        description_file (str): Path to the description file (e.g., input/fanfic_description.txt).
        num_parts (int): Number of parts to split the transcription into (default: 2).
    """
    # Check if files exist
    for file in [transcript_file, description_file]:
        if not os.path.exists(file):
            logger.error(f"File {file} not found!")
            return

    # Extract chunk name from transcript file (e.g., "output/chunk_1_sol_6_7/transcript.txt" -> "chunk_1_sol_6_7")
    chunk_name = os.path.basename(os.path.dirname(transcript_file))

    # Read the description and transcription
    with open(description_file, 'r', encoding='utf-8') as f:
        description_content = f.read()
    with open(transcript_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Parse the transcription (format: start    text)
    segments = []
    for line in lines[1:]:  # Skip header (start    text)
        if not line.strip():
            continue
        parts = line.strip().split('\t')
        if len(parts) < 2:
            continue
        try:
            start_ms = int(parts[0])
            text = parts[1]
            segments.append({'start': start_ms, 'text': text})
        except ValueError:
            logger.warning(f"Skipping invalid line in transcript: {line.strip()}")
            continue

    if not segments:
        logger.error("No valid segments found in transcript!")
        return

    # Split into parts
    total_segments = len(segments)
    segments_per_part = (total_segments + num_parts - 1) // num_parts  # Round up division
    parts = [segments[i:i + segments_per_part] for i in range(0, total_segments, segments_per_part)]

    # Create output directories and clean old files
    output_base_dir = os.path.dirname(transcript_file)
    transcript_parts_dir = os.path.join(output_base_dir, 'transcript_parts')
    music_analysis_dir = os.path.join(output_base_dir, 'music_analysis')
    sounds_analysis_dir = os.path.join(output_base_dir, 'sounds_analysis')

    for directory in [transcript_parts_dir, music_analysis_dir, sounds_analysis_dir]:
        # Remove the directory and its contents if it exists
        if os.path.exists(directory):
            shutil.rmtree(directory)
            logger.info(f"Cleared old directory: {directory}")
        # Create the directory
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

    # Save each part of the transcript
    for part_idx, part in enumerate(parts, 1):
        part_file = os.path.join(transcript_parts_dir, f'part{part_idx}.txt')
        with open(part_file, 'w', encoding='utf-8') as f:
            f.write("start\ttext\n")
            for segment in part:
                f.write(f"{segment['start']}\t{segment['text']}\n")
        logger.info(f"Saved transcript part {part_idx} to {part_file}")

    # Load prompts
    with open('prompts/analyze/music.txt', 'r', encoding='utf-8') as f:
        music_prompt_template = f.read()
    with open('prompts/analyze/sounds.txt', 'r', encoding='utf-8') as f:
        sounds_prompt_template = f.read()

    # Analyze each part
    start_time = time.time()
    for part_idx, part in enumerate(parts, 1):
        if not part:
            logger.warning(f"Part {part_idx} is empty, skipping.")
            continue

        start_ms = part[0]['start']
        end_ms = part[-1]['start']
        part_text = '\n'.join([f"{seg['start']}\t{seg['text']}" for seg in part])

        # Calculate total duration in seconds
        total_duration_seconds = (end_ms - start_ms) / 1000

        # Create prompts for music (scenes)
        music_prompt = music_prompt_template.format(
            part_idx=part_idx,
            start_ms=start_ms,
            end_ms=end_ms,
            total_duration_seconds=total_duration_seconds,  # Pass the calculated duration
            description_content=description_content,
            part_text=part_text
        )

        # Create prompts for sounds
        sounds_prompt = sounds_prompt_template.format(
            part_idx=part_idx,
            start_ms=start_ms,
            end_ms=end_ms,
            description_content=description_content,
            part_text=part_text
        )

        # Send requests to Gemini for music (scenes)
        logger.info(f"Processing music analysis for {chunk_name} (part {part_idx})...")
        response_music = api.send_gemini_request(music_prompt)
        if response_music:
            music_file = os.path.join(music_analysis_dir, f'part{part_idx}.txt')
            with open(music_file, 'w', encoding='utf-8') as f:
                f.write(response_music)
            logger.info(f"Music analysis (part {part_idx}) saved to {music_file}")
        else:
            logger.error(f"Failed to process music analysis (part {part_idx}).")

        # Send requests to Gemini for sounds
        logger.info(f"Processing sounds analysis for {chunk_name} (part {part_idx})...")
        response_sounds = api.send_gemini_request(sounds_prompt)
        if response_sounds:
            sounds_file = os.path.join(sounds_analysis_dir, f'part{part_idx}.txt')
            with open(sounds_file, 'w', encoding='utf-8') as f:
                f.write(response_sounds)
            logger.info(f"Sounds analysis (part {part_idx}) saved to {sounds_file}")
        else:
            logger.error(f"Failed to process sounds analysis (part {part_idx}).")

    end_time = time.time()
    duration = int(end_time - start_time)
    logger.info(f"Analysis completed for {chunk_name}. Took {duration} seconds.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze.py <transcript_file> <description_file> [num_parts]")
        sys.exit(1)
    transcript_file = sys.argv[1]  # e.g., "output/chunk_1_sol_6_7/transcript.txt"
    description_file = sys.argv[2]  # e.g., "input/fanfic_description.txt"
    num_parts = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    analyze_audio(transcript_file, description_file, num_parts)