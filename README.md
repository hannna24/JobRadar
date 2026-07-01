# JobRadar AI

A personalized job alert web app that fetches real job postings and uses
an LLM to score how well each one matches your profile.

## What it does
- Takes your field, role, skills, location and experience level
- Fetches jobs from Adzuna and Remotive APIs
- Scores each job 1-10 using Groq (Llama 3.3 70B) against your profile
- Returns a ranked feed of relevant opportunities

## APIs used
- Adzuna API - job listings (developer.adzuna.com)
- Remotive API - remote jobs, no key needed (remotive.com/api)
- Groq API - free LLM scoring (console.groq.com)

## How to run

1. Clone the repo and create a virtual environment
   python -m venv .venv
   .venv\Scripts\activate

2. Install dependencies
   pip install -r requirements.txt

3. Create a .env file in the root with your keys
   ADZUNA_APP_ID=your_id
   ADZUNA_APP_KEY=your_key
   GROQ_API_KEY=your_key

4. Start the server
   cd backend
   uvicorn main:app --reload --port 8000

5. Open http://localhost:8000 in your browser

## Tech stack
FastAPI · uvicorn · httpx · Groq SDK · Pydantic · Python 3.11+