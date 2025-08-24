"""
Dashboard page component for the Intelligent Log Analyzer frontend.

This module handles the results dashboard and job monitoring functionality.
"""

import streamlit as st
import requests
import json
import time
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render_dashboard_page():
    """Render the dashboard page interface."""
    
    st.markdown('<h1 class="main-header">📊 Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    if "jobs" not in st.session_state:
        st.session_state.jobs = []
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🔄 Job Status Monitor")
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=True)
    
    with col3:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    if st.session_state.jobs:
        total_jobs = len(st.session_state.jobs)
        completed_jobs = len([j for j in st.session_state.jobs if j.get('status') == 'completed'])
        processing_jobs = len([j for j in st.session_state.jobs if j.get('status') == 'processing'])
        failed_jobs = len([j for j in st.session_state.jobs if j.get('status') == 'failed'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Jobs", total_jobs)
        
        with col2:
            st.metric("✅ Completed", completed_jobs)
        
        with col3:
            st.metric("🔄 Processing", processing_jobs)
        
        with col4:
            st.metric("❌ Failed", failed_jobs)
        
        st.markdown("### 📋 Job Details")
        
        job_data = []
        for job in st.session_state.jobs:
            job_data.append({
                "Job ID": job.get('job_id', '')[:8] + "...",
                "Filename": job.get('filename', ''),
                "Status": job.get('status', '').title(),
                "Progress": f"{job.get('progress', 0)}%",
                "Created": job.get('created_at', 'Unknown')
            })
        
        if job_data:
            df = pd.DataFrame(job_data)
            st.dataframe(df, use_container_width=True)
        
        st.markdown("### 🔍 Analysis Results")
        
        completed_jobs_list = [j for j in st.session_state.jobs if j.get('status') == 'completed']
        
        if completed_jobs_list:
            selected_job = st.selectbox(
                "Select a completed job to view results:",
                options=completed_jobs_list,
                format_func=lambda x: f"{x['filename']} ({x['job_id'][:8]}...)"
            )
            
            if selected_job:
                display_job_results(selected_job)
        else:
            st.info("🔄 No completed jobs yet. Upload a file to start analysis.")
    
    else:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: #f8f9ff; border-radius: 10px; margin: 2rem 0;'>
            <h3>🚀 Ready to Analyze Logs</h3>
            <p>Upload your first ZIP file to get started with AI-powered log analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📤 Go to Upload", type="primary", use_container_width=True):
            st.switch_page("Upload")
    
    if auto_refresh and st.session_state.jobs:
        if any(job.get('status') == 'processing' for job in st.session_state.jobs):
            time.sleep(5)
            st.rerun()

def display_job_results(job):
    """Display detailed results for a specific job."""
    
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        response = requests.get(f"{backend_url}/api/jobs/{job['job_id']}/results")
        
        if response.status_code == 200:
            results = response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📁 Files Processed", results.get('files_processed', 0))
            
            with col2:
                st.metric("⚠️ Issues Found", results.get('issues_found', 0))
            
            with col3:
                st.metric("🎯 Confidence", f"{results.get('confidence', 0)}%")
            
            with col4:
                severity_dist = results.get('severity_distribution', {})
                high_severity = severity_dist.get('HIGH', 0)
                st.metric("🔴 High Severity", high_severity)
            
            if results.get('key_findings'):
                st.markdown("#### 🔍 Key Findings")
                for finding in results['key_findings']:
                    st.markdown(f"• {finding}")
            
            if results.get('severity_distribution'):
                st.markdown("#### 📊 Issue Severity Distribution")
                
                severity_data = results['severity_distribution']
                fig = px.pie(
                    values=list(severity_data.values()),
                    names=list(severity_data.keys()),
                    color_discrete_map={
                        'HIGH': '#ff4444',
                        'MEDIUM': '#ffaa00',
                        'LOW': '#44ff44'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            if results.get('ai_analysis'):
                ai_analysis = results['ai_analysis']
                
                st.markdown("#### 🤖 AI Analysis")
                
                with st.expander("📋 Root Cause Analysis", expanded=True):
                    st.write(ai_analysis.get('root_cause', 'No analysis available'))
                
                if ai_analysis.get('recommendations'):
                    with st.expander("💡 Recommendations"):
                        for rec in ai_analysis['recommendations']:
                            st.markdown(f"• {rec}")
            
            if results.get('similar_cases'):
                st.markdown("#### 🔗 Similar Historical Cases")
                
                for case in results['similar_cases'][:3]:
                    with st.expander(f"📋 {case.get('description', 'Similar Case')} (Similarity: {case.get('similarity', 0):.2f})"):
                        st.write(f"**Solution:** {case.get('solution', 'No solution available')}")
                        st.write(f"**Success Rate:** {case.get('success_rate', 0):.2f}")
            
            st.markdown("#### 📄 Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Export PDF", use_container_width=True):
                    export_results(job['job_id'], 'pdf')
            
            with col2:
                if st.button("📝 Export Word", use_container_width=True):
                    export_results(job['job_id'], 'word')
        
        else:
            st.error("❌ Failed to fetch results")
    
    except Exception as e:
        st.error(f"❌ Error displaying results: {str(e)}")

def export_results(job_id, format_type):
    """Export analysis results in specified format."""
    
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        
        response = requests.post(
            f"{backend_url}/api/export/{format_type}",
            json={"job_id": job_id}
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ {format_type.upper()} export started! Export ID: {result.get('export_id')}")
        else:
            st.error(f"❌ Export failed: {response.text}")
    
    except Exception as e:
        st.error(f"❌ Error exporting results: {str(e)}")
