"""
🔑 API Keys Configuration Template
===================================

Copy this file to api_keys.py and fill in your API keys.

DO NOT commit api_keys.py to version control!
"""

# =============================================================================
# API KEYS - Replace with your own keys
# =============================================================================

API_KEYS = {
    "openchargemap": "YOUR_OPENCHARGEMAP_API_KEY",  # Get from: https://openchargemap.org/site/developerinfo
    "census": "YOUR_CENSUS_API_KEY",                 # Get from: https://api.census.gov/data/key_signup.html
    "groq": "YOUR_GROQ_API_KEY"                      # Get from: https://console.groq.com/
}

# =============================================================================
# API BASE URLS (Don't change these)
# =============================================================================

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

def test_config():
    """Test that API keys are configured."""
    print("⚠️ Please configure your API keys in config/api_keys.py")
    print("   Copy this template and add your keys.")

if __name__ == "__main__":
    test_config()