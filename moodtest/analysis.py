import os
import json
from .api import call_openrouter

def analyze_mood(answers):
    """Analyze mood based on test answers [[2]]"""
    prompt = (
        "Analyze mood from answers (1-4 scale). "
        "Return only the numerical score. "
        f"Answers:\n{json.dumps(answers, indent=2)}"
    )
    response = call_openrouter(prompt)
    
    try:
        return int(response.strip()[0])
    except (ValueError, IndexError):
        print("Invalid analysis response")
        return None
