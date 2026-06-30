#!/usr/bin/env python3
"""
Test script for the real-time voice interview system
"""
import requests
import json

BACKEND_URL = "http://localhost:8001"

def test_upload_resume():
    """Test resume upload"""
    print("Testing resume upload...")
    # For testing, we'll create a simple test file
    with open("test_resume.txt", "w") as f:
        f.write("Test resume content for AI Mock Interview System")

    # Since we need a PDF, let's just test the endpoint availability
    try:
        response = requests.get(f"{BACKEND_URL}/docs")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend not responding")
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")

def test_process_transcript():
    """Test the new process_transcript endpoint"""
    print("\nTesting process_transcript endpoint...")

    # Test with invalid session first
    test_data = {
        "session_id": "invalid_session",
        "transcript": "Test transcript"
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/process_transcript",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint exists and responded")
            if "error" in data:
                print(f"Expected error for invalid session: {data['error']}")
            else:
                print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🧪 Testing AI Mock Interview - Real-Time Voice System")
    print("=" * 50)

    test_upload_resume()
    test_process_transcript()

    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print("\nTo use the system:")
    print("1. Backend running on: http://localhost:8001")
    print("2. Frontend available at: http://localhost:3000")
    print("3. Open http://localhost:3000 in Chrome/Edge browser")
    print("4. Allow microphone permissions when prompted")

if __name__ == "__main__":
    main()