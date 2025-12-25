"""
🤖 Groq LLM API Client
======================

AI-powered analysis using Groq's fast LLM inference.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional, Generator

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_access.base_api import BaseAPIClient, APIError
from config.api_keys import API_CONFIGS
from config.settings import LLM_SETTINGS


class GroqAPIClient(BaseAPIClient):
    """
    Client for Groq LLM API.
    
    Groq provides ultra-fast inference for LLMs like Llama.
    Used for generating insights and recommendations.
    """
    
    def __init__(self):
        """Initialize Groq API client."""
        config = API_CONFIGS["groq"]
        super().__init__(
            base_url=config["base_url"],
            api_key=config["api_key"]
        )
        self.model = LLM_SETTINGS["model"]
        self.temperature = LLM_SETTINGS["temperature"]
        self.max_tokens = LLM_SETTINGS["max_tokens"]
    
    def _add_auth_params(self, params: Dict) -> Dict:
        """Not used - auth is in headers."""
        return params
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        headers = super()._get_default_headers()
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    # =========================================================================
    # MAIN METHODS
    # =========================================================================
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }
        
        try:
            response = self.post("chat/completions", data=payload, use_cache=False)
            
            choices = response.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
            
        except APIError as e:
            print(f"❌ Groq API Error: {e.message}")
            return ""
        except Exception as e:
            print(f"❌ Groq API Error: {e}")
            return ""
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Multi-turn chat completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            
        Returns:
            Assistant's response
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }
        
        try:
            response = self.post("chat/completions", data=payload, use_cache=False)
            
            choices = response.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
            
        except Exception as e:
            print(f"❌ Groq API Error: {e}")
            return ""
    
    # =========================================================================
    # EV CHARGING ANALYSIS METHODS
    # =========================================================================
    
    def analyze_infrastructure(self, data: Dict[str, Any]) -> str:
        """
        Analyze EV charging infrastructure data.
        
        Args:
            data: Dictionary containing station statistics
            
        Returns:
            Analysis text
        """
        system_prompt = """You are an expert EV charging infrastructure analyst. 
Analyze the provided data and give clear, actionable insights.
Focus on:
1. Coverage adequacy
2. Infrastructure gaps
3. Operator diversity
4. Charging speed distribution
Be concise but comprehensive. Use bullet points for key findings."""

        prompt = f"""Analyze this EV charging infrastructure data:

Total Stations: {data.get('total_stations', 'N/A')}
Total Connectors: {data.get('total_connectors', 'N/A')}
Fast Chargers: {data.get('fast_chargers', 'N/A')}
Operators: {data.get('operators', {})}
Power Statistics: {data.get('power_stats', {})}

Location: {data.get('location', 'Unknown')}
Search Radius: {data.get('radius_km', 'N/A')} km

Provide a brief analysis with key findings and recommendations."""

        return self.generate(prompt, system_prompt, temperature=0.5)
    
    def analyze_equity(self, data: Dict[str, Any]) -> str:
        """
        Analyze equity in EV charging access.
        
        Args:
            data: Dictionary with demographic and infrastructure data
            
        Returns:
            Equity analysis text
        """
        system_prompt = """You are an expert in transportation equity and urban planning.
Analyze EV charging infrastructure equity based on demographic data.
Consider:
1. Income-based disparities in charging access
2. Underserved communities
3. Vehicle ownership patterns
4. Recommendations for equitable expansion
Be data-driven and provide actionable policy recommendations."""

        prompt = f"""Analyze EV charging equity for this area:

Demographics:
- Population: {data.get('population', 'N/A'):,}
- Median Income: ${data.get('median_income', 'N/A'):,}
- Poverty Rate: {data.get('poverty_rate', 'N/A')}%
- No Vehicle Households: {data.get('no_vehicle_rate', 'N/A')}%

Infrastructure:
- Charging Stations: {data.get('stations', 'N/A')}
- Stations per 1,000 people: {data.get('stations_per_1000', 'N/A')}

Location: {data.get('location', 'Unknown')}

Assess equity and provide recommendations for improving access."""

        return self.generate(prompt, system_prompt, temperature=0.5)
    
    def generate_recommendations(
        self,
        infrastructure_data: Dict,
        equity_data: Dict,
        climate_data: Dict = None
    ) -> str:
        """
        Generate comprehensive policy recommendations.
        
        Args:
            infrastructure_data: Station statistics
            equity_data: Demographic data
            climate_data: Optional weather/climate data
            
        Returns:
            Policy recommendations
        """
        system_prompt = """You are a senior policy advisor specializing in sustainable transportation.
Generate actionable policy recommendations for EV charging infrastructure.
Consider infrastructure coverage, equity, and climate factors.
Prioritize recommendations by impact and feasibility.
Format as numbered recommendations with brief justifications."""

        climate_info = ""
        if climate_data:
            climate_info = f"""
