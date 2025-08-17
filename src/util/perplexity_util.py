import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    raise EnvironmentError("PERPLEXITY_API_KEY is not set. Please add it to your .env file.")

client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

def summarize_text(text):
    response = client.chat.completions.create(
        model="sonar",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Please summarize the following text in 3 sentances: {text}"}
        ],
        max_tokens=200,
        temperature=0.7
    )

    return response.choices[0].message.content