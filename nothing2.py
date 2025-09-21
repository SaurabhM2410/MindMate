import os
from openai import OpenAI

# Use environment variable for API key (more secure)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
)

def ai_chat(user_message):
    """Send a message to OpenAI's GPT and return the response."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Test the function when script is run directly
if __name__ == "__main__":
    # Example usage
    test_message = "Hello, how are you?"
    print(f"User: {test_message}")
    print(f"AI: {ai_chat(test_message)}")