Climate Factors:
- Average Temperature: {climate_data.get('avg_temperature', 'N/A')}°C
- EV Range Impact: {climate_data.get('range_factor', 'N/A')}
- Climate Challenge: {climate_data.get('impact_level', 'N/A')}
"""

        prompt = f"""Generate policy recommendations based on this analysis:

INFRASTRUCTURE:
- Total Stations: {infrastructure_data.get('total_stations', 'N/A')}
- Fast Chargers: {infrastructure_data.get('fast_chargers', 'N/A')}
- Coverage Gaps: {infrastructure_data.get('gaps', 'Unknown')}

EQUITY:
- Median Income: ${equity_data.get('median_income', 'N/A'):,}
- Poverty Rate: {equity_data.get('poverty_rate', 'N/A')}%
- Stations per 1,000: {equity_data.get('stations_per_1000', 'N/A')}
{climate_info}
Location: {infrastructure_data.get('location', 'Unknown')}

Provide 5 prioritized policy recommendations with implementation notes."""

        return self.generate(prompt, system_prompt, temperature=0.6)
    
    def answer_question(
        self,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Answer a user question about the data.
        
        Args:
            question: User's question
            context: Relevant data context
            
        Returns:
            Answer text
        """
        system_prompt = """You are an AI assistant for EVChargeAdvisor-AI, 
a tool for analyzing EV charging infrastructure equity and accessibility.
Answer questions based on the provided data context.
Be helpful, accurate, and concise.
If data is insufficient, acknowledge limitations."""

        prompt = f"""Context Data:
{self._format_context(context)}

User Question: {question}

Please provide a helpful answer based on the available data."""

        return self.generate(prompt, system_prompt, temperature=0.7)
    
    def summarize_analysis(
        self,
        full_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate executive summary of full analysis.
        
        Args:
            full_analysis: Complete analysis results
            
        Returns:
            Executive summary
        """
        system_prompt = """You are writing an executive summary for urban planners.
Be concise (3-4 paragraphs max).
Highlight key findings, critical gaps, and top recommendations.
Use professional but accessible language."""

        prompt = f"""Summarize this EV charging infrastructure analysis:

{self._format_context(full_analysis)}

Write a concise executive summary suitable for policy makers."""

        return self.generate(prompt, system_prompt, temperature=0.5, max_tokens=500)
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _format_context(self, data: Dict, indent: int = 0) -> str:
        """Format dictionary as readable text."""
        lines = []
        prefix = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_context(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}: {len(value)} items")
            else:
                lines.append(f"{prefix}{key}: {value}")
        
        return "\n".join(lines)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model configuration."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "base_url": self.base_url
        }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🤖 Groq LLM API Client")
    print("=" * 60)
    
    # Initialize client
    client = GroqAPIClient()
    print(f"✅ Client initialized")
    print(f"   Model: {client.model}")
    
    # Test: Simple generation
    print("\n📍 Testing simple generation...")
    response = client.generate(
        prompt="What are 3 key benefits of EV charging infrastructure? Be brief.",
        temperature=0.5,
        max_tokens=200
    )
    
    if response:
        print(f"✅ Response received:")
        print(f"   {response[:300]}...")
    else:
        print("❌ No response received")
    
    # Test: Infrastructure analysis
    print("\n📍 Testing infrastructure analysis...")
    test_data = {
        "total_stations": 50,
        "total_connectors": 169,
        "fast_chargers": 15,
        "operators": {"ChargePoint": 20, "Tesla": 15, "EVgo": 10, "Other": 5},
        "power_stats": {"min_kw": 3.7, "max_kw": 150, "avg_kw": 22},
        "location": "San Francisco, CA",
        "radius_km": 10
    }
    
    analysis = client.analyze_infrastructure(test_data)
    
    if analysis:
        print(f"✅ Infrastructure Analysis:")
        print(f"   {analysis[:400]}...")
    else:
        print("❌ Analysis failed")
    
    # Test: Equity analysis
    print("\n📍 Testing equity analysis...")
    equity_data = {
        "population": 851036,
        "median_income": 136689,
        "poverty_rate": 10.48,
        "no_vehicle_rate": 4.12,
        "stations": 50,
        "stations_per_1000": 0.06,
        "location": "San Francisco, CA"
    }
    
    equity_analysis = client.analyze_equity(equity_data)
    
    if equity_analysis:
        print(f"✅ Equity Analysis:")
        print(f"   {equity_analysis[:400]}...")
    else:
        print("❌ Equity analysis failed")
    
    # Show stats
    print("\n📈 Client Stats:")
    print(f"   {client.get_stats()}")