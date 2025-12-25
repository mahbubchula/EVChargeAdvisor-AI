"""
📊 Chart Generator
==================

Creates charts and visualizations for EV charging analysis.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import CHART_COLORS


class ChartGenerator:
    """
    Creates interactive charts for EV charging visualization.
    
    Chart types:
    - Operator distribution (pie/bar)
    - Charging level distribution
    - Equity scatter plots
    - Coverage metrics
    - Time series (if data available)
    """
    
    def __init__(self):
        """Initialize chart generator."""
        self.colors = CHART_COLORS
        self.template = "plotly_white"
        
        # Color palette for charts
        self.palette = [
            "#3b82f6", "#10b981", "#f59e0b", "#ef4444", 
            "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16"
        ]
    
    # =========================================================================
    # OPERATOR CHARTS
    # =========================================================================
    
    def create_operator_pie_chart(
        self,
        operators: Dict[str, Any],
        title: str = "Charging Stations by Operator"
    ) -> go.Figure:
        """
        Create pie chart of operator distribution.
        
        Args:
            operators: Dictionary with operator data
            title: Chart title
            
        Returns:
            Plotly figure
        """
        # Extract data
        names = list(operators.keys())[:10]  # Top 10
        values = [operators[n].get("stations", operators[n]) if isinstance(operators[n], dict) else operators[n] for n in names]
        
        fig = go.Figure(data=[go.Pie(
            labels=names,
            values=values,
            hole=0.4,
            marker_colors=self.palette[:len(names)],
            textinfo="percent+label",
            textposition="outside"
        )])
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=18)),
            template=self.template,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            height=450
        )
        
        return fig
    
    def create_operator_bar_chart(
        self,
        operators: Dict[str, Any],
        title: str = "Top Operators by Station Count"
    ) -> go.Figure:
        """
        Create horizontal bar chart of operators.
        
        Args:
            operators: Dictionary with operator data
            title: Chart title
            
        Returns:
            Plotly figure
        """
        # Sort and get top 10
        sorted_ops = sorted(
            operators.items(),
            key=lambda x: x[1].get("stations", x[1]) if isinstance(x[1], dict) else x[1],
            reverse=True
        )[:10]
        
        names = [op[0] for op in sorted_ops]
        values = [op[1].get("stations", op[1]) if isinstance(op[1], dict) else op[1] for op in sorted_ops]
        
        # Reverse for horizontal bar (top at top)
        names.reverse()
        values.reverse()
        
        fig = go.Figure(data=[go.Bar(
            x=values,
            y=names,
            orientation='h',
            marker_color=self.colors["primary"],
            text=values,
            textposition="outside"
        )])
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=18)),
            template=self.template,
            xaxis_title="Number of Stations",
            yaxis_title="",
            height=400,
            margin=dict(l=150)
        )
        
        return fig
    
    # =========================================================================
    # CHARGING LEVEL CHARTS
    # =========================================================================
    
    def create_charging_level_chart(
        self,
        levels: Dict[str, Any],
        title: str = "Connectors by Charging Level"
    ) -> go.Figure:
        """
        Create bar chart of charging level distribution.
        
        Args:
            levels: Dictionary with level distribution data
            title: Chart title
            
        Returns:
            Plotly figure
        """
        distribution = levels.get("distribution", levels)
        
        names = list(distribution.keys())
        values = [distribution[n].get("count", 0) if isinstance(distribution[n], dict) else distribution[n] for n in names]
        
        # Color by level
        colors = ["#94a3b8", "#3b82f6", "#10b981", "#f59e0b"]
        
        fig = go.Figure(data=[go.Bar(
            x=names,
            y=values,
            marker_color=colors[:len(names)],
            text=values,
            textposition="outside"
        )])
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=18)),
            template=self.template,
            xaxis_title="Charging Level",
            yaxis_title="Number of Connectors",
            height=400
        )
        
        return fig
    
    def create_power_distribution_chart(
        self,
        stations: List[Dict],
        title: str = "Power Distribution (kW)"
    ) -> go.Figure:
        """
        Create histogram of power distribution.
        
        Args:
            stations: List of station dictionaries
            title: Chart title
            
        Returns:
            Plotly figure
        """
        powers = [s.get("total_power_kw", 0) for s in stations if s.get("total_power_kw")]
        
        fig = go.Figure(data=[go.Histogram(
            x=powers,
            nbinsx=20,
            marker_color=self.colors["primary"]
        )])
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=18)),
            template=self.template,
            xaxis_title="Power (kW)",
            yaxis_title="Number of Stations",
            height=400
        )
        
        return fig
    
    # =========================================================================
    # EQUITY CHARTS
    # =========================================================================
    
    def create_equity_gauge(
        self,
        score: float,
        title: str = "Equity Score"
    ) -> go.Figure:
        """
        Create gauge chart for equity score.
        
        Args:
            score: Equity score (0-100)
            title: Chart title
            
        Returns:
            Plotly figure
        """
        # Determine color based on score
        if score >= 70:
            color = "#10b981"  # Green
        elif score >= 50:
            color = "#f59e0b"  # Orange
        else:
            color = "#ef4444"  # Red
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': '#fee2e2'},
                    {'range': [40, 70], 'color': '#fef3c7'},
                    {'range': [70, 100], 'color': '#d1fae5'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig
    
    def create_equity_components_chart(
        self,
        components: Dict[str, float],
        title: str = "Equity Score Components"
    ) -> go.Figure:
        """
        Create radar chart for equity components.
        
        Args:
            components: Dictionary of component scores
            title: Chart title
            
        Returns:
            Plotly figure
        """
        categories = list(components.keys())
        values = list(components.values())
        
        # Close the radar chart
        categories.append(categories[0])
        values.append(values[0])
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            marker_color=self.colors["primary"],
            line_color=self.colors["primary"]
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title=dict(text=title, x=0.5, font=dict(size=18)),
            showlegend=False,
            height=400
        )
        
        return fig
    
    def create_income_vs_access_scatter(
        self,
        data: List[Dict],
        title: str = "Income vs. Charging Access"
    ) -> go.Figure:
        """
        Create scatter plot of income vs. charging access.
        
        Args:
            data: List of dictionaries with income and access data
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if not data:
            # Return empty figure
            return go.Figure()
        
        incomes = [d.get("median_income", 0) for d in data]
        access = [d.get("stations_per_1000", 0) for d in data]
        names = [d.get("name", "Unknown") for d in data]
        populations = [d.get("population", 1000) for d in data]
        
        fig = go.Figure(data=go.Scatter(
            x=incomes,
            y=access,
            mode='markers',
            marker=dict(
                size=[max(10, min(50, p / 10000)) for p in populations],
                color=access,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Stations/1000")
            ),
            text=names,
            hovertemplate="<b>%{text}</b><br>" +
                          "Income: $%{x:,.0f}<br>" +
                          "Stations/1000: %{y:.3f}<br>" +
                          "<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=18)),
            template=self.template,
            xaxis_title="Median Household Income ($)",
            yaxis_title="Stations per 1,000 People",
            height=450
        )
        
        return fig
    
    # =========================================================================
    # SUMMARY CHARTS
    # =========================================================================
    
    def create_metrics_summary(
        self,
        metrics: Dict[str, Any],
        title: str = "Key Metrics Summary"
    ) -> go.Figure:
        """
        Create summary cards/indicators for key metrics.
        
        Args:
            metrics: Dictionary of metrics
            title: Chart title
            
        Returns:
            Plotly figure
        """
        fig = make_subplots(
            rows=1, cols=4,
            specs=[[{"type": "indicator"}] * 4],
            subplot_titles=["Stations", "Connectors", "Fast Chargers", "Operators"]
        )
        
        # Stations
        fig.add_trace(go.Indicator(
            mode="number",
            value=metrics.get("total_stations", 0),
            number={'font': {'size': 40, 'color': self.colors["primary"]}}
        ), row=1, col=1)
        
        # Connectors
        fig.add_trace(go.Indicator(
            mode="number",
            value=metrics.get("total_connectors", 0),
            number={'font': {'size': 40, 'color': self.colors["secondary"]}}
        ), row=1, col=2)
        
        # Fast Chargers
        fig.add_trace(go.Indicator(
            mode="number",
            value=metrics.get("fast_chargers", 0),
            number={'font': {'size': 40, 'color': self.colors["warning"]}}
        ), row=1, col=3)
        
        # Operators
        fig.add_trace(go.Indicator(
            mode="number",
            value=metrics.get("unique_operators", 0),
            number={'font': {'size': 40, 'color': self.colors["info"]}}
        ), row=1, col=4)
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=18)),
            height=200,
            margin=dict(t=80, b=20)
        )
        
        return fig
    
    def create_grade_distribution_chart(
        self,
        grades: Dict[str, int],
        title: str = "Accessibility Grade Distribution"
    ) -> go.Figure:
        """
        Create bar chart showing grade distribution.
        
        Args:
            grades: Dictionary of grade counts
            title: Chart title
            
        Returns:
            Plotly figure
        """
        grade_order = ["A", "B", "C", "D", "F"]
        colors = ["#10b981", "#84cc16", "#f59e0b", "#f97316", "#ef4444"]
        
        names = [g for g in grade_order if g in grades]
        values = [grades.get(g, 0) for g in names]
        bar_colors = [colors[grade_order.index(g)] for g in names]
        
        fig = go.Figure(data=[go.Bar(
            x=names,
            y=values,
            marker_color=bar_colors,
            text=values,
            textposition="outside"
        )])
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=18)),
            template=self.template,
            xaxis_title="Grade",
            yaxis_title="Number of Stations",
            height=350
        )
        
        return fig


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("📊 Chart Generator")
    print("=" * 60)
    
    # Initialize generator
    generator = ChartGenerator()
    print("✅ Generator initialized")
    
    # Test data
    operators = {
        "ChargePoint": {"stations": 195, "market_share": 44.8},
        "Blink": {"stations": 52, "market_share": 12.0},
        "Tesla": {"stations": 44, "market_share": 10.1},
        "Shell Recharge": {"stations": 25, "market_share": 5.7},
        "EVgo": {"stations": 20, "market_share": 4.6},
        "Other": {"stations": 99, "market_share": 22.8}
    }
    
    levels = {
        "distribution": {
            "Level 1 (Slow)": {"count": 50},
            "Level 2 (Medium)": {"count": 1200},
            "Level 3 (Fast)": {"count": 300},
            "DC Fast (Ultra)": {"count": 306}
        }
    }
    
    equity_components = {
        "Access": 70.7,
        "Affordability": 58.6,
        "Mobility": 90.0,
        "Income Alignment": 77.7
    }
    
    grades = {"A": 5, "B": 3, "C": 2, "D": 0, "F": 0}
    
    # Create charts
    print("\n📊 Creating charts...")
    
    # 1. Operator pie chart
    pie_chart = generator.create_operator_pie_chart(operators)
    pie_chart.write_html("data/operator_pie.html")
    print("   ✅ Operator pie chart: data/operator_pie.html")
    
    # 2. Operator bar chart
    bar_chart = generator.create_operator_bar_chart(operators)
    bar_chart.write_html("data/operator_bar.html")
    print("   ✅ Operator bar chart: data/operator_bar.html")
    
    # 3. Charging level chart
    level_chart = generator.create_charging_level_chart(levels)
    level_chart.write_html("data/charging_levels.html")
    print("   ✅ Charging level chart: data/charging_levels.html")
    
    # 4. Equity gauge
    gauge = generator.create_equity_gauge(72.9)
    gauge.write_html("data/equity_gauge.html")
    print("   ✅ Equity gauge: data/equity_gauge.html")
    
    # 5. Equity radar
    radar = generator.create_equity_components_chart(equity_components)
    radar.write_html("data/equity_radar.html")
    print("   ✅ Equity radar chart: data/equity_radar.html")
    
    # 6. Grade distribution
    grade_chart = generator.create_grade_distribution_chart(grades)
    grade_chart.write_html("data/grade_distribution.html")
    print("   ✅ Grade distribution: data/grade_distribution.html")
    
    print("\n✅ All charts created successfully!")
    print("   Open the HTML files in your browser to view them.")