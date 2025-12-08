import google.generativeai as genai
import os
from typing import List, Dict, Any

def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)

def get_medical_response(
    query: str, 
    profile: Dict[str, Any], 
    consultations: List[Dict[str, Any]],
    chat_history: List[Dict[str, str]] = []
) -> str:
    """
    Generates a response from the "Medical Expert" persona, taking into account
    the user's profile (allergies, meds) and past consultations.
    """
    
    # 1. Build Context
    # Format Profile
    profile_text = f"""
    PATIENT PROFILE:
    Name: {profile.get('name', 'N/A')}
    Date of Birth: {profile.get('dob', 'N/A')}
    Allergies: {', '.join(profile.get('allergies', [])) if profile.get('allergies') else 'None listed'}
    Current Medications: {', '.join(profile.get('current_medications', [])) if profile.get('current_medications') else 'None listed'}
    Medical History: {profile.get('medical_history', 'None listed')}
    """

    # Format Recent Consultations (Last 3 for brevity in context)
    recent_consults = consultations[-3:]
    consults_text = "RECENT CONSULTATIONS:\n"
    if not recent_consults:
        consults_text += "No recent consultations logged.\n"
    else:
        for c in recent_consults:
            consults_text += f"- Date: {c.get('date')}, Provider: {c.get('provider')}\n  Notes: {c.get('notes')}\n"

    # 2. System Prompt
    system_prompt = f"""
    You are an AI Medical Companion and Assistant. 
    Your goal is to help the user manage their health, prepare for doctor visits, and understand their medical data.
    
    CRITICAL INSTRUCTION: You MUST take the patient's specific profile (Allergies, Medications, History) into account.
    If the user asks about a new medication, CHECK against their known allergies and current medications for potential interactions.
    
    DISCLAIMER: You are an AI, not a doctor. Always advise the user to consult a professional for serious medical decisions.
    
    CONTEXT:
    {profile_text}
    
    {consults_text}
    """

    # 3. Model Interaction
    # We use a generative model. 
    # Valid models: gemini-1.5-flash, gemini-1.5-pro, gemini-pro (older)
    # Start a chat session or just generate content. For simple turn-based RAG, generate_content is often easiest, 
    # but 'start_chat' manages history better if we were passing the object around. 
    # Here we are stateless per request for simplicity, re-injecting history manually or just relying on the query context.
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Construct the full prompt including history if provided (simplified for this prototype)
    messages = [
        {'role': 'model', 'parts': [system_prompt]}
    ]
    
    # Add chat history to the prompt context if needed, or just append to the prompt.
    # For robust chat, we usually map 'user'/'assistant' roles.
    chat_context = ""
    for msg in chat_history:
        role = "User" if msg['role'] == 'user' else "Assistant"
        chat_context += f"{role}: {msg['content']}\n"
        
    final_prompt = f"{system_prompt}\n\nCHAT HISTORY:\n{chat_context}\n\nUser: {query}\nAssistant:"

    try:
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"Error contacting Gemini: {str(e)}"
