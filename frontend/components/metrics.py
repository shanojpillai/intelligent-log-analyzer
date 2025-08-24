"""
Metrics components for the Intelligent Log Analyzer frontend.

This module provides reusable metric display components.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def display_metric_card(title, value, delta=None, delta_color="normal"):
    """Display a styled metric card."""
    
    delta_html = ""
    if delta is not None:
        color = "green" if delta_color == "normal" and delta > 0 else "red" if delta < 0 else "gray"
        delta_html = f'<div style="color: {color}; font-size: 0.8rem;">{"+" if delta > 0 else ""}{delta}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 2rem; font-weight: bold; color: #333;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def display_severity_chart(severity_data):
    """Display a severity distribution chart."""
    
    if not severity_data:
        st.info("No severity data available")
        return
    
    fig = px.pie(
        values=list(severity_data.values()),
        names=list(severity_data.keys()),
        title="Issue Severity Distribution",
        color_discrete_map={
            'HIGH': '#ff4444',
            'MEDIUM': '#ffaa00',
            'LOW': '#44ff44'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True)
    
    st.plotly_chart(fig, use_container_width=True)

def display_progress_bar(progress, status="Processing"):
    """Display a styled progress bar."""
    
    progress_color = "#667eea"
    if status.lower() == "completed":
        progress_color = "#44ff44"
    elif status.lower() == "failed":
        progress_color = "#ff4444"
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: bold;">{status}</span>
            <span>{progress}%</span>
        </div>
        <div style="background: #f0f0f0; border-radius: 10px; height: 10px; overflow: hidden;">
            <div style="background: {progress_color}; height: 100%; width: {progress}%; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_status_badge(status):
    """Display a colored status badge."""
    
    status_colors = {
        'queued': '#ffa500',
        'processing': '#667eea',
        'completed': '#44ff44',
        'failed': '#ff4444'
    }
    
    color = status_colors.get(status.lower(), '#666666')
    
    st.markdown(f"""
    <span style="
        background: {color};
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    ">{status}</span>
    """, unsafe_allow_html=True)

def display_key_findings_list(findings):
    """Display a styled list of key findings."""
    
    if not findings:
        st.info("No key findings available")
        return
    
    st.markdown("#### 🔍 Key Findings")
    
    for i, finding in enumerate(findings, 1):
        st.markdown(f"""
        <div style="
            background: #f8f9ff;
            border-left: 4px solid #667eea;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 5px 5px 0;
        ">
            <strong>{i}.</strong> {finding}
        </div>
        """, unsafe_allow_html=True)

def display_recommendations_list(recommendations):
    """Display a styled list of recommendations."""
    
    if not recommendations:
        st.info("No recommendations available")
        return
    
    st.markdown("#### 💡 Recommendations")
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"""
        <div style="
            background: #f0fff0;
            border-left: 4px solid #44ff44;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 5px 5px 0;
        ">
            <strong>Action {i}:</strong> {rec}
        </div>
        """, unsafe_allow_html=True)
