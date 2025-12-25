"""
📄 PDF Report Generator
=======================

Generates professional PDF reports from analysis data.

Author: MAHBUB
Date: December 25, 2024
"""

import streamlit as st
import sys
import os
from datetime import datetime
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import PROJECT_NAME, VERSION, AUTHOR


class ReportGenerator:
    """Generates PDF and text reports from analysis data."""
    
    def __init__(self):
        """Initialize report generator."""
        self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def render(self, context: dict = None):
        """
        Render the report generation interface.
        
        Args:
            context: Analysis data for report
        """
        st.markdown("## 📄 Export Reports")
        st.markdown("*Download professional reports of your analysis*")
        
        if not context or not any(context.values()):
            st.warning("⚠️ No analysis data available. Please run an analysis first.")
            return
        
        # Report options
        st.markdown("### 📋 Report Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_infra = st.checkbox("Include Infrastructure Analysis", value=True)
            include_equity = st.checkbox("Include Equity Analysis", value=True)
            include_access = st.checkbox("Include Accessibility Analysis", value=True)
        
        with col2:
            include_recommendations = st.checkbox("Include Recommendations", value=True)
            include_raw_data = st.checkbox("Include Raw Statistics", value=False)
        
        st.markdown("---")
        
        # Generate buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generate Text Report", use_container_width=True):
                report = self._generate_text_report(
                    context,
                    include_infra=include_infra,
                    include_equity=include_equity,
                    include_access=include_access,
                    include_recommendations=include_recommendations,
                    include_raw_data=include_raw_data
                )
                
                st.download_button(
                    label="⬇️ Download Text Report",
                    data=report,
                    file_name=f"evchargeadvisor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
                with st.expander("📖 Preview Report"):
                    st.text(report)
        
        with col2:
            if st.button("📊 Generate CSV Data", use_container_width=True):
                csv_data = self._generate_csv_data(context)
                
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"evchargeadvisor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col3:
            if st.button("📋 Generate Markdown", use_container_width=True):
                md_report = self._generate_markdown_report(
                    context,
                    include_infra=include_infra,
                    include_equity=include_equity,
                    include_access=include_access,
                    include_recommendations=include_recommendations
                )
                
                st.download_button(
                    label="⬇️ Download Markdown",
                    data=md_report,
                    file_name=f"evchargeadvisor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    
    def _generate_text_report(
        self,
        context: dict,
        include_infra: bool = True,
        include_equity: bool = True,
        include_access: bool = True,
        include_recommendations: bool = True,
        include_raw_data: bool = False
    ) -> str:
        """Generate plain text report."""
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"{PROJECT_NAME} - ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {self.generated_at}")
        lines.append(f"Version: {VERSION}")
        lines.append(f"Author: {AUTHOR}")
        lines.append("")
        
        # Location info
        infra = context.get("infrastructure", {})
        location = infra.get("location", {})
        lines.append(f"LOCATION: {location.get('name', 'Unknown')}")
        lines.append(f"Coordinates: ({location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')})")
        lines.append(f"Search Radius: {location.get('radius_km', 'N/A')} km")
        lines.append("")
        
        # Infrastructure section
        if include_infra and infra:
            lines.append("-" * 80)
            lines.append("INFRASTRUCTURE ANALYSIS")
            lines.append("-" * 80)
            
            summary = infra.get("summary", {})
            lines.append(f"Total Charging Stations: {summary.get('total_stations', 'N/A')}")
            lines.append(f"Total Connectors: {summary.get('total_connectors', 'N/A')}")
            lines.append(f"Fast Chargers (DC): {summary.get('fast_chargers', 'N/A')} ({summary.get('fast_charger_ratio', 0)}%)")
            lines.append(f"Unique Operators: {summary.get('unique_operators', 'N/A')}")
            lines.append(f"Operational Stations: {summary.get('operational_stations', 'N/A')}")
            lines.append("")
            
            coverage = infra.get("coverage", {})
            lines.append(f"Coverage Rating: {coverage.get('coverage_rating', 'N/A')}")
            lines.append(f"Station Density: {coverage.get('station_density', 'N/A')} per km²")
            lines.append("")
            
            # Top operators
            operators = infra.get("operators", {}).get("distribution", {})
            lines.append("Top Operators:")
            for name, data in list(operators.items())[:5]:
                stations = data.get("stations", data) if isinstance(data, dict) else data
                lines.append(f"  - {name}: {stations} stations")
            lines.append("")
        
        # Equity section
        equity = context.get("equity", {})
        if include_equity and equity and equity.get("status") == "success":
            lines.append("-" * 80)
            lines.append("EQUITY ANALYSIS")
            lines.append("-" * 80)
            
            lines.append(f"Data Source: {equity.get('data_source', 'N/A')}")
            lines.append("")
            
            demo = equity.get("demographics", {})
            lines.append("Demographics:")
            lines.append(f"  Population: {demo.get('population', 'N/A'):,}")
            lines.append(f"  Income per Capita: ${demo.get('income_per_capita', 0):,.0f}")
            lines.append(f"  Income Level: {demo.get('income_level', 'N/A')}")
            lines.append(f"  Poverty Rate: {demo.get('poverty_rate', 'N/A')}%")
            lines.append("")
            
            eq = equity.get("equity_assessment", {})
            lines.append(f"Equity Score: {eq.get('score', 'N/A')}/100")
            lines.append(f"Equity Grade: {eq.get('grade', 'N/A')} ({eq.get('rating', 'N/A')})")
            lines.append("")
            
            components = eq.get("components", {})
            lines.append("Component Scores:")
            for comp, score in components.items():
                lines.append(f"  - {comp.replace('_', ' ').title()}: {score}/100")
            lines.append("")
        
        # Accessibility section
        access = context.get("accessibility", {})
        if include_access and access and access.get("status") == "success":
            lines.append("-" * 80)
            lines.append("ACCESSIBILITY ANALYSIS")
            lines.append("-" * 80)
            
            summary = access.get("summary", {})
            lines.append(f"Average Convenience Score: {summary.get('avg_convenience_score', 'N/A')}/10")
            lines.append(f"Overall Grade: {summary.get('overall_grade', 'N/A')}")
            lines.append(f"Stations Analyzed: {summary.get('stations_analyzed', 'N/A')}")
            lines.append("")
            
            climate = access.get("climate_impact", {})
            if climate:
                lines.append("Climate Impact:")
                lines.append(f"  Temperature: {climate.get('current', {}).get('temperature', 'N/A')}°C")
                lines.append(f"  EV Range Factor: {climate.get('current', {}).get('range_percentage', 'N/A')}")
                lines.append(f"  Impact Level: {climate.get('impact', {}).get('level', 'N/A')}")
            lines.append("")
        
        # Recommendations
        if include_recommendations:
            recommendations = equity.get("recommendations", []) if equity else []
            if recommendations:
                lines.append("-" * 80)
                lines.append("RECOMMENDATIONS")
                lines.append("-" * 80)
                
                for i, rec in enumerate(recommendations, 1):
                    lines.append(f"{i}. [{rec.get('priority', 'N/A')}] {rec.get('category', 'N/A')}")
                    lines.append(f"   {rec.get('recommendation', 'N/A')}")
                    lines.append(f"   Rationale: {rec.get('rationale', 'N/A')}")
                    lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _generate_csv_data(self, context: dict) -> str:
        """Generate CSV data from analysis."""
        
        lines = []
        lines.append("Category,Metric,Value")
        
        # Infrastructure metrics
        infra = context.get("infrastructure", {})
        if infra:
            summary = infra.get("summary", {})
            lines.append(f"Infrastructure,Total Stations,{summary.get('total_stations', '')}")
            lines.append(f"Infrastructure,Total Connectors,{summary.get('total_connectors', '')}")
            lines.append(f"Infrastructure,Fast Chargers,{summary.get('fast_chargers', '')}")
            lines.append(f"Infrastructure,Unique Operators,{summary.get('unique_operators', '')}")
            
            coverage = infra.get("coverage", {})
            lines.append(f"Coverage,Rating,{coverage.get('coverage_rating', '')}")
            lines.append(f"Coverage,Station Density,{coverage.get('station_density', '')}")
        
        # Equity metrics
        equity = context.get("equity", {})
        if equity and equity.get("status") == "success":
            demo = equity.get("demographics", {})
            lines.append(f"Demographics,Population,{demo.get('population', '')}")
            lines.append(f"Demographics,Income per Capita,{demo.get('income_per_capita', '')}")
            lines.append(f"Demographics,Poverty Rate,{demo.get('poverty_rate', '')}")
            
            eq = equity.get("equity_assessment", {})
            lines.append(f"Equity,Score,{eq.get('score', '')}")
            lines.append(f"Equity,Grade,{eq.get('grade', '')}")
        
        # Accessibility metrics
        access = context.get("accessibility", {})
        if access and access.get("status") == "success":
            summary = access.get("summary", {})
            lines.append(f"Accessibility,Convenience Score,{summary.get('avg_convenience_score', '')}")
            lines.append(f"Accessibility,Overall Grade,{summary.get('overall_grade', '')}")
        
        return "\n".join(lines)
    
    def _generate_markdown_report(
        self,
        context: dict,
        include_infra: bool = True,
        include_equity: bool = True,
        include_access: bool = True,
        include_recommendations: bool = True
    ) -> str:
        """Generate Markdown report."""
        
        lines = []
        lines.append(f"# {PROJECT_NAME} Analysis Report")
        lines.append("")
        lines.append(f"**Generated:** {self.generated_at}")
        lines.append(f"**Version:** {VERSION}")
        lines.append(f"**Author:** {AUTHOR}")
        lines.append("")
        
        # Location
        infra = context.get("infrastructure", {})
        location = infra.get("location", {})
        lines.append(f"## 📍 Location: {location.get('name', 'Unknown')}")
        lines.append("")
        lines.append(f"- **Coordinates:** ({location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')})")
        lines.append(f"- **Search Radius:** {location.get('radius_km', 'N/A')} km")
        lines.append("")
        
        # Infrastructure
        if include_infra and infra:
            lines.append("## 🔌 Infrastructure Analysis")
            lines.append("")
            
            summary = infra.get("summary", {})
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Stations | {summary.get('total_stations', 'N/A')} |")
            lines.append(f"| Total Connectors | {summary.get('total_connectors', 'N/A')} |")
            lines.append(f"| Fast Chargers | {summary.get('fast_chargers', 'N/A')} |")
            lines.append(f"| Operators | {summary.get('unique_operators', 'N/A')} |")
            lines.append("")
        
        # Equity
        equity = context.get("equity", {})
        if include_equity and equity and equity.get("status") == "success":
            lines.append("## ⚖️ Equity Analysis")
            lines.append("")
            lines.append(f"**Data Source:** {equity.get('data_source', 'N/A')}")
            lines.append("")
            
            eq = equity.get("equity_assessment", {})
            lines.append(f"### Score: {eq.get('score', 'N/A')}/100 (Grade: {eq.get('grade', 'N/A')})")
            lines.append("")
        
        # Recommendations
        if include_recommendations:
            recommendations = equity.get("recommendations", []) if equity else []
            if recommendations:
                lines.append("## 💡 Recommendations")
                lines.append("")
                for i, rec in enumerate(recommendations, 1):
                    lines.append(f"{i}. **[{rec.get('priority', '')}] {rec.get('category', '')}**")
                    lines.append(f"   - {rec.get('recommendation', '')}")
                    lines.append("")
        
        lines.append("---")
        lines.append(f"*Report generated by {PROJECT_NAME} v{VERSION}*")
        
        return "\n".join(lines)


# Standalone test
if __name__ == "__main__":
    st.set_page_config(page_title="Report Generator Test", layout="wide")
    
    generator = ReportGenerator()
    
    # Test context
    test_context = {
        "infrastructure": {
            "location": {"name": "San Francisco, CA", "latitude": 37.7749, "longitude": -122.4194, "radius_km": 10},
            "summary": {
                "total_stations": 435,
                "total_connectors": 1856,
                "fast_chargers": 375,
                "fast_charger_ratio": 20.2,
                "unique_operators": 29,
                "operational_stations": 427
            },
            "coverage": {"coverage_rating": "Moderate", "station_density": 1.38},
            "operators": {"distribution": {"ChargePoint": {"stations": 195}, "Tesla": {"stations": 44}}}
        },
        "equity": {
            "status": "success",
            "data_source": "US Census Bureau",
            "demographics": {
                "population": 851036,
                "income_per_capita": 136689,
                "income_level": "High Income",
                "poverty_rate": 10.48
            },
            "equity_assessment": {
                "score": 90.0,
                "grade": "A",
                "rating": "Excellent",
                "components": {"access": 70.7, "affordability": 58.6, "mobility": 90.0}
            },
            "recommendations": [
                {"priority": "Standard", "category": "Community Engagement", "recommendation": "Engage community", "rationale": "Local needs"}
            ]
        },
        "accessibility": {
            "status": "success",
            "summary": {"avg_convenience_score": 10.0, "overall_grade": "A", "stations_analyzed": 5},
            "climate_impact": {"current": {"temperature": 12.5, "range_percentage": "93%"}, "impact": {"level": "Low"}}
        }
    }
    
    generator.render(test_context)