import httpx
from models.schemas import JobPosting
from config import ADZUNA_APP_ID, ADZUNA_APP_KEY, MAX_JOBS_PER_FETCH
from typing import List

async def fetch_adzuna_jobs(query: str, location: str) -> List[JobPosting]:
    # Adzuna doesn't cover Egypt ('eg' 404s) — 'us' gives the broadest ML/AI job market.
    # TODO: add JSearch (RapidAPI) once we have a key, for actual Egypt coverage via Google Jobs.
    url = f'https://api.adzuna.com/v1/api/jobs/us/search/1'
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'what': query,
        'results_per_page': MAX_JOBS_PER_FETCH,
        'content-type': 'application/json'
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    jobs = []
    for item in data.get('results', []):
        jobs.append(JobPosting(
            title=item.get('title', ''),
            company=item.get('company', {}).get('display_name', ''),
            location=item.get('location', {}).get('display_name', ''),
            description=item.get('description', '')[:1000], # truncate
            url=item.get('redirect_url', ''),
            source='adzuna',
            salary=f"{item.get('salary_min','')}-{item.get('salary_max','')}" or None
        ))
    data = resp.json()
    print(f"ADZUNA: got {len(data.get('results', []))} results for '{query}' in '{location}'")
    for item in data.get('results', [])[:3]:
        print(f"  - {item.get('title')} | {item.get('location', {}).get('display_name')}")    
    return jobs
  
    
def is_relevant(job: JobPosting, profile) -> bool:
    """Quick keyword check before sending to expensive LLM scorer."""
    role_keywords = profile.role.lower().split()
    field_keywords = profile.field.lower().split()
    all_keywords = role_keywords + field_keywords + [s.lower() for s in profile.skills]
    
    job_text = f"{job.title} {job.description}".lower()
    
    # Job must match at least ONE keyword from role/field/skills
    return any(kw in job_text for kw in all_keywords)



async def fetch_remotive_jobs(query: str) -> List[JobPosting]:
    url = 'https://remotive.com/api/remote-jobs'
    params = {'search': query, 'limit': MAX_JOBS_PER_FETCH}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    jobs = []
    for item in data.get('jobs', []):
        jobs.append(JobPosting(
            title=item.get('title', ''),
            company=item.get('company_name', ''),
            location=item.get('candidate_required_location', 'Remote'),
            description=item.get('description', '')[:1000],
            url=item.get('url', ''),
            source='remotive',
            salary=item.get('salary')
        ))
    return jobs


async def fetch_all_jobs(query: str, location: str, remote: bool = False) -> List[JobPosting]:
    adzuna = await fetch_adzuna_jobs(query, location)
    
    # Only call Remotive if user explicitly wants remote work
    if remote:
        remotive = await fetch_remotive_jobs(query)
        return adzuna + remotive
    
    return adzuna
