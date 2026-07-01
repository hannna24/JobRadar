from fastapi import APIRouter, HTTPException
from models.schemas import UserProfile, ScoredJob, JobQuery, RAGResponse, StatusUpdate
from services.job_fetcher import fetch_all_jobs
from services.scorer import score_all_jobs
from typing import List
from services.rag import ask_about_jobs
from services.vector_store import save_jobs, make_job_id
from services.history import get_seen_job_ids, mark_jobs_seen, update_job_status

router = APIRouter()

@router.post('/jobs', response_model=List[ScoredJob])
async def get_scored_jobs(profile: UserProfile):
    query = f'{profile.role} {profile.field}'
    jobs = await fetch_all_jobs(query, profile.location, profile.remote)
    if not jobs:
        raise HTTPException(404, 'No jobs found')

    # Step 1: Save new jobs to Chroma (deduplicates automatically)
    save_jobs(jobs)

    # Step 2: Filter out jobs user has already seen
    seen_ids = get_seen_job_ids(profile.user_id)
    new_jobs = [j for j in jobs if make_job_id(j) not in seen_ids]

    if not new_jobs:
        return []   # user has seen everything — signal to frontend

    # Step 3: Score only the new jobs
    scored = await score_all_jobs(profile, new_jobs)
    top = scored[:15]

    # Step 4: Attach job_id so the frontend can report status back
    for s in top:
        s.job_id = make_job_id(s.job)

    # Step 5: Mark these as seen in history
    mark_jobs_seen(profile.user_id, [s.job_id for s in top])

    return top


@router.post('/ask', response_model=RAGResponse)
async def ask_jobs_question(query: JobQuery):
    '''RAG endpoint: user asks a question, gets an AI answer
    grounded in real jobs stored in Chroma.'''
    answer = await ask_about_jobs(query.question)
    return RAGResponse(answer=answer)


@router.post('/status')
async def set_job_status(payload: StatusUpdate):
    '''Record that the user marked a job as applied/rejected.'''
    update_job_status(payload.user_id, payload.job_id, payload.status)
    return {'ok': True}


# @router.post('/jobs', response_model=List[ScoredJob])
# async def get_scored_jobs(profile: UserProfile):
#     # Keep the query short — Adzuna returns nothing for long, over-qualified queries
#     query = profile.role

#     # Fetch jobs from all sources
#     jobs = await fetch_all_jobs(query, profile.location, profile.remote)
#     print(f"Fetched {len(jobs)} total jobs")

#     # Filter before scoring — saves tokens and improves results
#     relevant = [j for j in jobs if is_relevant(j, profile)]
#     print(f"After keyword filter: {len(relevant)} relevant jobs")

#     if not relevant:
#         raise HTTPException(404, "No relevant jobs found. Try broader keywords.")

#     scored = await score_all_jobs(profile, relevant[:10])
#     return scored

