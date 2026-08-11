"""
SmartHire GenAI portal (Streamlit).
Run locally: streamlit run app/streamlit_app.py

Wires together pieces that already work in src/:
    upload CV -> parsed profile -> matched jobs -> (CV suggestions / mentor chat coming soon)
"""
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

import streamlit as st

# Make sure "src" is importable when Streamlit runs this file directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load local .env first, then prefer Streamlit secrets if available.
load_dotenv(PROJECT_ROOT / ".env")
api_key = None
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    api_key = None

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

st.set_page_config(page_title="SmartHire GenAI", page_icon="\U0001F4BC", layout="wide")

if not api_key:
    st.title("SmartHire GenAI")
    st.error("GEMINI_API_KEY not found. Set it in Streamlit secrets or in .env, then redeploy.")
    st.stop()

try:
    from src import config
    from src.parsing.loader import load_text
    from src.parsing.resume_parser import parse_resume
    from src.search.job_search import search_jobs, build_job_index, INDEX_PATH
except ImportError as e:
    st.title("SmartHire GenAI")
    st.error("A required dependency is missing in the current Python environment.")
    st.markdown(
        "Install the project requirements and run Streamlit from the virtual environment: "
        "`python -m pip install -r requirements.txt` then `./.venv/Scripts/streamlit.exe run app/streamlit_app.py`."
    )
    st.exception(e)
    st.stop()
except Exception as e:
    st.title("SmartHire GenAI")
    st.error("Failed to initialize the app. Check that GEMINI_API_KEY is set and the project dependencies are installed.")
    st.exception(e)
    st.stop()

st.title("SmartHire GenAI")
st.caption("Upload a resume to get a parsed profile and AI-matched jobs.")

@st.cache_resource
def ensure_job_index():
    if not INDEX_PATH.exists():
        with st.spinner("Building job index for the first time (this can take a few minutes)..."):
            build_job_index(limit=60)
    return True

try:
    ensure_job_index()
except Exception as e:
    st.title("SmartHire GenAI")
    st.error("Failed to prepare the job index. Make sure data is available and faiss-cpu is installed.")
    st.exception(e)
    st.stop()

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    temp_path = PROJECT_ROOT / "data" / "resumes" / uploaded_file.name
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Parsing your resume..."):
        resume_text = load_text(temp_path)
        profile = parse_resume(resume_text)

    st.success(f"Parsed profile for **{profile.get('name', 'candidate')}**")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Parsed Profile")
        st.write(f"**Target role:** {profile.get('target_role', 'N/A')}")
        st.write(f"**Email:** {profile.get('email', 'N/A')}")
        st.write(f"**Phone:** {profile.get('phone', 'N/A')}")
        st.write("**Skills:**")
        st.write(", ".join(profile.get("skills", [])) or "None found")

        st.write("**Experience:**")
        for exp in profile.get("experience", []):
            st.markdown(f"- **{exp.get('role', '')}** at {exp.get('company', '')} ({exp.get('duration', '')})")

        st.write("**Education:**")
        for edu in profile.get("education", []):
            st.markdown(f"- {edu.get('degree', '')}, {edu.get('institution', '')} ({edu.get('year', '')})")

    with col2:
        st.subheader("Top Matching Jobs")
        with st.spinner("Searching for matching jobs..."):
            matches = search_jobs(profile, top_n=5)

        for m in matches:
            with st.container(border=True):
                st.markdown(f"**{m.get('jobtitle', 'Untitled role')}**")
                st.caption(f"{m.get('company', '')} -- {m.get('joblocation_address', '')}")
                st.write(f"Match score: `{m.get('match_score', 0):.2f}` (lower = closer match)")
                with st.expander("Job description"):
                    st.write(m.get("jobdescription", "No description available."))
else:
    st.info("Upload a PDF, DOCX, or TXT resume above to get started.")

st.divider()
st.caption("CV improvement suggestions and the AI Career Mentor chat are coming soon.")
