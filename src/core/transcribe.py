# src/core/transcribe.py
import os
import sys
import logging
import whisper
import time

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import config

# Create a specific logger for this script
logger = logging.getLogger('transcribe')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logs/transcribe.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.handlers = []  # Clear any existing handlers
logger.addHandler(handler)


def transcribe_with_timestamps(audio_file, language="auto", model_size="turbo"):
    """
    Transcribes an audio file using Whisper with start timestamps.

    Args:
        audio_file (str): Path to the audio file.
        language (str): Language for transcription ("auto", "en", "ru").
        model_size (str): Whisper model size ("tiny", "base", "small", "medium", "large", "large-v3", "turbo").
    Returns:
        str: Path to the transcription file, or None if failed.
    """
    # Check if the audio file exists
    if not os.path.exists(audio_file):
        logger.error(f"Audio file {audio_file} not found!")
        return None

    # Determine the chunk name and output directory
    chunk_name = os.path.splitext(os.path.basename(audio_file))[0]
    output_dir = os.path.join(config.OUTPUT_DIR, chunk_name)
    output_file = os.path.join(output_dir, 'transcript.txt')

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created directory: {output_dir}")

    # Load the Whisper model
    try:
        logger.info(f"Loading Whisper model '{model_size}' for transcription of {audio_file}...")
        model = whisper.load_model(model_size)
    except Exception as e:
        logger.error(f"Error loading Whisper model: {e}")
        return None

    # Perform transcription with timing
    start_time = time.time()
    try:
        logger.info(f"Starting transcription of {audio_file} with language={language}...")
        language_code = None if language == "auto" else language
        result = model.transcribe(audio_file, language=language_code, verbose=False)
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return None

    # Save the result with start timestamps in the format: start	text
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            # Write header
            f.write("start\ttext\n")
            # Write segments
            for segment in result["segments"]:
                start_ms = int(segment["start"] * 1000)  # Convert seconds to milliseconds
                text = segment["text"].strip()
                f.write(f"{start_ms}\t{text}\n")
        end_time = time.time()
        duration = int(end_time - start_time)
        logger.info(f"Transcription completed! Result saved in {output_file}")
        logger.info(f"Transcription took {duration} seconds")
        return output_file
    except Exception as e:
        logger.error(f"Error saving transcription: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file> [language] [model_size]")
        sys.exit(1)
    audio_file = sys.argv[1]  # e.g., "input/chunk_1_sol_6_7.mp3"
    language = sys.argv[2] if len(sys.argv) > 2 else "auto"
    model_size = sys.argv[3] if len(sys.argv) > 3 else "base"
    output_file = transcribe_with_timestamps(audio_file, language, model_size)
    if output_file:
        print(f"Transcription saved to {output_file}")
    else:
        print("Transcription failed. Check logs/transcribe.log for details.")