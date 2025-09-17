#!/usr/bin/env python3
"""
Test script to verify education level formatting
"""
import requests
import json

# Test data
test_data = {
    "education_level": "2nd year",
    "interests": ["AI/ML"],
    "career_goal": "Data Scientist",
    "course_count": 3
}

# Make request to local server
url = "http://localhost:5001/api/recommend"

try:
    print("Testing education level formatting...")
    print(f"Sending data: {test_data}")
    
    response = requests.post(url, json=test_data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*50)
        print("SUCCESS! Response received:")
        print("="*50)
        print(result.get('recommendation', 'No recommendation found'))
        print("="*50)
    else:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error making request: {e}")