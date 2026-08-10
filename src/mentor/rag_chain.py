"""Module 4 — AI Career Mentor (RAG).

A LangChain pipeline that answers career questions grounded in the career-notes
FAISS index (config.NOTES_INDEX_DIR): retrieve the top-K relevant chunks, stuff them
into the mentor prompt, and generate an answer that sticks to the documents. The
mentor must say "I don't know" when the answer is not in the notes. Prototype the
chain in notebook 03, then move it here.
"""
