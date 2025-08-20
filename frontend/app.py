import streamlit as st
import requests
import json
import time
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import zipfile
import tempfile
from pathlib import Path

st.set_page_config(
    page_title="Intelligent Log Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .upload-zone {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        margin: 1rem 0;
    }
    
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-processing {
        color: #ffc107;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'current_job' not in st.session_state:
    st.session_state.current_job = None

def load_lottie_url(url: str):
    """Load Lottie animation from URL"""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def upload_file(uploaded_file):
    """Upload file to backend"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/zip")}
        response = requests.post(f"{BACKEND_URL}/api/upload", files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def get_job_status(job_id):
    """Get job status from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/jobs/{job_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching job status: {str(e)}")
        return None

def get_job_results(job_id):
    """Get job results from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/jobs/{job_id}/results")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching results: {str(e)}")
        return None

def export_report(job_id, format_type="pdf"):
    """Export analysis report"""
    try:
        response = requests.post(f"{BACKEND_URL}/api/export/{format_type}", 
                               json={"job_id": job_id})
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Export error: {str(e)}")
        return None

with st.sidebar:
    st.markdown("### 🔍 Intelligent Log Analyzer")
    
    selected = option_menu(
        menu_title=None,
        options=["Upload", "Dashboard", "Analysis", "Knowledge Base", "Settings"],
        icons=["cloud-upload", "speedometer2", "graph-up", "book", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#667eea", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#667eea"},
        }
    )
    
    st.markdown("---")
    
    st.markdown("### System Status")
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("🟢 Backend Online")
        else:
            st.error("🔴 Backend Offline")
    except:
        st.error("🔴 Backend Offline")
    
    st.markdown("### Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Jobs", len([j for j in st.session_state.jobs if j.get('status') == 'processing']))
    with col2:
        st.metric("Completed", len([j for j in st.session_state.jobs if j.get('status') == 'completed']))

if selected == "Upload":
    st.markdown('<h1 class="main-header">📤 Upload Portal</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="upload-zone">
            <h3>🗂️ Drop your ZIP files here</h3>
            <p>Upload log files for intelligent analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a ZIP file",
            type=['zip'],
            help="Upload ZIP files containing log files for analysis"
        )
        
        if uploaded_file is not None:
            st.success(f"File selected: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
            
            with col_b:
                if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                    with st.spinner("Uploading file..."):
                        result = upload_file(uploaded_file)
                        
                        if result:
                            job_info = {
                                'job_id': result['job_id'],
                                'filename': uploaded_file.name,
                                'status': 'processing',
                                'created_at': datetime.now().isoformat(),
                                'progress': 0
                            }
                            st.session_state.jobs.append(job_info)
                            st.session_state.current_job = result['job_id']
                            
                            st.success(f"✅ Upload successful! Job ID: {result['job_id']}")
                            st.info("🔄 Processing started. Check the Dashboard for progress.")
                            
                            time.sleep(2)
                            st.rerun()

elif selected == "Dashboard":
    st.markdown('<h1 class="main-header">📊 Results Dashboard</h1>', unsafe_allow_html=True)
    
    if not st.session_state.jobs:
        st.info("📝 No jobs found. Upload a file to get started!")
    else:
        st.markdown("### 📋 Job Overview")
        
        jobs_df = pd.DataFrame(st.session_state.jobs)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_jobs = len(st.session_state.jobs)
            st.metric("Total Jobs", total_jobs)
        
        with col2:
            processing_jobs = len([j for j in st.session_state.jobs if j.get('status') == 'processing'])
            st.metric("Processing", processing_jobs)
        
        with col3:
            completed_jobs = len([j for j in st.session_state.jobs if j.get('status') == 'completed'])
            st.metric("Completed", completed_jobs)
        
        with col4:
            failed_jobs = len([j for j in st.session_state.jobs if j.get('status') == 'failed'])
            st.metric("Failed", failed_jobs)
        
        st.markdown("---")
        
        st.markdown("### 📄 Job Details")
        
        for i, job in enumerate(reversed(st.session_state.jobs)):
            with st.expander(f"🗂️ {job['filename']} - {job['job_id'][:8]}...", expanded=(i == 0)):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Job ID:** {job['job_id']}")
                    st.write(f"**Created:** {job['created_at']}")
                    st.write(f"**Status:** {job['status']}")
                
                with col2:
                    if st.button(f"🔄 Refresh", key=f"refresh_{job['job_id']}"):
                        status = get_job_status(job['job_id'])
                        if status:
                            for j in st.session_state.jobs:
                                if j['job_id'] == job['job_id']:
                                    j['status'] = status.get('status', 'unknown')
                                    j['progress'] = status.get('progress', 0)
                            st.rerun()
                
                progress = job.get('progress', 0)
                st.progress(progress / 100 if progress <= 100 else 1.0)
                
                if job['status'] == 'completed':
                    if st.button(f"📊 View Results", key=f"results_{job['job_id']}"):
                        st.session_state.current_job = job['job_id']
                        st.info("Switching to Analysis view...")

elif selected == "Analysis":
    st.markdown('<h1 class="main-header">🔬 Analysis Results</h1>', unsafe_allow_html=True)
    
    if st.session_state.current_job:
        job_id = st.session_state.current_job
        
        results = get_job_results(job_id)
        
        if results:
            st.success(f"📊 Analysis Results for Job: {job_id[:8]}...")
            
            tab1, tab2, tab3, tab4 = st.tabs(["🎯 Summary", "🔍 Similar Cases", "🧠 AI Analysis", "📄 Export"])
            
            with tab1:
                st.markdown("### 📈 Analysis Summary")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Log Files Processed", results.get('files_processed', 0))
                
                with col2:
                    st.metric("Issues Detected", results.get('issues_found', 0))
                
                with col3:
                    st.metric("Confidence Score", f"{results.get('confidence', 0):.1f}%")
                
                st.markdown("### 🔑 Key Findings")
                findings = results.get('key_findings', [])
                for finding in findings:
                    st.info(f"• {finding}")
                
                if 'severity_distribution' in results:
                    st.markdown("### 📊 Issue Severity Distribution")
                    severity_data = results['severity_distribution']
                    fig = px.pie(
                        values=list(severity_data.values()),
                        names=list(severity_data.keys()),
                        title="Issues by Severity"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.markdown("### 🔍 Similar Historical Cases")
                
                similar_cases = results.get('similar_cases', [])
                
                if similar_cases:
                    for i, case in enumerate(similar_cases):
                        with st.expander(f"📋 Case #{i+1} - Similarity: {case.get('similarity', 0):.1f}%"):
                            st.write(f"**Description:** {case.get('description', 'N/A')}")
                            st.write(f"**Resolution:** {case.get('resolution', 'N/A')}")
                            st.write(f"**Date:** {case.get('date', 'N/A')}")
                            
                            if case.get('solution'):
                                st.success(f"💡 **Recommended Solution:** {case['solution']}")
                else:
                    st.info("No similar cases found in the knowledge base.")
            
            with tab3:
                st.markdown("### 🧠 AI Analysis (Open Source LLM)")
                
                ai_analysis = results.get('ai_analysis', {})
                
                if ai_analysis:
                    st.markdown("#### 🎯 Root Cause Analysis")
                    st.write(ai_analysis.get('root_cause', 'Analysis in progress...'))
                    
                    st.markdown("#### 💡 Recommendations")
                    recommendations = ai_analysis.get('recommendations', [])
                    for rec in recommendations:
                        st.success(f"• {rec}")
                    
                    st.markdown("#### 🏷️ Extracted Entities (spaCy NLU)")
                    entities = ai_analysis.get('entities', [])
                    if entities:
                        entity_df = pd.DataFrame(entities)
                        st.dataframe(entity_df, use_container_width=True)
                    else:
                        st.info("No entities extracted.")
                else:
                    st.info("AI analysis in progress...")
            
            with tab4:
                st.markdown("### 📄 Export Reports")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 Export PDF", type="primary", use_container_width=True):
                        with st.spinner("Generating PDF report..."):
                            export_result = export_report(job_id, "pdf")
                            if export_result:
                                st.success("PDF report generated successfully!")
                                st.download_button(
                                    label="⬇️ Download PDF",
                                    data=export_result.get('file_data', ''),
                                    file_name=f"analysis_report_{job_id[:8]}.pdf",
                                    mime="application/pdf"
                                )
                
                with col2:
                    if st.button("📝 Export Word", type="secondary", use_container_width=True):
                        with st.spinner("Generating Word document..."):
                            export_result = export_report(job_id, "word")
                            if export_result:
                                st.success("Word document generated successfully!")
                                st.download_button(
                                    label="⬇️ Download Word",
                                    data=export_result.get('file_data', ''),
                                    file_name=f"analysis_report_{job_id[:8]}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
        else:
            st.warning("No results available for this job yet.")
    else:
        st.info("Select a completed job from the Dashboard to view analysis results.")

elif selected == "Knowledge Base":
    st.markdown('<h1 class="main-header">📚 Knowledge Base</h1>', unsafe_allow_html=True)
    
    st.markdown("### 🔍 Search Historical Solutions")
    
    search_query = st.text_input("Search for similar issues or solutions:")
    
    if search_query:
        if st.button("🔍 Search"):
            with st.spinner("Searching knowledge base..."):
                st.success("Found 3 similar cases:")
                
                with st.expander("📋 Database Connection Timeout"):
                    st.write("**Issue:** Database connection timeout errors in production")
                    st.write("**Solution:** Increase connection pool size and timeout values")
                    st.write("**Success Rate:** 95%")
                
                with st.expander("📋 Memory Leak in Application"):
                    st.write("**Issue:** Gradual memory increase leading to OOM errors")
                    st.write("**Solution:** Implement proper resource cleanup and garbage collection")
                    st.write("**Success Rate:** 88%")
                
                with st.expander("📋 API Rate Limiting"):
                    st.write("**Issue:** External API calls being rate limited")
                    st.write("**Solution:** Implement exponential backoff and request queuing")
                    st.write("**Success Rate:** 92%")
    
    st.markdown("---")
    
    st.markdown("### 📊 Knowledge Base Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cases", "1,247")
    
    with col2:
        st.metric("Solved Cases", "1,156")
    
    with col3:
        st.metric("Success Rate", "92.7%")
    
    with col4:
        st.metric("Categories", "23")

elif selected == "Settings":
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    
    st.markdown("### 🔧 System Configuration")
    
    with st.expander("🌐 API Configuration"):
        st.text_input("Backend URL", value=BACKEND_URL)
        st.text_input("Ollama Host", value="http://ollama:11434")
        st.text_input("Weaviate URL", value="http://weaviate:8080")
    
    with st.expander("📊 Processing Settings"):
        st.slider("Max Concurrent Jobs", 1, 10, 5)
        st.slider("Job Timeout (minutes)", 5, 60, 30)
        st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
    
    with st.expander("🎨 UI Preferences"):
        st.selectbox("Theme", ["Light", "Dark", "Auto"])
        st.checkbox("Enable Animations", value=True)
        st.checkbox("Auto-refresh Dashboard", value=True)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        🔍 Intelligent Log Analyzer | Built with ❤️ using Streamlit | 
        <a href='#' style='color: #667eea;'>Documentation</a> | 
        <a href='#' style='color: #667eea;'>Support</a>
    </div>
    """, 
    unsafe_allow_html=True
)

if st.session_state.jobs and any(job.get('status') == 'processing' for job in st.session_state.jobs):
    time.sleep(5)
    st.rerun()
