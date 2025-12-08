import streamlit as st
from datetime import datetime
import sys
import os

# Add src to path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src import storage, llm, auth

# --- Page Config ---
st.set_page_config(
    page_title="My Health Companion",
    page_icon="🩺",
    layout="wide"
)

# --- Custom CSS for "Premium" Feel ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        font-family: 'Inter', sans-serif;
        color: #1E3A8A; /* Dark Blue */
        font-weight: 700;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar & Navigation ---
with st.sidebar:
    st.title("🩺 Health Companion")
    
    # API Key Handling
    api_key = auth.get_api_key()
    if not api_key:
        st.error("Missing API Key")
        st.caption("Set GEMINI_API_KEY in environment.")
            
    st.markdown("---")
    page = st.radio("Navigation", ["Dashboard", "Medical Profile", "Log Consultation", "AI Assistant"])

# --- Main App Logic ---

if page == "Dashboard":
    st.markdown("<h1 class='main-header'>Health Dashboard</h1>", unsafe_allow_html=True)
    
    profile = storage.load_profile()
    consultations = storage.load_consultations()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>Patient Profile</h3>
            <p><strong>Name:</strong> {}</p>
            <p><strong>Allergies:</strong> {}</p>
            <p><strong>Meds:</strong> {}</p>
        </div>
        """.format(
            profile.get('name', 'Not set'),
            len(profile.get('allergies', [])),
            len(profile.get('current_medications', []))
        ), unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>Consultations</h3>
            <p><strong>Total Logs:</strong> {}</p>
            <p><strong>Last Visit:</strong> {}</p>
        </div>
        """.format(
            len(consultations),
            consultations[-1]['date'] if consultations else "None"
        ), unsafe_allow_html=True)
        
    st.info("Welcome back. Use the sidebar to update your profile or chat with the assistant.")

elif page == "Medical Profile":
    st.markdown("<h1 class='main-header'>My Medical Profile</h1>", unsafe_allow_html=True)
    
    profile = storage.load_profile()
    
    with st.form("profile_form"):
        name = st.text_input("Full Name", value=profile.get("name", ""))
        dob = st.date_input("Date of Birth", value=datetime.strptime(profile.get("dob"), "%Y-%m-%d") if profile.get("dob") else None)
        
        st.subheader("Allergies & Reactions")
        allergies_str = st.text_area("List allergies (comma separated)", value=", ".join(profile.get("allergies", [])))
        
        st.subheader("Current Medications")
        meds_str = st.text_area("List medications (comma separated)", value=", ".join(profile.get("current_medications", [])))
        
        st.subheader("Medical History")
        history = st.text_area("Chronic conditions, past surgeries, etc.", value=profile.get("medical_history", ""))
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            new_profile = {
                "name": name,
                "dob": str(dob) if dob else "",
                "allergies": [x.strip() for x in allergies_str.split(",") if x.strip()],
                "current_medications": [x.strip() for x in meds_str.split(",") if x.strip()],
                "medical_history": history
            }
            storage.save_profile(new_profile)
            st.success("Profile updated successfully!")

elif page == "Log Consultation":
    st.markdown("<h1 class='main-header'>Log New Consultation</h1>", unsafe_allow_html=True)
    
    with st.form("consult_form"):
        date_visit = st.date_input("Date of Visit", value=datetime.today())
        provider = st.text_input("Provider Name (e.g. Dr. Smith)")
        notes = st.text_area("Consultation Notes (Key takeaways, vitals, advice)")
        
        submitted = st.form_submit_button("Save Log")
        
        if submitted:
            if not provider or not notes:
                st.error("Please fill in provider and notes.")
            else:
                consultation = {
                    "date": str(date_visit),
                    "provider": provider,
                    "notes": notes,
                    "timestamp": str(datetime.now())
                }
                storage.add_consultation(consultation)
                st.success("Consultation logged successfully!")

elif page == "AI Assistant":
    st.markdown("<h1 class='main-header'>Medical Assistant</h1>", unsafe_allow_html=True)
    
    if not api_key:
        st.warning("⚠️ API Key not found. Please set `GEMINI_API_KEY` in your environment variables or `.env` file.")
    else:
        llm.configure_gemini(api_key)
        profile = storage.load_profile()
        consultations = storage.load_consultations()
        
        # Display Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat Input
        if prompt := st.chat_input("Ask about your health, medications, or past visits..."):
            # Add user message to state
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate Response
            with st.spinner("Analyzing profile & generating response..."):
                response_text = llm.get_medical_response(
                    query=prompt,
                    profile=profile,
                    consultations=consultations,
                    chat_history=st.session_state.messages
                )
            
            # Add assistant message to state
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)

