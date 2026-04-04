import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing models:")
for m in client.models.list():
    if "embed" in m.name.lower():
        print(m.name, m.supported_actions)

print("\nTesting text-embedding-004:")
try:
    response = client.models.embed_content(
        model="text-embedding-004",
        contents="Hello world"
    )
    print("Success text-embedding-004")
except Exception as e:
    print("Error text-embedding-004:", e)
