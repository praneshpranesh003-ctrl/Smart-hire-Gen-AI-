"""Prompt library — every prompt the project uses lives here, not scattered in code.

Keep each prompt as a named string (or LangChain PromptTemplate) so you can edit
and compare versions in one place. The evaluation report asks for at least one
before/after prompt comparison, so keeping them here makes that easy.

Prompts to write:
    RESUME_PARSE_PROMPT   -> resume text in, strict JSON profile out
    CV_SUGGESTIONS_PROMPT -> resume + target job in, improvement suggestions out
    MENTOR_SYSTEM_PROMPT  -> the "answer only from the context" instruction for RAG
"""
