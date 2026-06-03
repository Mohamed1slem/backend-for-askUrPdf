import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
key = os.getenv("GROQ_API_KEY")
print("Found Key in .env:", key[:8] + "..." if key else "None")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=key
)

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Hello! Say hi."}
        ]
    )
    print("\n[SUCCESS] Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print("\n[ERROR] Failed to query Groq:", e)
