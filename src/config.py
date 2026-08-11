"""Paths, model names, and constants. Import from here instead of hard-coding."""
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()

# ---- Folders ----
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
JOBS_DIR = DATA_DIR / "jobs"
RESUMES_DIR = DATA_DIR / "resumes"
CAREER_NOTES_DIR = DATA_DIR / "career_notes"

VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"
JOBS_INDEX_DIR = VECTORSTORE_DIR / "jobs_faiss"
NOTES_INDEX_DIR = VECTORSTORE_DIR / "notes_faiss"

JOBS_CSV = JOBS_DIR / "naukri_com-job_sample.csv"

CHAT_MODEL = "gemini-flash-latest"
EMBED_MODEL = "models/gemini-embedding-001"
EMBED_DIM = 768

API_KEY_ENV = "GEMINI_API_KEY"
API_KEY = os.getenv(API_KEY_ENV)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

TOP_N_JOBS = 5
TOP_K_NOTES = 3

JOB_TEXT_COLUMNS = ["jobtitle", "skills", "jobdescription"]
