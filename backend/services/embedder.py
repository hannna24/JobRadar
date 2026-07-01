#converts jobs to vectors

from sentence_transformers import SentenceTransformer
from models.schemas import JobPosting
from typing import List

# Model loads ONCE when the module is first imported
# First run: downloads ~80MB. All subsequent runs: loads from cache.
_model = SentenceTransformer('all-MiniLM-L6-v2')

def build_job_text(job: JobPosting) -> str:
    '''Combine fields into one string for embedding.
    More context = better embedding quality.'''
    return f'''
    Job Title: {job.title}
    Company: {job.company}
    Location: {job.location}
    Description: {job.description[:600]}
    '''.strip()

def embed_job(job: JobPosting) -> List[float]:
    '''Returns a 384-dimensional vector for one job.'''
    text = build_job_text(job)
    embedding = _model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def embed_jobs(jobs: List[JobPosting]) -> List[List[float]]:
    '''Batch embed multiple jobs at once (faster than one by one).'''
    texts = [build_job_text(j) for j in jobs]
    embeddings = _model.encode(texts, normalize_embeddings=True, batch_size=32)
    return embeddings.tolist()

def embed_query(query: str) -> List[float]:
    '''Embed a user's question for RAG similarity search.'''
    embedding = _model.encode(query, normalize_embeddings=True)
    return embedding.tolist()
