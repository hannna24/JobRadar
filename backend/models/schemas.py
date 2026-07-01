from pydantic import BaseModel
from typing import Optional, List


class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str             # 'adzuna' or 'remotive'

class ScoredJob(BaseModel):
    job: JobPosting
    score: int              # 1-10
    reason: str             # LLM's explanation
    job_id: Optional[str] = None  # set by the route so the frontend can report status

class UserProfile(BaseModel):
    user_id: str = 'default_user'  # ← NEW: used for history tracking
    field: str              # e.g. 'Data Science'
    role: str               # e.g. 'ML Engineer'
    skills: List[str]       # e.g. ['Python', 'SQL']
    location: str           # e.g. 'London' or 'Remote'
    experience: str         # 'junior', 'mid', or 'senior'
    remote: bool = False    # prefers remote?

class JobQuery(BaseModel):          # ← NEW: for the /api/ask route
    question: str                   # e.g. 'any remote Python jobs this week?'

class RAGResponse(BaseModel):       # ← NEW: what /api/ask returns
    answer: str

class StatusUpdate(BaseModel):      # ← NEW: for the /api/status route
    user_id: str = 'default_user'
    job_id: str
    status: str                     # 'applied' or 'rejected'
