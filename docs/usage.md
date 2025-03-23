# Usage Instructions

This document explains how to use the Audiobook Enhancer scripts to process audiobooks.

## Project Structure

- `input/`: Place your audio files (e.g., `chunk_1_sol_6_7.mp3`) and description (`fanfic_description.txt`) here.
- `output/`: Results are saved here, in subfolders named after the audio file (e.g., `output/chunk_1_sol_6_7/`).
  - `transcript.txt`: The transcription file.
  - `transcript_parts/`: Split transcript parts (created by `analyze.py`).
  - `music_analysis/`: Music analysis results.
  - `sounds_analysis/`: Sounds analysis results.
  - `export_vegas/`: Exported files for Vegas Pro (`music_regions.txt`, `sound_markers.txt`).
- `logs/`: Logs for debugging (`transcribe.log`, `analyze.log`, `export_vegas.log`).
- `prompts/`: Prompts for Gemini API.
  - `analyze/`: Prompts for `analyze.py` (`music.txt`, `sounds.txt`).
  - `export_vegas/`: Prompts for `export_vegas.py` (`music_regions.txt`, `sound_markers.txt`).

## Prerequisites

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Set your Gemini API key in `config/settings.json`.

## Scripts

### 1. Transcribe Audio (`transcribe.py`)

Transcribes an audio file and saves the result with timestamps.

**Usage:**
```
python src/core/transcribe.py <audio_file> [language] [model_size]
```

- `<audio_file>`: Path to the audio file (e.g., `input/chunk_1_sol_6_7.mp3`).
- `[language]`: Language for transcription (`auto`, `en`, `ru`...). Default: `auto`.
- `[model_size]`: Whisper model size (`tiny`, `base`, `small`, `medium`, `large`, `turbo`). Default: `turbo`.

**Example:**
```
python src/core/transcribe.py input/chunk_1_sol_6_7.mp3 ru base
```

**Output:**
- Transcription is saved to `output/chunk_1_sol_6_7/transcript.txt`.
- Logs are saved to `logs/transcribe.log`.

---

### 2. Analyze Transcription (`analyze.py`)

Analyzes the audiobook transcription and description to identify scenes for music and sound effects, splitting the transcription into parts.

**Usage:**
```
python src/core/analyze.py <transcript_file> <description_file> [num_parts]
```

- `<transcript_file>`: Path to the transcription file (e.g., `output/chunk_1_sol_6_7/transcript.txt`).
- `<description_file>`: Path to the description file (e.g., `input/fanfic_description.txt`).
- `[num_parts]`: Number of parts to split the transcription into (optional). Default: `2`.

**Example:**
```
python src/core/analyze.py output/chunk_1_sol_6_7/transcript.txt input/fanfic_description.txt 2
```

**Output:**
- Split transcript parts are saved to `output/chunk_1_sol_6_7/transcript_parts/partX.txt` (e.g., `part1.txt`, `part2.txt`).
- Music analysis results are saved to `output/chunk_1_sol_6_7/music_analysis/partX.txt`.
- Sound analysis results are saved to `output/chunk_1_sol_6_7/sounds_analysis/partX.txt`.
- Logs are saved to `logs/analyze.log`.

**Notes:**
- The script uses prompts from `prompts/analyze/music.txt` and `prompts/analyze/sounds.txt` to guide the Gemini API.
- Old analysis directories are cleared and recreated each time the script runs.

---

### 3. Export to Vegas Pro (`export_vegas.py`)

Exports music regions and sound markers in a format compatible with Vegas Pro.

**Usage:**
```
python src/core/export_vegas.py <chunk_name> <music_files> <sound_files>
```

- `<chunk_name>`: Name of the chunk (e.g., `chunk_1_sol_6_7`).
- `<music_files>`: Comma-separated list of music analysis files (e.g., `"output/chunk_1_sol_6_7/music_analysis/part1.txt,output/chunk_1_sol_6_7/music_analysis/part2.txt"`).
- `<sound_files>`: Comma-separated list of sound analysis files (e.g., `"output/chunk_1_sol_6_7/sounds_analysis/part1.txt,output/chunk_1_sol_6_7/sounds_analysis/part2.txt"`).

**Example:**
```
python src/core/export_vegas.py chunk_1_sol_6_7 "output/chunk_1_sol_6_7/music_analysis/part1.txt,output/chunk_1_sol_6_7/music_analysis/part2.txt" "output/chunk_1_sol_6_7/sounds_analysis/part1.txt,output/chunk_1_sol_6_7/sounds_analysis/part2.txt"
```

**Output:**
- Music regions are saved to `output/chunk_1_sol_6_7/export_vegas/music_regions.txt` in Vegas Pro format (e.g., `Start End Length Name`).
- Sound markers are saved to `output/chunk_1_sol_6_7/export_vegas/sound_markers.txt` in Vegas Pro format (e.g., `Position Name`).
- Logs are saved to `logs/export_vegas.log`.

**Notes:**
- The script converts timestamps to Vegas Pro’s `HH:MM:SS:FF` format (assuming ~30 fps).
- Prompts from `prompts/export_vegas/music_regions.txt` and `prompts/export_vegas/sound_markers.txt` are used for Gemini API requests.