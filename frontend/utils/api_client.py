"""
API client utilities for the Intelligent Log Analyzer frontend.

This module provides functions for communicating with the backend API.
"""

import requests
import os
import json
from typing import Dict, List, Optional, Any

class APIClient:
    """Client for communicating with the backend API."""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize the API client."""
        self.base_url = base_url or os.getenv("BACKEND_URL", "http://localhost:8000")
        self.session = requests.Session()
    
    def upload_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Upload a file for analysis."""
        try:
            files = {"file": (filename, file_data, "application/zip")}
            response = self.session.post(f"{self.base_url}/api/upload", files=files)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Upload failed: {str(e)}")
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of a processing job."""
        try:
            response = self.session.get(f"{self.base_url}/api/jobs/{job_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get job status: {str(e)}")
    
    def get_job_results(self, job_id: str) -> Dict[str, Any]:
        """Get the results of a completed job."""
        try:
            response = self.session.get(f"{self.base_url}/api/jobs/{job_id}/results")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get job results: {str(e)}")
    
    def list_jobs(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List all jobs with optional filtering."""
        try:
            params: Dict[str, Any] = {"limit": limit, "offset": offset}
            if status:
                params["status"] = status
            
            response = self.session.get(f"{self.base_url}/api/jobs", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to list jobs: {str(e)}")
    
    def search_similar_cases(self, query: str, limit: int = 10, threshold: float = 0.7) -> Dict[str, Any]:
        """Search for similar historical cases."""
        try:
            params = {
                "query": query,
                "limit": limit,
                "threshold": threshold
            }
            response = self.session.get(f"{self.base_url}/api/search/similar", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to search similar cases: {str(e)}")
    
    def export_results(self, job_id: str, format_type: str) -> Dict[str, Any]:
        """Export analysis results in specified format."""
        try:
            data = {"job_id": job_id}
            response = self.session.post(f"{self.base_url}/api/export/{format_type}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to export results: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the backend services."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Health check failed: {str(e)}")

api_client = APIClient()
