"""SmartHire GenAI portal (Streamlit). Run: streamlit run app/streamlit_app.py

Build this LAST. It only wires together pieces that already work in src/:
    upload CV -> parsed profile -> matched jobs -> CV suggestions -> mentor chat.
Cache the FAISS index / chain with @st.cache_resource so it is not rebuilt on every
interaction, and read the API key from st.secrets (not the .env file) once deployed.
"""
