"""Module 5 — Guardrails.

Your own validation code that runs BEFORE every LLM call — not the model itself.
Reject empty, too-short, or too-long input, and block off-topic or unsafe requests
and prompt-injection phrases. This is the validate_question() pattern from the
guardrails session: return (ok, message) and only call the model when ok is True.
"""
