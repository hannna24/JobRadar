#Chroma operations

import chromadb
import hashlib
from models.schemas import JobPosting
from services.embedder import embed_jobs, embed_query
from typing import List

# Initialize Chroma with persistent storage
# Data survives server restarts — stored in chroma_db/ folder
_client = chromadb.PersistentClient(path='../chroma_db')
_collection = _client.get_or_create_collection(
    name='jobs',
    metadata={'hnsw:space': 'cosine'}  # use cosine similarity
)

def make_job_id(job: JobPosting) -> str:
    '''Create a stable unique ID from job content.
    Same job from two different sources = same ID = deduplication.'''
    key = f'{job.title.lower().strip()}_{job.company.lower().strip()}'
    return hashlib.md5(key.encode()).hexdigest()

def job_exists(job: JobPosting) -> bool:
    '''Check if this job is already in the vector store.'''
    job_id = make_job_id(job)
    result = _collection.get(ids=[job_id])
    return len(result['ids']) > 0

def save_jobs(jobs: List[JobPosting]) -> int:
    '''Embed and store jobs. Skips duplicates. Returns count saved.'''
    new_jobs = [j for j in jobs if not job_exists(j)]
    if not new_jobs:
        return 0

    embeddings = embed_jobs(new_jobs)
    ids = [make_job_id(j) for j in new_jobs]
    documents = [f'{j.title} at {j.company}' for j in new_jobs]
    metadatas = [{
        'title': j.title, 'company': j.company,
        'location': j.location, 'url': j.url,
        'source': j.source
    } for j in new_jobs]

    _collection.add(
        ids=ids, embeddings=embeddings,
        documents=documents, metadatas=metadatas
    )
    return len(new_jobs)

def search_jobs(query: str, n_results: int = 10) -> List[dict]:
    '''Find the N most semantically similar jobs to a query.'''
    query_vector = embed_query(query)
    results = _collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=['documents', 'metadatas', 'distances']
    )
    jobs = []
    for i, meta in enumerate(results['metadatas'][0]):
        jobs.append({
            **meta,
            'similarity': 1 - results['distances'][0][i]
        })
    return jobs
