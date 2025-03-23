# src/utils/api.py
import time
import logging
import google.generativeai as genai

# Add the project root directory to sys.path
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import config

# Create a specific logger for this module
logger = logging.getLogger('api')
logger.setLevel(logging.INFO)

# File handler for logging to file
file_handler = logging.FileHandler('logs/api.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Stream handler for logging to terminal
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Clear existing handlers and add both
logger.handlers = []
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def send_gemini_request(
    prompt,
    model_name="gemini-2.0-flash-thinking-exp-01-21",
    temperature=0.7,
    top_p=0.95,
    top_k=64,
    max_output_tokens=65536
):
    """
    Sends a request to the Gemini API and returns the response.

    Args:
        prompt (str): The prompt to send to Gemini.
        model_name (str): The Gemini model to use (default: gemini-2.0-flash-thinking-exp-01-21).
        temperature (float): Sampling temperature (default: 0.7).
        top_p (float): Top-p sampling parameter (default: 0.95).
        top_k (int): Top-k sampling parameter (default: 64).
        max_output_tokens (int): Maximum number of output tokens (default: 65536).

    Returns:
        str: The response text, or None if the request fails.
    """
    # Set up the Gemini client
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name)
        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens,
            "response_mime_type": "text/plain"
        }
        contents = [prompt]
    except Exception as e:
        logger.error(f"Error setting up Gemini client: {e}")
        return None

    # Count tokens before sending the request
    try:
        token_count = model.count_tokens(contents)
        prompt_tokens = token_count.total_tokens
        logger.info(f"Prompt token count: {prompt_tokens}")
    except Exception as e:
        logger.warning(f"Could not count tokens before request: {e}")
        prompt_tokens = None

    # Log the request
    logger.info(f"Sending request to Gemini model '{model_name}' with prompt length {len(prompt)} characters...")

    # Retry logic for errors
    attempts = 0
    delay = 10  # Start with 10 seconds
    max_attempts = 5
    while attempts < max_attempts:
        try:
            response = model.generate_content(contents, generation_config=generation_config)
            # Extract token usage from response
            usage = response.usage_metadata
            logger.info(f"Token usage: prompt={usage.prompt_token_count}, output={usage.candidates_token_count}, total={usage.total_token_count}")
            logger.info("Request successful.")
            return response.text
        except Exception as e:
            error_str = str(e)
            if '403' in error_str:  # Permission error
                logger.warning(f"API error 403, retrying in {delay} seconds... (Attempt {attempts + 1}/{max_attempts})")
                time.sleep(delay)
                delay += 15  # Increase delay: 10, 25, 40...
                attempts += 1
            elif '429' in error_str:  # Rate limit error
                logger.warning(f"API error 429 (rate limit), retrying in {delay} seconds... (Attempt {attempts + 1}/{max_attempts})")
                time.sleep(delay)
                delay += 15
                attempts += 1
            else:
                logger.error(f"Error in Gemini request: {e}")
                return None

    logger.error(f"Failed after {max_attempts} attempts.")
    return None