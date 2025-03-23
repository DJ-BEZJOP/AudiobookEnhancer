# AudiobookEnhancer

AudiobookEnhancer is a Python-based tool designed to enhance audiobook production by automatically analyzing transcription texts (e.g., fanfiction) and generating recommendations for background music and sound effects. It leverages the Gemini API to process the text and exports the results into files compatible with Vegas Pro, streamlining the editing process for audiobook creators.

## Features
- **Scene Analysis**: Breaks down audiobook transcriptions into logical scenes based on narrative flow.
- **Music Recommendations**: Suggests music styles, volumes, tempos, and durations for each scene, with priority levels (High, Medium, Low).
- **Sound Effects**: Proposes sound effects for key moments, including categories and descriptions.
- **Vegas Pro Export**: Generates region and marker files (`music_regions.txt` and `sound_markers.txt`) for seamless integration into Vegas Pro timelines.

## Prerequisites
Before using AudiobookEnhancer, ensure you have the following:
- **Python**: Version 3.8 or higher.
- **Dependencies**: Listed in `requirements.txt`.
- **Gemini API Key**: Required for text analysis (see [Configuration](#configuration)).
- **Vegas Pro**: For importing the exported region and marker files (tested with Vegas Pro 18+).
- **Text Files**: A fanfiction description and transcription files to analyze.

## Installation
Follow these steps to set up the project on your machine:

1. **Clone the Repository**:


2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv .venv
   # Linux/Mac:
   source .venv/bin/activate
   # Windows:
   .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Project**:
   - Copy the example configuration file:
     ```bash
     cp config/settings.example.json config/settings.json
     ```
   - Edit `config/settings.json` to include your Gemini API key and output directory:
     ```json
     {
       "GEMINI_API_KEY": "your-gemini-api-key-here",
       "OUTPUT_DIR": "output"
     }
     ```

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

## Project Structure
```
AudiobookEnhancer/
├── input/                          # Input files
│   ├── chunk_1_sol_6_7.mp3         # Audio file
│   └── fanfic_description.txt      # Description of the fanfic
├── output/                         # Output files
│   ├── chunk_1_sol_6_7/            # Folder for each chunk (named after the mp3 file)
│   │   ├── transcript.txt          # Transcription (created by transcribe.py)
│   │   ├── transcript_parts/       # Split transcript parts (created by analyze.py)
│   │   │   ├── part1.txt
│   │   │   └── part2.txt
│   │   ├── music_analysis/         # Music analysis (created by analyze.py)
│   │   │   ├── part1.txt
│   │   │   └── part2.txt
│   │   ├── sounds_analysis/        # Sounds analysis (created by analyze.py)
│   │   │   ├── part1.txt
│   │   │   └── part2.txt
│   │   ├── export_vegas/           # Export files for Vegas (created by export_vegas.py)
│   │   │   ├── music_regions.txt   # Music regions for Vegas
│   │   │   └── sound_markers.txt   # Sound markers for Vegas
├── src/                            # Source code
│   ├── core/                       # Core scripts
│   │   ├── transcribe.py           # To be updated
│   │   ├── analyze.py              # To be updated
│   │   └── export_vegas.py         # To be updated
│   ├── utils/                      # Utilities
│   │   └── api.py                  # To be updated
│   ├── gui/                        # GUI (to be added later)
│   │   └── app.py
├── config/                         # Configuration files
│   ├── config.py                   # To be updated
│   └── settings.json               # To be created
├── prompts/                        # Prompts for Gemini
│   ├── analyze/                    # Prompts for analyze.py
│   │   ├── music.txt
│   │   └── sounds.txt
│   ├── export_vegas/               # Prompts for export_vegas.py
│   │   ├── music_regions.txt
│   │   └── sound_markers.txt
├── docs/                           # Documentation
│   ├── usage.md
│   └── demo.gif
├── logs/                           # Logs
│   ├── transcribe.log              # To be created
│   ├── analyze.log
│   └── export_vegas.log
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── requirements.txt
└── README.md
```

## Configuration
Edit `config/settings.json` to customize the tool:
- **`GEMINI_API_KEY`**: Your Gemini API key (required).
- **`OUTPUT_DIR`**: Directory for output files (default: `output`).

To obtain a Gemini API key:
1. Visit [Gemini API website](https://example.com) (replace with the actual URL).
2. Sign up and generate an API key.
3. Insert it into `config/settings.json`.

## Dependencies
Install dependencies listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```
Key dependencies include:
- `requests`: For API calls to Gemini.
- Python built-in modules: `os`, `sys`, `re`, `logging`, `time`.

## How It Works
1. **Analysis Phase**:
   - `analyze.py` reads the transcription and fanfiction description.
   - Uses Gemini API to break the text into scenes and suggest music/sound effects.
   - Outputs recommendations in milliseconds with detailed metadata.

2. **Export Phase**:
   - `export_vegas.py` processes the analysis files.
   - Converts millisecond timings to Vegas Pro’s HH:MM:SS:FF format.
   - Ensures no overlaps in music regions and unique sound marker positions.

## Customization
- **Prompts**: Edit the `.txt` files in `prompts/` to adjust how Gemini interprets the text or formats output.
- **Frame Rate**: Modify `milliseconds_to_vegas_time` in `export_vegas.py` if your Vegas Pro project uses a different frame rate (default is ~30 fps).
- **Output Path**: Change `OUTPUT_DIR` in `config/settings.json` for a custom output location.

## Troubleshooting
- **Script Hangs**: Check internet connection and Gemini API key validity.
- **No Output Files**: Verify input file paths and check logs (`logs/analyze.log` or `logs/export_vegas.log`).
- **Gemini Errors**: Ensure `src/utils/api.py` is correctly implemented and the API key is active.
- **Timing Issues**: Confirm transcription timings are in milliseconds and match the expected format.

For detailed debugging:
```bash
tail -f logs/analyze.log
tail -f logs/export_vegas.log
```

## Contributing
Feel free to fork the repository and submit pull requests with improvements! Ideas for enhancement:
- Support for other editing software (e.g., Audacity, Premiere Pro).
- GUI for easier usage.
- Batch processing for multiple chunks.

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Happy audiobook editing!