"""
Semantic Job Search -- embed job postings into FAISS, search by candidate profile.
"""
import json
import numpy as np
import pandas as pd

from src.config import JOBS_CSV, JOBS_INDEX_DIR, JOB_TEXT_COLUMNS, TOP_N_JOBS
from src.search.embed import embed_texts, embed_single


def _load_faiss():
    try:
        import faiss
    except ImportError as exc:
        raise ImportError(
            "The faiss module is missing. Install the project requirements and run Streamlit from the virtual environment."
        ) from exc
    return faiss

METADATA_PATH = JOBS_INDEX_DIR / "jobs_metadata.json"
INDEX_PATH = JOBS_INDEX_DIR / "jobs.index"


def _combine_row(row) -> str:
    parts = [str(row[col]) for col in JOB_TEXT_COLUMNS if col in row and pd.notna(row[col])]
    return " | ".join(parts)


def build_job_index(limit: int | None = 60):
    faiss = _load_faiss()
    JOBS_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(JOBS_CSV)
    if limit:
        df = df.head(limit)

    texts = [_combine_row(row) for _, row in df.iterrows()]
    print(f"Embedding {len(texts)} job postings...")
    vectors = embed_texts(texts)

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, str(INDEX_PATH))

    metadata = df[["jobtitle", "company", "joblocation_address", "skills", "jobdescription"]].to_dict(orient="records")
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Saved FAISS index -> {INDEX_PATH}")
    print(f"Saved metadata -> {METADATA_PATH}")


def search_jobs(profile: dict, top_n: int = TOP_N_JOBS) -> list[dict]:
    faiss = _load_faiss()
    index = faiss.read_index(str(INDEX_PATH))
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    query_text = " | ".join([
        profile.get("target_role", ""),
        ", ".join(profile.get("skills", [])),
    ])
    query_vector = embed_single(query_text).reshape(1, -1)

    distances, indices = index.search(query_vector, top_n)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(metadata):
            continue
        job = metadata[idx]
        job["match_score"] = float(dist)
        results.append(job)

    return results


if __name__ == "__main__":
    build_job_index(limit=60)

    sample_profile = {
        "target_role": "Data Analyst",
        "skills": ["SQL", "Excel", "Python", "Tableau"],
    }
    matches = search_jobs(sample_profile, top_n=5)
    print("\nTop matches:")
    for m in matches:
        print(f"- {m['jobtitle']} @ {m['company']} (score: {m['match_score']:.2f})")
