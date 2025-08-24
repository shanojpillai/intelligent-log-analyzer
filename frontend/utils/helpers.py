"""
Helper utilities for the Intelligent Log Analyzer frontend.

This module provides common utility functions for the Streamlit application.
"""

import streamlit as st
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size_float = float(size_bytes)
    while size_float >= 1024 and i < len(size_names) - 1:
        size_float /= 1024.0
        i += 1
    
    return f"{size_float:.2f} {size_names[i]}"

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def get_status_color(status: str) -> str:
    """Get color for status display."""
    status_colors = {
        'queued': '#ffa500',
        'processing': '#667eea',
        'extracting': '#667eea',
        'embedding': '#667eea',
        'retrieving': '#667eea',
        'ai_analysis': '#667eea',
        'nlu_processing': '#667eea',
        'completed': '#44ff44',
        'failed': '#ff4444',
        'error': '#ff4444'
    }
    return status_colors.get(status.lower(), '#666666')

def validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """Validate uploaded file."""
    if uploaded_file is None:
        return False, "No file selected"
    
    if not uploaded_file.name.endswith('.zip'):
        return False, "Only ZIP files are supported"
    
    max_size = 100 * 1024 * 1024
    if uploaded_file.size > max_size:
        return False, f"File too large. Maximum size is {format_file_size(max_size)}"
    
    return True, "File is valid"

def init_session_state():
    """Initialize session state variables."""
    if "jobs" not in st.session_state:
        st.session_state.jobs = []
    
    if "current_job" not in st.session_state:
        st.session_state.current_job = None
    
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = True

def update_job_in_session(job_id: str, updates: Dict[str, Any]):
    """Update a job in session state."""
    if "jobs" not in st.session_state:
        st.session_state.jobs = []
    
    for i, job in enumerate(st.session_state.jobs):
        if job.get('job_id') == job_id:
            st.session_state.jobs[i].update(updates)
            break
    else:
        updates['job_id'] = job_id
        st.session_state.jobs.append(updates)
