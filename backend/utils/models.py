#centralized LLM config

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# init_chat_model doesn't take an API key directly. It reads it automatically from your .env file.
# As long as load_dotenv() runs at startup, init_chat_model finds the key automatically.
load_dotenv()

# Scoring model — low temperature for consistent job scoring
scorer_model = init_chat_model('groq:llama-3.3-70b-versatile', temperature=0.1)

# RAG model — slightly higher temp for natural answers
rag_model = init_chat_model('groq:llama-3.3-70b-versatile',temperature=0.3)
