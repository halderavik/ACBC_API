#!/usr/bin/env python3
"""
Debug script to test API endpoints and identify the source of 422 and 500 errors.
"""

import requests
import json
import time

BASE_URL = "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com"

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an endpoint and return detailed results."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "headers": dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def main():
    print("🔍 Debugging API Errors")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing Health Endpoint")
    result = test_endpoint("GET", "/health")
    if result["success"]:
        print(f"✅ Health: {result['status_code']} - {result['response']}")
    else:
        print(f"❌ Health failed: {result['error']}")
        return
    
    # Test 2: BYO Config with valid data
    print("\n2. Testing BYO Config Endpoint (Valid Data)")
    valid_byo_data = {
        "session_id": "debug_test_001",
        "selected_attributes": {
            "brand": ["Nike", "Adidas"],
            "material": ["leather", "canvas"]
        }
    }
    result = test_endpoint("POST", "/api/byo-config", data=valid_byo_data)
    if result["success"]:
        print(f"✅ BYO Config: {result['status_code']} - {result['response']}")
    else:
        print(f"❌ BYO Config failed: {result['error']}")
    
    # Test 3: BYO Config with missing required fields (should get 422)
    print("\n3. Testing BYO Config Endpoint (Missing selected_attributes)")
    invalid_byo_data = {
        "session_id": "debug_test_002"
        # Missing selected_attributes
    }
    result = test_endpoint("POST", "/api/byo-config", data=invalid_byo_data)
    if result["success"]:
        print(f"✅ BYO Config (invalid): {result['status_code']} - {result['response']}")
    else:
        print(f"❌ BYO Config (invalid) failed: {result['error']}")
    
    # Test 4: Screening Responses with valid data
    print("\n4. Testing Screening Responses Endpoint (Valid Data)")
    valid_screening_data = {
        "session_id": "test456",  # Use existing session
        "responses": [True, False, True, False, True]
    }
    result = test_endpoint("POST", "/api/screening/responses", data=valid_screening_data)
    if result["success"]:
        print(f"✅ Screening Responses: {result['status_code']} - {result['response']}")
    else:
        print(f"❌ Screening Responses failed: {result['error']}")
    
    # Test 5: Screening Responses with invalid data (should get 422)
    print("\n5. Testing Screening Responses Endpoint (Invalid Data)")
    invalid_screening_data = {
        "session_id": "test456",
        "responses": "not_a_list"  # Should be a list of booleans
    }
    result = test_endpoint("POST", "/api/screening/responses", data=invalid_screening_data)
    if result["success"]:
        print(f"✅ Screening Responses (invalid): {result['status_code']} - {result['response']}")
    else:
        print(f"❌ Screening Responses (invalid) failed: {result['error']}")
    
    # Test 6: Tournament Choice with existing session
    print("\n6. Testing Tournament Choice Endpoint (Existing Session)")
    result = test_endpoint("GET", "/api/tournament/choice", params={"session_id": "test456", "task_number": 1})
    if result["success"]:
        print(f"✅ Tournament Choice: {result['status_code']} - {result['response']}")
    else:
        print(f"❌ Tournament Choice failed: {result['error']}")
    
    # Test 7: Tournament Choice with non-existent session (should get 404)
    print("\n7. Testing Tournament Choice Endpoint (Non-existent Session)")
    result = test_endpoint("GET", "/api/tournament/choice", params={"session_id": "FS_91BRT1fthh9NpSZ", "task_number": 1})
    if result["success"]:
        print(f"✅ Tournament Choice (non-existent): {result['status_code']} - {result['response']}")
    else:
        print(f"❌ Tournament Choice (non-existent) failed: {result['error']}")
    
    print("\n" + "=" * 50)
    print("🎯 Debug Analysis Complete!")
    print("\nExpected Results:")
    print("- Tests 1, 2, 4, 6 should return 200 OK")
    print("- Tests 3, 5 should return 422 Unprocessable Entity")
    print("- Test 7 should return 404 Not Found")

if __name__ == "__main__":
    main() 