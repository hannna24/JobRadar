#SQLite user history

from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import datetime
from typing import Set

DATABASE_URL = 'sqlite:///./db/jobradar.db'
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

class Base(DeclarativeBase): pass

class UserJobHistory(Base):
    __tablename__ = 'user_job_history'
    id       = Column(String, primary_key=True)   # user_id + job_id
    user_id  = Column(String, nullable=False)
    job_id   = Column(String, nullable=False)     # same MD5 as Chroma
    status   = Column(String, default='viewed')   # viewed/applied/rejected
    added_at = Column(DateTime, default=datetime.utcnow)

# Create the table if it doesn't exist yet
Base.metadata.create_all(engine)

def get_seen_job_ids(user_id: str) -> Set[str]:
    '''Get all job IDs this user has already seen.'''
    with Session(engine) as session:
        rows = session.query(UserJobHistory.job_id)\
                      .filter_by(user_id=user_id).all()
        return {row.job_id for row in rows}

def mark_jobs_seen(user_id: str, job_ids: list):
    '''Record that a user was shown these jobs.'''
    with Session(engine) as session:
        for job_id in job_ids:
            record_id = f'{user_id}_{job_id}'
            if not session.get(UserJobHistory, record_id):
                session.add(UserJobHistory(
                    id=record_id, user_id=user_id, job_id=job_id
                ))
        session.commit()

def update_job_status(user_id: str, job_id: str, status: str):
    '''Update status when user clicks applied/rejected.'''
    with Session(engine) as session:
        record = session.get(UserJobHistory, f'{user_id}_{job_id}')
        if record:
            record.status = status
            session.commit()
