# scripts/utils.py
import time
import google.generativeai as genai
import config

def send_gemini_request(prompt):
    # Set up the Gemini client with your API key
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")  # Updated model name
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 65536,
        "response_mime_type": "text/plain"
    }
    contents = [prompt]  # Simplified content structure

    # Retry logic for errors
    attempts = 0
    delay = 10  # Start with 10 seconds
    while attempts < 5:  # Try up to 5 times
        try:
            response = model.generate_content(contents, generation_config=generation_config)
            return response.text  # Success!
        except Exception as e:
            if '403' in str(e):  # Permission error
                print(f"API error 403, waiting {delay} seconds...")
                time.sleep(delay)
                delay += 15  # Increase delay: 10, 25, 40...
                attempts += 1
            else:
                print(f"Error: {e}")
                return None
    print("Failed after 5 tries.")
    return None