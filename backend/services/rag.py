#Q&A pipeline

from utils.models import rag_model
from services.vector_store import search_jobs
from langchain_core.messages import SystemMessage, HumanMessage

RAG_SYSTEM = '''You are a job search assistant with access to a
database of recent job postings. Answer the user's question
ONLY using the job data provided below. If no jobs match,
say so honestly. Be specific — mention company names, titles,
and locations from the data. Do not invent jobs.'''

def format_jobs_as_context(jobs: list) -> str:
    '''Format retrieved jobs into readable context for the LLM.'''
    if not jobs:
        return 'No matching jobs found in the database.'
    lines = ['RETRIEVED JOB POSTINGS:', '---']
    for i, job in enumerate(jobs, 1):
        lines.append(f'{i}. {job["title"]} at {job["company"]}'
                    f'({job["location"]}) - Similarity: {job["similarity"]:.2f}')
        lines.append(f'   Apply: {job["url"]}')
        lines.append('')
    return ' '.join(lines)

async def ask_about_jobs(question: str) -> str:
    '''Full RAG pipeline: retrieve relevant jobs, answer the question.'''
    # Step 1: retrieve
    relevant_jobs = search_jobs(question, n_results=8)

    # Step 2: build context
    context = format_jobs_as_context(relevant_jobs)

    # Step 3: generate answer
    messages = [
        SystemMessage(content=RAG_SYSTEM),
        HumanMessage(content=f'{context}  User question: {question}')
    ]
    response = await rag_model.ainvoke(messages)
    return response.content
