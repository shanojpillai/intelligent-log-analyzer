"""
Upload page component for the Intelligent Log Analyzer frontend.

This module handles the file upload interface and job submission functionality.
"""

import streamlit as st
import requests
import os
from pathlib import Path

def render_upload_page():
    """Render the upload page interface."""
    
    st.markdown('<h1 class="main-header">📤 Upload Log Files</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="upload-zone">
        <h3>🗂️ Drag and Drop Your ZIP Files</h3>
        <p>Upload ZIP files containing your application logs for AI-powered analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a ZIP file",
        type=['zip'],
        help="Upload ZIP files containing log files (max 100MB)"
    )
    
    if uploaded_file is not None:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📁 File Name", uploaded_file.name)
        
        with col2:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.metric("📊 File Size", f"{file_size_mb:.2f} MB")
        
        with col3:
            st.metric("📋 File Type", uploaded_file.type)
        
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            with st.spinner("Uploading file and starting analysis..."):
                try:
                    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                    
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/zip")}
                    response = requests.post(f"{backend_url}/api/upload", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        job_id = result.get("job_id")
                        
                        if "jobs" not in st.session_state:
                            st.session_state.jobs = []
                        
                        st.session_state.jobs.append({
                            "job_id": job_id,
                            "filename": uploaded_file.name,
                            "status": "queued",
                            "progress": 0
                        })
                        
                        st.success(f"✅ File uploaded successfully! Job ID: {job_id}")
                        st.info("🔄 Your file is now being processed. Check the Dashboard for progress updates.")
                        
                        st.markdown("### 🎯 Next Steps")
                        st.markdown("""
                        1. **Monitor Progress**: Go to the Dashboard to track analysis progress
                        2. **Review Results**: Once complete, view detailed findings and recommendations
                        3. **Export Reports**: Generate PDF or Word reports of the analysis
                        """)
                        
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Error uploading file: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📋 Upload Guidelines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **✅ Supported Formats:**
        - ZIP files containing log files
        - Common log formats (txt, log, json)
        - Application and system logs
        - Error and access logs
        """)
    
    with col2:
        st.markdown("""
        **⚠️ Requirements:**
        - Maximum file size: 100MB
        - ZIP format only
        - Valid log file contents
        - No encrypted archives
        """)
    
    st.markdown("### 🎯 Try with Sample Data")
    
    if st.button("📥 Download Sample Log Files"):
        st.info("Sample log files would be downloaded here in a real implementation")
    
    if "jobs" in st.session_state and st.session_state.jobs:
        st.markdown("### 📚 Recent Uploads")
        
        for job in st.session_state.jobs[-3:]:
            with st.expander(f"📁 {job['filename']} - {job['status'].title()}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Job ID:** {job['job_id']}")
                
                with col2:
                    st.write(f"**Status:** {job['status'].title()}")
                
                with col3:
                    if job['status'] == 'completed':
                        if st.button(f"View Results", key=f"view_{job['job_id']}"):
                            st.switch_page("Dashboard")
