"""
Resume Parser -- extracts structured JSON from raw resume text using Gemini.
"""
import json
from google import genai
from google.genai import types

from src.config import API_KEY, CHAT_MODEL

client = genai.Client(api_key=API_KEY)

RESUME_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "phone": {"type": "string"},
        "target_role": {"type": "string"},
        "skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string"},
                    "company": {"type": "string"},
                    "duration": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["role", "company"]
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "degree": {"type": "string"},
                    "institution": {"type": "string"},
                    "year": {"type": "string"}
                },
                "required": ["degree", "institution"]
            }
        }
    },
    "required": ["name", "skills", "experience", "education"]
}

PARSE_PROMPT = """You are a resume-parsing engine. Extract structured information from the resume text below.

Rules:
- Only extract information that is explicitly present in the text.
- If a field is missing, use an empty string "" or empty list [], never invent data.
- "target_role" should be the role the candidate appears to be seeking, inferred from their most recent experience or an explicit objective -- leave "" if unclear.
- Return ONLY valid JSON matching the schema. No markdown, no commentary.

Resume text:
---
{resume_text}
---
"""


def parse_resume(resume_text: str) -> dict:
    prompt = PARSE_PROMPT.format(resume_text=resume_text)

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RESUME_SCHEMA,
        ),
    )

    try:
        profile = json.loads(response.text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nRaw output: {response.text}")

    required_fields = ["name", "skills", "experience", "education"]
    missing = [f for f in required_fields if f not in profile]
    if missing:
        raise ValueError(f"Parsed profile is missing required fields: {missing}")

    return profile


if __name__ == "__main__":
    from src.parsing.loader import load_text
    from src import config

    resume_files = [
        f for f in config.RESUMES_DIR.glob("*")
        if f.suffix.lower() in (".pdf", ".docx", ".txt")
    ]

    if not resume_files:
        raise FileNotFoundError(
            f"No resume files found in {config.RESUMES_DIR} -- add a sample resume there first."
        )

    sample_path = resume_files[0]
    print(f"Parsing: {sample_path.name}\n")

    resume_text = load_text(sample_path)
    result = parse_resume(resume_text)
    print(json.dumps(result, indent=2))
