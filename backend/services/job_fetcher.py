import httpx
from models.schemas import JobPosting
from config import ADZUNA_APP_ID, ADZUNA_APP_KEY, MAX_JOBS_PER_FETCH
from typing import List

async def fetch_adzuna_jobs(query: str, location: str) -> List[JobPosting]:
    url = f'https://api.adzuna.com/v1/api/jobs/gb/search/1'
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'what': query,
        'where': location,
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
    return jobs

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

async def fetch_all_jobs(query: str, location: str) -> List[JobPosting]:
    # Run both fetches and combine results
    adzuna = await fetch_adzuna_jobs(query, location)
    remotive = await fetch_remotive_jobs(query)
    return adzuna + remotive
