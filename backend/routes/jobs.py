from fastapi import APIRouter, HTTPException
from models.schemas import UserProfile, ScoredJob
from services.job_fetcher import fetch_all_jobs, is_relevant
from services.scorer import score_all_jobs
from typing import List

router = APIRouter()

@router.post('/jobs', response_model=List[ScoredJob])
async def get_scored_jobs(profile: UserProfile):
    # Keep the query short — Adzuna returns nothing for long, over-qualified queries
    query = profile.role

    # Fetch jobs from all sources
    jobs = await fetch_all_jobs(query, profile.location, profile.remote)
    print(f"Fetched {len(jobs)} total jobs")

    # Filter before scoring — saves tokens and improves results
    relevant = [j for j in jobs if is_relevant(j, profile)]
    print(f"After keyword filter: {len(relevant)} relevant jobs")

    if not relevant:
        raise HTTPException(404, "No relevant jobs found. Try broader keywords.")

    scored = await score_all_jobs(profile, relevant[:10])
    return scored

