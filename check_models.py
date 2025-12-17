import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load your API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env file.")
else:
    genai.configure(api_key=api_key)

    print("--- contacting Google API ---")
    try:
        # List all models available to your key
        found = False
        for m in genai.list_models():
            # We only care about models that can generate text (Chat)
            if 'generateContent' in m.supported_generation_methods:
                print(f"AVAILABLE: {m.name}")
                found = True
        
        if not found:
            print("No models found. Check if your API Key has 'Generative AI API' enabled in Google Cloud Console.")
            
    except Exception as e:
        print(f"Error connecting to Google: {e}")