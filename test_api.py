import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in environment variables.")

genai.configure(api_key=api_key)
llm = genai.GenerativeModel(model_name=model_name)
response = llm.generate_content("Xin chào?")
print(response.text)