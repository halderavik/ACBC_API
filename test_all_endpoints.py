#!/usr/bin/env python3
"""
Comprehensive API endpoint test script for ACBC API.
Tests all endpoints to ensure they're working after numpy deployment.
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com"

def test_endpoint(method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test a single endpoint and return results."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": 200 <= response.status_code < 300,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "url": url
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "success": False,
            "url": url
        }

def main():
    """Run comprehensive API tests."""
    print("🧪 Testing ACBC API Endpoints")
    print("=" * 50)
    
    # Test 1: Health endpoint
    print("\n1. Testing Health Endpoint")
    result = test_endpoint("GET", "/health")
    if result["success"]:
        print(f"✅ Health endpoint: {result['status_code']} - {result['response']}")
    else:
        print(f"❌ Health endpoint failed: {result.get('error', result)}")
    
    # Test 2: Root endpoint
    print("\n2. Testing Root Endpoint")
    result = test_endpoint("GET", "/")
    if result["success"]:
        print(f"✅ Root endpoint: {result['status_code']} - {result['response']}")
    else:
        print(f"❌ Root endpoint failed: {result.get('error', result)}")
    
    # Test 3: API Documentation
    print("\n3. Testing API Documentation")
    result = test_endpoint("GET", "/docs")
    if result["success"]:
        print(f"✅ API docs: {result['status_code']} - Documentation accessible")
    else:
        print(f"❌ API docs failed: {result.get('error', result)}")
    
    # Test 4: BYO Config endpoint (GET with parameters)
    print("\n4. Testing BYO Config Endpoint")
    # Sample smartphone attributes
    sample_attributes = {
        "brand": ["Apple", "Samsung", "Google"],
        "price": ["$500", "$800", "$1200"],
        "storage": ["64GB", "128GB", "256GB"]
    }
    
    params = {
        "session_id": "test_session_123",
        "selected_attributes": json.dumps(sample_attributes)
    }
    
    result = test_endpoint("GET", "/api/byo-config", params=params)
    if result["success"]:
        print(f"✅ BYO config: {result['status_code']} - {result['response']}")
        session_id = result['response'].get('session_id', 'test_session_123')
    else:
        print(f"❌ BYO config failed: {result.get('error', result)}")
        session_id = "test_session_123"
    
    # Test 5: Screening Design endpoint
    print("\n5. Testing Screening Design Endpoint")
    params = {"session_id": session_id}
    result = test_endpoint("GET", "/api/screening/design", params=params)
    if result["success"]:
        print(f"✅ Screening design: {result['status_code']} - {len(result['response'])} tasks returned")
    else:
        print(f"❌ Screening design failed: {result.get('error', result)}")
    
    # Test 6: Tournament Choice endpoint
    print("\n6. Testing Tournament Choice Endpoint")
    params = {"session_id": session_id, "task_number": 1}
    result = test_endpoint("GET", "/api/tournament/choice", params=params)
    if result["success"]:
        print(f"✅ Tournament choice: {result['status_code']} - Task {result['response'].get('task_number', 'N/A')}")
        concepts = result['response'].get('concepts', [])
        print(f"   - {len(concepts)} concepts returned")
    else:
        print(f"❌ Tournament choice failed: {result.get('error', result)}")
    
    # Test 7: Choice Response endpoint (if we have concepts)
    if result["success"] and result['response'].get('concepts'):
        print("\n7. Testing Choice Response Endpoint")
        concepts = result['response']['concepts']
        if concepts:
            # Select the first concept
            selected_concept_id = concepts[0].get('id', 0)
            
            data = {
                "session_id": session_id,
                "task_number": 1,
                "selected_concept_id": selected_concept_id
            }
            
            result = test_endpoint("POST", "/api/tournament/choice-response", data=data)
            if result["success"]:
                print(f"✅ Choice response: {result['status_code']} - {result['response']}")
            else:
                print(f"❌ Choice response failed: {result.get('error', result)}")
    
    # Test 8: Screening Responses endpoint
    print("\n8. Testing Screening Responses Endpoint")
    data = {
        "session_id": session_id,
        "responses": [True, False, True, False, True]  # Sample responses
    }
    
    result = test_endpoint("POST", "/api/screening/responses", data=data)
    if result["success"]:
        print(f"✅ Screening responses: {result['status_code']} - {result['response']}")
    else:
        print(f"❌ Screening responses failed: {result.get('error', result)}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\nIf all tests passed, your ACBC API is fully functional with numpy support.")

if __name__ == "__main__":
    main() 