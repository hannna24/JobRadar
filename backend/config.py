""" This file loads all environment variables and makes them available throughout the app"""

# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()   # reads .env file

ADZUNA_APP_ID  = os.getenv('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY')
GROQ_API_KEY   = os.getenv('GROQ_API_KEY')

# App settings
MAX_JOBS_PER_FETCH = 20   # how many jobs to pull per API call
LLM_MODEL = 'llama-3.3-70b-versatile'  # Groq's free fast model


