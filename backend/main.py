from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.jobs import router as jobs_router

app = FastAPI(title='JobRadar AI', version='1.0.0')

# Allow frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],   # in production, restrict this
    allow_methods=['*'],
    allow_headers=['*'],
)
# Register routes
app.include_router(jobs_router, prefix='/api')

# Serve frontend files
app.mount('/', StaticFiles(directory='../frontend', html=True))

