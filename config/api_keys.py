"""
🔑 API Keys Configuration
=========================

API keys are loaded from Streamlit secrets (cloud) or environment variables (local).

Author: MAHBUB
Date: December 25, 2024
"""

import os

# =============================================================================
# LOAD API KEYS SAFELY
# =============================================================================

def get_api_key(key_name):
    """Get API key from Streamlit secrets or environment."""
    
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'api_keys' in st.secrets:
            return st.secrets["api_keys"].get(key_name, "")
    except:
        pass
    
    # Try environment variables
    env_map = {
        "openchargemap": "OPENCHARGEMAP_API_KEY",
        "census": "CENSUS_API_KEY", 
        "groq": "GROQ_API_KEY"
    }
    return os.environ.get(env_map.get(key_name, ""), "")


API_KEYS = {
    "openchargemap": get_api_key("openchargemap"),
    "census": get_api_key("census"),
    "groq": get_api_key("groq")
}

API_CONFIGS = {
    "openchargemap": {
        "base_url": "https://api.openchargemap.io/v3",
        "api_key": API_KEYS["openchargemap"]
    },
    "census": {
        "base_url": "https://api.census.gov/data",
        "api_key": API_KEYS["census"]
    },
    "overpass": {
        "base_url": "https://overpass-api.de/api/interpreter",
        "api_key": None
    },
    "openmeteo": {
        "base_url": "https://api.open-meteo.com/v1",
        "api_key": None
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": API_KEYS["groq"]
    }
}

if __name__ == "__main__":
    print("🔑 API Keys Status:")
    for name, key in API_KEYS.items():
        status = "✅ Set" if key else "❌ Not set"
        print(f"   {name}: {status}")