# scripts/transcribe_audio.py
import whisper
import sys
import os

def transcribe_with_timestamps(audio_file, output_file):
    # Check if the audio file exists
    if not os.path.exists(audio_file):
        print(f"Error: file {audio_file} not found!")
        return

    # Create the output directory if it doesn’t exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directory created: {output_dir}")

    # Load the Whisper model
    try:
        print(f"Loading Whisper model for transcription {audio_file}...")
        model = whisper.load_model("base")  # "base" is small and fast
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        return

    # Perform transcription
    try:
        print(f"Starting transcription of {audio_file}...")
        result = model.transcribe(audio_file, language="ru", verbose=True)
    except Exception as e:
        print(f"Error during transcription: {e}")
        return

    # Save the result with timestamps
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for segment in result["segments"]:
                start = int(segment["start"])  # Start time in seconds
                text = segment["text"]  # The spoken text
                f.write(f"[{start}]: {text}\n")
        print(f"Transcription completed! Result saved in {output_file}")
    except Exception as e:
        print(f"Error saving transcription: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python transcribe_audio.py <audio_file> <output_file>")
        sys.exit(1)
    audio_file = sys.argv[1]  # e.g., "../input/chunk_1_sol_6_7.mp3"
    output_file = sys.argv[2]  # e.g., "../input/chunk_1_transcript.txt"
    transcribe_with_timestamps(audio_file, output_file)