# config/config.py
import os
import json

# Load settings from settings.json
with open('config/settings.json', 'r') as f:
    settings = json.load(f)

# Directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, settings['output_dir'])

# API keys
GEMINI_API_KEY = settings['gemini_api_key']