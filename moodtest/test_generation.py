import json
from .api import call_openrouter

def generate_mood_test():
    """Generate standardized mood test questions [[3]]"""
    prompt = (
        "Create a JSON-formatted mood test with 10 questions. "
        "Each question must have: 'question' and 'options' (3 items). "
        "Format: List[Dict]. No explanations. Just test and nothing else, without any additional information"
    )
    response = call_openrouter(prompt)
    response = response.replace("```json", "")
    response = response.replace("```", "")
    print(response)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("Failed to parse test JSON")
        return []
