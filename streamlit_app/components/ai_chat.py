"""
💬 AI Chat Component
====================

Interactive AI chat for asking questions about EV charging data.

Author: MAHBUB
Date: December 25, 2024
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_access.groq_api import GroqAPIClient


class AIChat:
    """Interactive AI chat for EV charging analysis."""
    
    def __init__(self):
        """Initialize chat component."""
        self.llm_client = GroqAPIClient()
        
        # Initialize chat history in session state
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
    
    def render(self, context: dict = None):
        """
        Render the chat interface.
        
        Args:
            context: Analysis data to provide context for AI
        """
        st.markdown("## 💬 AI Assistant")
        st.markdown("*Ask questions about your EV charging analysis*")
        
        # Chat container
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about EV charging infrastructure..."):
            # Add user message
            st.session_state.chat_messages.append({
                "role": "user",
                "content": prompt
            })
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = self._generate_response(prompt, context)
                        st.markdown(response)
            
            # Add assistant message
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response
            })
        
        # Clear chat button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
        
        # Quick questions
        st.markdown("### 💡 Quick Questions")
        
        quick_questions = [
            "What are the main infrastructure gaps?",
            "How does equity compare to other cities?",
            "What policy recommendations do you suggest?",
            "Which operators dominate the market?",
            "How does weather affect EV range here?"
        ]
        
        cols = st.columns(3)
        for i, question in enumerate(quick_questions[:3]):
            with cols[i]:
                if st.button(f"❓ {question[:30]}...", key=f"q_{i}", use_container_width=True):
                    self._ask_question(question, context, chat_container)
    
    def _generate_response(self, prompt: str, context: dict = None) -> str:
        """Generate AI response with context."""
        
        # Build context string
        context_str = self._build_context_string(context)
        
        system_prompt = f"""You are an expert AI assistant for EVChargeAdvisor-AI, 
a global EV charging infrastructure equity analysis tool.

You have access to the following analysis data:
{context_str}

Guidelines:
- Answer questions based on the available data
- Be specific with numbers and statistics when available
- Provide actionable insights and recommendations
- If data is not available, acknowledge limitations
- Be concise but comprehensive
- Use markdown formatting for clarity"""

        return self.llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
    
    def _build_context_string(self, context: dict) -> str:
        """Build context string from analysis data."""
        if not context:
            return "No analysis data available yet. Please run an analysis first."
        
        parts = []
        
        # Infrastructure context
        if context.get("infrastructure"):
            infra = context["infrastructure"]
            summary = infra.get("summary", {})
            parts.append(f"""
INFRASTRUCTURE DATA:
- Location: {infra.get('location', {}).get('name', 'Unknown')}
- Total Stations: {summary.get('total_stations', 'N/A')}
- Total Connectors: {summary.get('total_connectors', 'N/A')}
- Fast Chargers: {summary.get('fast_chargers', 'N/A')}
- Operators: {summary.get('unique_operators', 'N/A')}
- Coverage Rating: {infra.get('coverage', {}).get('coverage_rating', 'N/A')}
""")
        
        # Equity context
        if context.get("equity"):
            equity = context["equity"]
            demo = equity.get("demographics", {})
            eq = equity.get("equity_assessment", {})
            parts.append(f"""
EQUITY DATA:
- Data Source: {equity.get('data_source', 'N/A')}
- Population: {demo.get('population', 'N/A')}
- Income Level: {demo.get('income_level', 'N/A')}
- Poverty Rate: {demo.get('poverty_rate', 'N/A')}%
- Equity Score: {eq.get('score', 'N/A')}/100
- Equity Grade: {eq.get('grade', 'N/A')}
""")
        
        # Accessibility context
        if context.get("accessibility"):
            access = context["accessibility"]
            summary = access.get("summary", {})
            parts.append(f"""
ACCESSIBILITY DATA:
- Average Convenience Score: {summary.get('avg_convenience_score', 'N/A')}/10
- Overall Grade: {summary.get('overall_grade', 'N/A')}
- Stations Analyzed: {summary.get('stations_analyzed', 'N/A')}
""")
        
        return "\n".join(parts) if parts else "No analysis data available."
    
    def _ask_question(self, question: str, context: dict, container):
        """Process a quick question."""
        st.session_state.chat_messages.append({
            "role": "user",
            "content": question
        })
        
        response = self._generate_response(question, context)
        
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })
        
        st.rerun()


# Standalone test
if __name__ == "__main__":
    st.set_page_config(page_title="AI Chat Test", layout="wide")
    
    chat = AIChat()
    
    # Test context
    test_context = {
        "infrastructure": {
            "location": {"name": "San Francisco, CA"},
            "summary": {
                "total_stations": 435,
                "total_connectors": 1856,
                "fast_chargers": 375,
                "unique_operators": 29
            },
            "coverage": {"coverage_rating": "Moderate"}
        },
        "equity": {
            "data_source": "US Census Bureau",
            "demographics": {
                "population": 851036,
                "income_level": "High Income",
                "poverty_rate": 10.48
            },
            "equity_assessment": {
                "score": 90.0,
                "grade": "A"
            }
        }
    }
    
    chat.render(test_context)