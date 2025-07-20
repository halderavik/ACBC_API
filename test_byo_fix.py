#!/usr/bin/env python3
"""
Quick test to check BYO config endpoint
"""

import requests
import json

BASE_URL = "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com"

def test_byo_config():
    """Test the BYO config endpoint."""
    url = f"{BASE_URL}/api/byo-config"
    
    data = {
        "session_id": "test_fix_123",
        "selected_attributes": {
            "brand": ["Apple", "Samsung"],
            "storage": ["64GB", "128GB"]
        }
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ BYO config endpoint is working!")
        else:
            print("❌ BYO config endpoint has issues")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing BYO config endpoint...")
    test_byo_config() 