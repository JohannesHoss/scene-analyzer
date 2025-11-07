#!/usr/bin/env python3
"""
Tatort Treatment Analysis Test - Crime Mode
Tests the complete workflow: Upload -> Analyze -> Download
"""

import requests
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8001"
TREATMENT_PATH = "/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/examples/treatments/Tatort_SaltoMortale_Treatment_2025-08.pdf"
OUTPUT_DIR = "/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/tests/output"

# Analysis parameters for Tatort mode
ANALYSIS_CONFIG = {
    "output_language": "DE",
    "model": "gpt-4o-mini",
    "mode": "tatort",  # Crime mode
    "protagonist_count": 2
}


def test_api_health():
    """Test if API is running"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        print("✅ API is healthy")
        print(f"   Status: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False


def upload_treatment():
    """Upload the Tatort treatment file"""
    print("\n📤 Uploading Tatort treatment...")
    
    if not os.path.exists(TREATMENT_PATH):
        print(f"❌ File not found: {TREATMENT_PATH}")
        return None
    
    file_size_mb = os.path.getsize(TREATMENT_PATH) / 1024 / 1024
    print(f"   File size: {file_size_mb:.2f} MB")
    
    try:
        with open(TREATMENT_PATH, 'rb') as f:
            files = {'file': (os.path.basename(TREATMENT_PATH), f, 'application/pdf')}
            response = requests.post(
                f"{BASE_URL}/api/v1/upload",
                files=files,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Upload successful")
            print(f"   File ID: {data['file_id']}")
            print(f"   Status: {data['status']}")
            
            return data['file_id']
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None


def inspect_scenes(file_id):
    """Inspect extracted scenes (debug endpoint)"""
    print(f"\n🔎 Inspecting extracted scenes...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/scenes/{file_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Scene extraction:")
        print(f"   Total scenes: {data['total_scenes']}")
        print(f"   Detected language: {data['detected_language']}")
        
        # Show first 3 scenes
        print(f"\n   First 3 scenes preview:")
        for i, scene in enumerate(data['scenes'][:3], 1):
            print(f"   Scene {i}: {scene.get('int_ext', '?')} - {scene.get('location', 'UNKNOWN')} - {scene.get('time_of_day', '?')}")
            text_preview = scene['text'][:100].replace('\n', ' ')
            print(f"            {text_preview}...")
        
        return data['total_scenes']
    except Exception as e:
        print(f"❌ Scene inspection failed: {e}")
        return 0


def start_analysis(file_id):
    """Start Crime mode analysis"""
    print(f"\n🚀 Starting Tatort (Crime) analysis...")
    
    request_data = {
        "file_id": file_id,
        **ANALYSIS_CONFIG
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            json=request_data,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Analysis started")
        print(f"   Job ID: {data['job_id']}")
        print(f"   Total scenes: {data['total_scenes']}")
        print(f"   Estimated cost: €{data['estimated_cost']:.3f}")
        
        return data['job_id']
    except Exception as e:
        print(f"❌ Analysis start failed: {e}")
        return None


def poll_status(job_id, max_wait=300):
    """Poll analysis status until completion"""
    print(f"\n⏳ Waiting for analysis to complete...")
    
    start_time = time.time()
    last_progress = -1
    
    try:
        while time.time() - start_time < max_wait:
            response = requests.get(f"{BASE_URL}/api/v1/status/{job_id}", timeout=10)
            response.raise_for_status()
            status = response.json()
            
            # Show progress updates
            progress = status.get('progress', 0)
            if progress != last_progress:
                current = status.get('current_scene', '?')
                total = status.get('total_scenes', '?')
                print(f"   Progress: {progress}% (Scene {current}/{total})")
                last_progress = progress
            
            # Check if completed
            if status['status'] == 'completed':
                elapsed = time.time() - start_time
                print(f"✅ Analysis completed in {elapsed:.1f} seconds")
                return True
            
            # Check for errors
            if status['status'] == 'error':
                print(f"❌ Analysis failed: {status.get('error', 'Unknown error')}")
                return False
            
            time.sleep(2)
        
        print(f"⏰ Timeout after {max_wait} seconds")
        return False
        
    except Exception as e:
        print(f"❌ Status polling failed: {e}")
        return False


def download_results(job_id):
    """Download Excel results"""
    print(f"\n📥 Downloading results...")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/download/{job_id}", timeout=30)
        response.raise_for_status()
        
        # Extract filename from Content-Disposition header
        content_disp = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disp:
            filename = content_disp.split('filename=')[1].strip('"')
        else:
            filename = f"tatort_analysis_{job_id}.xlsx"
        
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Save file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        file_size_kb = len(response.content) / 1024
        print(f"✅ Results downloaded")
        print(f"   File: {output_path}")
        print(f"   Size: {file_size_kb:.1f} KB")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


def get_results_preview(job_id):
    """Get JSON preview of results"""
    print(f"\n📊 Results preview...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/results/{job_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"   Mode: {data['mode']}")
        print(f"   Language: {data['language']}")
        print(f"   Model: {data['model']}")
        print(f"   Total scenes analyzed: {data['total_scenes']}")
        
        # Show first analyzed scene
        if data['results']:
            scene = data['results'][0]
            print(f"\n   First scene example:")
            print(f"   - Scene: {scene['number']}")
            print(f"   - Location: {scene['int_ext']} - {scene['location']} - {scene['time_of_day']}")
            print(f"   - Story Event: {scene.get('story_event', 'N/A')[:100]}...")
            print(f"   - Characters on stage: {', '.join(scene.get('on_stage', [])[:5])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Results preview failed: {e}")
        return False


def main():
    """Run complete Tatort analysis test"""
    print("=" * 60)
    print("🔍 TATORT TREATMENT ANALYSIS TEST - CRIME MODE")
    print("=" * 60)
    print(f"\nTreatment: {os.path.basename(TREATMENT_PATH)}")
    print(f"Mode: {ANALYSIS_CONFIG['mode']}")
    print(f"Language: {ANALYSIS_CONFIG['output_language']}")
    print(f"Model: {ANALYSIS_CONFIG['model']}")
    print(f"Protagonists: {ANALYSIS_CONFIG['protagonist_count']}")
    
    # Step 1: Health check
    if not test_api_health():
        print("\n⚠️  Make sure the API is running: docker-compose up")
        return
    
    # Step 2: Upload
    file_id = upload_treatment()
    if not file_id:
        return
    
    # Step 3: Inspect scenes
    scene_count = inspect_scenes(file_id)
    if scene_count == 0:
        return
    
    # Step 4: Start analysis
    job_id = start_analysis(file_id)
    if not job_id:
        return
    
    # Step 5: Wait for completion
    if not poll_status(job_id):
        return
    
    # Step 6: Preview results
    get_results_preview(job_id)
    
    # Step 7: Download
    output_file = download_results(job_id)
    if not output_file:
        return
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"\n📁 Results saved to: {output_file}")
    print("   Open the Excel file to review the Crime mode analysis")


if __name__ == "__main__":
    main()
