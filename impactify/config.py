import os
from dotenv import load_dotenv, find_dotenv
from pydantic import SecretStr
from langchain_groq import ChatGroq

load_dotenv(find_dotenv())
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=SecretStr(GROQ_API_KEY) if GROQ_API_KEY is not None else None,
        temperature=0,
    )