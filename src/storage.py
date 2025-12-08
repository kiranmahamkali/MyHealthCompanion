import json
import os
from typing import Dict, List, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
PROFILE_FILE = os.path.join(DATA_DIR, 'profile.json')
CONSULTATIONS_FILE = os.path.join(DATA_DIR, 'consultations.json')

def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_profile() -> Dict[str, Any]:
    _ensure_data_dir()
    if not os.path.exists(PROFILE_FILE):
        return {
            "name": "",
            "dob": "",
            "allergies": [],
            "current_medications": [],
            "medical_history": ""
        }
    with open(PROFILE_FILE, 'r') as f:
        return json.load(f)

def save_profile(profile_data: Dict[str, Any]):
    _ensure_data_dir()
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile_data, f, indent=4)

def load_consultations() -> List[Dict[str, Any]]:
    _ensure_data_dir()
    if not os.path.exists(CONSULTATIONS_FILE):
        return []
    with open(CONSULTATIONS_FILE, 'r') as f:
        return json.load(f)

def add_consultation(consultation: Dict[str, Any]):
    _ensure_data_dir()
    consultations = load_consultations()
    consultations.append(consultation)
    with open(CONSULTATIONS_FILE, 'w') as f:
        json.dump(consultations, f, indent=4)
