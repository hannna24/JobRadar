from pydantic import BaseModel
from typing import Optional, List

class UserProfile(BaseModel):
    field: str              # e.g. 'Data Science'
    role: str               # e.g. 'ML Engineer'
    skills: List[str]       # e.g. ['Python', 'SQL']
    location: str           # e.g. 'London' or 'Remote'
    experience: str         # 'junior', 'mid', or 'senior'
    remote: bool = False    # prefers remote?

class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str             # 'adzuna' or 'remotive'
    salary: Optional[str] = None

class ScoredJob(BaseModel):
    job: JobPosting
    score: int              # 1-10
    reason: str             # LLM's explanation
