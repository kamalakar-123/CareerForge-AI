"""Test Gemini API connection"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-10:] if GEMINI_API_KEY else 'NOT FOUND'}")

# First, list available models
print("\n=== Listing Available Models ===")
list_models_url = f'https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}'

try:
    response = requests.get(list_models_url, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if 'models' in result:
            print(f"\nAvailable models:")
            for model in result['models']:
                name = model.get('name', 'Unknown')
                supported_methods = model.get('supportedGenerationMethods', [])
                print(f"  - {name}")
                print(f"    Methods: {', '.join(supported_methods)}")
        else:
            print("No models found in response")
            print(result)
    else:
        print(f"Error listing models:")
        print(response.text)

except Exception as e:
    print(f"Exception: {e}")

# Now test with a specific model
print("\n\n=== Testing generateContent ===")

# Try different model names
model_names = [
    'gemini-flash-latest',  # Latest flash model (alias)
    'gemini-pro-latest',     # Latest pro model (alias)
    'gemini-2.5-flash',      # Specific version
    'gemini-2.5-pro',        # Specific version
]

for model_name in model_names:
    GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}'
    
    try:
        print(f"\nTrying model: {model_name}")
        payload = {
            "contents": [{
                "parts": [{"text": "Say 'Hello, this is a test'"}]
            }]
        }
        
        response = requests.post(GEMINI_API_URL, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    text = candidate['content']['parts'][0]['text']
                    print(f"✅ SUCCESS! Response: {text}")
                    print(f"\n✅✅✅ USE THIS MODEL: {model_name} ✅✅✅")
                    break
        else:
            print(f"   Error: {response.json().get('error', {}).get('message', 'Unknown error')}")
        
    except Exception as e:
        print(f"   Exception: {e}")

