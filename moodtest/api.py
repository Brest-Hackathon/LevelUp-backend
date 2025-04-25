import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def call_openrouter(prompt, model="deepseek/deepseek-chat-v3-0324:free"):
    """Core API communication function [[9]]"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        return None
