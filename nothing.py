import requests

def ai_chat(user_message):
    # Use Qoder's AI API (check documentation)
    response = requests.post("https://api.qoder.ai/chat", json={"message": user_message})
    return response.json()["reply"]