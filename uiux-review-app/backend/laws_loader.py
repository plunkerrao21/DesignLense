import json
import os
from pathlib import Path

def load_laws():
    """Load UI/UX laws from shared/laws.json"""
    try:
        # Get the directory of this file
        current_dir = Path(__file__).parent
        # Navigate to shared directory
        laws_path = current_dir.parent / "shared" / "laws.json"
        
        with open(laws_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: laws.json not found at {laws_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing laws.json: {e}")
        return {}
