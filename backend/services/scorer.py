import asyncio
import json
from groq import AsyncGroq
from models.schemas import UserProfile, JobPosting, ScoredJob
from config import GROQ_API_KEY, LLM_MODEL
from typing import List

client = AsyncGroq(api_key=GROQ_API_KEY)

# ← ADD THIS: limits to 3 concurrent requests at a time
_semaphore = asyncio.Semaphore(3)

SYSTEM_PROMPT = '''You are a career matching expert. Respond ONLY
with JSON: {"score": <1-10>, "reason": "<one sentence>"}.'''

def build_user_prompt(profile: UserProfile, job: JobPosting) -> str:
    return f'''Candidate profile:
- Field: {profile.field}
- Target role: {profile.role}
- Skills: {", ".join(profile.skills)}
- Location preference: {profile.location} (remote: {profile.remote})
- Experience level: {profile.experience}

Job posting:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location}
- Source: {job.source}
- Description: {job.description}

How well does this job match the candidate?'''

async def score_job(profile: UserProfile, job: JobPosting) -> ScoredJob:
    async with _semaphore:   # ← WRAP the request in the semaphore
        try:
            resp = await client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(profile, job)}
                ],
                max_tokens=100,
                temperature=0.1,
            )
            result = json.loads(resp.choices[0].message.content)
            return ScoredJob(job=job, score=result["score"], reason=result["reason"])
        except Exception:
            # ← ADD THIS: one bad job won't crash the whole request
            return ScoredJob(job=job, score=5, reason="Could not score this job.")

async def score_all_jobs(profile: UserProfile, jobs: List[JobPosting]) -> List[ScoredJob]:
    scored = await asyncio.gather(*[score_job(profile, j) for j in jobs])
    return sorted(scored, key=lambda x: x.score, reverse=True)