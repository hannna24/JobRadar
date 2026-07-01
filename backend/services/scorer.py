import asyncio
import json
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from models.schemas import JobPosting, ScoredJob, UserProfile
from utils.models import scorer_model

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
- Description: {job.description[:500]}

How well does this job match the candidate?'''


async def score_job(profile: UserProfile, job: JobPosting) -> ScoredJob:
    async with _semaphore:
        try:
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=build_user_prompt(profile, job)),
            ]
            resp = await scorer_model.ainvoke(messages)

            # strip markdown fences if present
            raw = resp.content.strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            result = json.loads(raw.strip())
            return ScoredJob(job=job, score=result['score'], reason=result['reason'])

        except json.JSONDecodeError as e:
            print(f"JSON PARSE ERROR for '{job.title}': {e}")
            print(f"Raw response was: {resp.content[:200]}")
            return ScoredJob(job=job, score=5, reason='Could not parse score.')

        except Exception as e:
            print(f"SCORING ERROR for '{job.title}': {type(e).__name__}: {e}")
            return ScoredJob(job=job, score=5, reason='Could not score this job.')


async def score_all_jobs(profile: UserProfile, jobs: List[JobPosting]) -> List[ScoredJob]:
    scored = await asyncio.gather(*[score_job(profile, j) for j in jobs])
    return sorted(scored, key=lambda x: x.score, reverse=True)
