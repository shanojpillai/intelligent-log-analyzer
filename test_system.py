#!/usr/bin/env python3
"""
Test script to verify the intelligent log analyzer system functionality
"""
import requests
import time
import json
import os
from pathlib import Path

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_file_upload():
    """Test file upload functionality"""
    try:
        zip_file = Path("sample_logs.zip")
        if not zip_file.exists():
            print("❌ Sample logs zip file not found")
            return None
            
        with open(zip_file, "rb") as f:
            files = {"file": ("sample_logs.zip", f, "application/zip")}
            response = requests.post("http://localhost:8000/api/upload", files=files, timeout=30)
            
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job_id")
            print(f"✅ File upload successful, job ID: {job_id}")
            return job_id
        else:
            print(f"❌ File upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ File upload failed: {e}")
        return None

def test_job_status(job_id):
    """Test job status checking"""
    try:
        response = requests.get(f"http://localhost:8000/api/jobs/{job_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            progress = data.get("progress", "0")
            print(f"✅ Job status check successful: {status} ({progress}%)")
            return data
        else:
            print(f"❌ Job status check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Job status check failed: {e}")
        return None

def test_job_results(job_id):
    """Test job results retrieval"""
    try:
        response = requests.get(f"http://localhost:8000/api/jobs/{job_id}/results", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "not available" in data["message"]:
                print("⏳ Results not ready yet")
                return False
            else:
                print("✅ Job results retrieved successfully")
                print(f"   Files processed: {data.get('files_processed', 'N/A')}")
                print(f"   Issues found: {data.get('issues_found', 'N/A')}")
                return True
        else:
            print(f"❌ Job results check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Job results check failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Intelligent Log Analyzer System")
    print("=" * 50)
    
    if not test_backend_health():
        print("❌ Backend is not healthy, stopping tests")
        return
    
    job_id = test_file_upload()
    if not job_id:
        print("❌ File upload failed, stopping tests")
        return
    
    print("\n⏳ Monitoring job progress...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        job_data = test_job_status(job_id)
        if job_data:
            status = job_data.get("status", "unknown")
            if status == "completed":
                print("✅ Job completed successfully!")
                break
            elif status == "failed":
                error = job_data.get("error", "Unknown error")
                print(f"❌ Job failed: {error}")
                return
            elif status in ["queued", "processing"]:
                print(f"⏳ Job {status}... waiting 5 seconds")
                time.sleep(5)
        
        attempt += 1
    
    if attempt >= max_attempts:
        print("⏰ Job did not complete within expected time")
        return
    
    if test_job_results(job_id):
        print("✅ All tests passed! System is functional.")
    else:
        print("❌ Results retrieval failed")

if __name__ == "__main__":
    main()
