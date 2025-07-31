"""Chart creation utilities."""
import plotly.graph_objects as go
from typing import Dict, List

def create_payoff_chart(payoff_data: Dict[float, float], current_price: float, breakeven_points: List[float], title: str = "Strategy Payoff Diagram") -> go.Figure:
    prices = list(payoff_data.keys())
    payoffs = list(payoff_data.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices, y=payoffs, mode='lines', name='Payoff', line=dict(color='#1f77b4', width=3)))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=current_price, line_dash="dot", line_color="red", annotation_text=f"Precio Actual: ${current_price:.2f}")
    
    for i, breakeven in enumerate(breakeven_points):
        fig.add_vline(x=breakeven, line_dash="dash", line_color="orange", annotation_text=f"BE: ${breakeven:.2f}")
    
    fig.update_layout(title=title, xaxis_title="Precio del Subyacente ($)", yaxis_title="Profit/Loss ($)", template='plotly_white', height=500)
    return fig
