import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in project root (one level up from src/)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_api_key():
    """
    Retrieves the API Key from secrets, environment variables, or session state.
    Checks both GOOGLE_API_KEY and GEMINI_API_KEY.
    """
    # Check Streamlit secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except FileNotFoundError:
        # secrets.toml not found, just continue to environment variables
        pass
    except Exception:
        # Catch other streamlit secret errors (like StreamlitSecretNotFoundError)
        pass
        
    # Check Environment Variables
    if os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY")
    if os.getenv("GOOGLE_API_KEY"):
        return os.getenv("GOOGLE_API_KEY")
        
    # Check Session State
    if "api_key" in st.session_state:
        return st.session_state.api_key
        
    return None
