import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("🎬 Movie Explorer")

# Initialize session state
if "movie" not in st.session_state:
    st.session_state.movie = None
if "summary" not in st.session_state:
    st.session_state.summary = None

# Fetch a random movie
if st.button("Show Random Movie"):
    try:
        resp = requests.get(f"{API_URL}/movies/random/")
        resp.raise_for_status()
        st.session_state.movie = resp.json()
        st.session_state.summary = None
    except Exception as e:
        st.error(f"Error fetching movie: {e}")

# Display movie details
if st.session_state.movie:
    m = st.session_state.movie
    st.header(f"{m['title']} ({m['year']})")
    st.write(f"**Director:** {m['director']}")
    st.write("**Actors:**")
    for actor in m["actors"]:
        st.write(f"- {actor['actor_name']}")

    # Request summary
    if st.button("Get Summary"):
        try:
            resp = requests.post(f"{API_URL}/generate_summary/", json={"movie_id": m["id"]})
            resp.raise_for_status()
            st.session_state.summary = resp.json()["summary_text"]
        except Exception as e:
            st.error(f"Error generating summary: {e}")

# Display summary
if st.session_state.summary:
    st.info(st.session_state.summary)
