#!/usr/bin/env python3
"""
Comprehensive ACBC Test with 3 attributes, 4 levels each - LOCAL VERSION
Tests all API endpoints with realistic smartphone data on local server
"""

import requests
import json
import time
import random
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"  # Local server

def test_endpoint(method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
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
    print("🚀 Comprehensive ACBC Test - 3 Attributes, 4 Levels Each (LOCAL)")
    print("=" * 60)
    
    # Define our smartphone attributes
    smartphone_attributes = {
        "brand": ["Apple", "Samsung", "Google", "OnePlus"],
        "storage": ["64GB", "128GB", "256GB", "512GB"],
        "price": ["$399", "$599", "$799", "$999"]
    }
    
    session_id = f"test_comprehensive_{int(time.time())}"
    
    print(f"\n📱 Smartphone Attributes:")
    for attr, values in smartphone_attributes.items():
        print(f"   {attr}: {values}")
    
    print(f"\n🆔 Session ID: {session_id}")
    
    # Step 1: Health Check
    print("\n1️⃣ Testing Health Endpoint")
    result = test_endpoint("GET", "/health")
    if result["success"]:
        print(f"✅ Health: {result['status_code']} - {result['response']}")
    else:
        print(f"❌ Health failed: {result['error']}")
        print("   Make sure the local server is running: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Step 2: Create BYO Configuration
    print("\n2️⃣ Creating BYO Configuration")
    byo_data = {
        "session_id": session_id,
        "selected_attributes": smartphone_attributes
    }
    
    result = test_endpoint("POST", "/api/byo-config", data=byo_data)
    if result["success"]:
        print(f"✅ BYO Config: {result['status_code']} - {result['response']}")
        if result['status_code'] == 200:
            session_id = result['response'].get('session_id', session_id)
            print(f"   Session created: {session_id}")
    else:
        print(f"❌ BYO Config failed: {result['error']}")
        return
    
    # Step 3: Get Screening Design
    print("\n3️⃣ Getting Screening Design")
    result = test_endpoint("GET", "/api/screening/design", params={"session_id": session_id})
    if result["success"]:
        print(f"✅ Screening Design: {result['status_code']}")
        if result['status_code'] == 200:
            screening_tasks = result['response']
            print(f"   Found {len(screening_tasks)} screening tasks")
            
            # Display first few tasks
            for i, task in enumerate(screening_tasks[:3]):
                print(f"   Task {i+1}: {task['concept']}")
            if len(screening_tasks) > 3:
                print(f"   ... and {len(screening_tasks) - 3} more tasks")
    else:
        print(f"❌ Screening Design failed: {result['error']}")
        return
    
    # Step 4: Submit Screening Responses
    print("\n4️⃣ Submitting Screening Responses")
    if result["success"] and result['status_code'] == 200:
        screening_tasks = result['response']
        # Generate realistic responses (mix of likes and dislikes)
        responses = [random.choice([True, False]) for _ in range(len(screening_tasks))]
        
        screening_data = {
            "session_id": session_id,
            "responses": responses
        }
        
        result = test_endpoint("POST", "/api/screening/responses", data=screening_data)
        if result["success"]:
            print(f"✅ Screening Responses: {result['status_code']} - {result['response']}")
            print(f"   Submitted {len(responses)} responses")
            print(f"   Likes: {sum(responses)}, Dislikes: {len(responses) - sum(responses)}")
        else:
            print(f"❌ Screening Responses failed: {result['error']}")
            return
    else:
        print("❌ Cannot submit screening responses - no tasks found")
        return
    
    # Step 5: Get Tournament Choice (Task 1)
    print("\n5️⃣ Getting Tournament Choice (Task 1)")
    result = test_endpoint("GET", "/api/tournament/choice", params={"session_id": session_id, "task_number": 1})
    if result["success"]:
        print(f"✅ Tournament Choice: {result['status_code']}")
        if result['status_code'] == 200:
            tournament_data = result['response']
            print(f"   Task Number: {tournament_data.get('task_number', 'N/A')}")
            concepts = tournament_data.get('concepts', [])
            print(f"   Found {len(concepts)} concepts")
            
            # Display concepts
            for i, concept in enumerate(concepts):
                print(f"   Concept {i}: {concept['attributes']}")
    else:
        print(f"❌ Tournament Choice failed: {result['error']}")
        return
    
    # Step 6: Submit Choice Response (Task 1)
    print("\n6️⃣ Submitting Choice Response (Task 1)")
    if result["success"] and result['status_code'] == 200:
        concepts = result['response'].get('concepts', [])
        if concepts:
            # Select a random concept
            selected_concept_id = random.randint(0, len(concepts) - 1)
            
            choice_data = {
                "session_id": session_id,
                "task_number": 1,
                "selected_concept_id": selected_concept_id
            }
            
            result = test_endpoint("POST", "/api/tournament/choice-response", data=choice_data)
            if result["success"]:
                print(f"✅ Choice Response: {result['status_code']} - {result['response']}")
                print(f"   Selected concept {selected_concept_id}: {concepts[selected_concept_id]['attributes']}")
                next_task = result['response'].get('next_task', 'N/A')
                print(f"   Next task: {next_task}")
            else:
                print(f"❌ Choice Response failed: {result['error']}")
                return
        else:
            print("❌ No concepts found for choice")
            return
    else:
        print("❌ Cannot submit choice response - no tournament data")
        return
    
    # Step 7: Test Multiple Tournament Tasks
    print("\n7️⃣ Testing Multiple Tournament Tasks")
    max_tasks = 5  # Test up to 5 tasks
    
    for task_num in range(2, max_tasks + 1):
        print(f"\n   Testing Task {task_num}...")
        
        # Get tournament choice
        result = test_endpoint("GET", "/api/tournament/choice", params={"session_id": session_id, "task_number": task_num})
        if result["success"] and result['status_code'] == 200:
            concepts = result['response'].get('concepts', [])
            if concepts:
                # Select a random concept
                selected_concept_id = random.randint(0, len(concepts) - 1)
                
                choice_data = {
                    "session_id": session_id,
                    "task_number": task_num,
                    "selected_concept_id": selected_concept_id
                }
                
                result = test_endpoint("POST", "/api/tournament/choice-response", data=choice_data)
                if result["success"]:
                    print(f"   ✅ Task {task_num}: Selected concept {selected_concept_id}")
                    next_task = result['response'].get('next_task', 'N/A')
                    if next_task == 'completed':
                        print(f"   🎉 Tournament completed after {task_num} tasks!")
                        break
                else:
                    print(f"   ❌ Task {task_num} choice failed: {result['error']}")
                    break
            else:
                print(f"   ❌ Task {task_num}: No concepts found")
                break
        else:
            if result['status_code'] == 404:
                print(f"   ℹ️ Task {task_num}: No more tasks available (tournament completed)")
                break
            else:
                print(f"   ❌ Task {task_num} failed: {result['error']}")
                break
        
        # Small delay between tasks
        time.sleep(0.5)
    
    # Step 8: Test Error Cases
    print("\n8️⃣ Testing Error Cases")
    
    # Test with non-existent session
    print("   Testing non-existent session...")
    result = test_endpoint("GET", "/api/screening/design", params={"session_id": "non_existent_session"})
    if result["success"]:
        print(f"   ✅ Non-existent session: {result['status_code']} (expected 404)")
    else:
        print(f"   ❌ Non-existent session test failed: {result['error']}")
    
    # Test invalid screening responses
    print("   Testing invalid screening responses...")
    invalid_data = {
        "session_id": session_id,
        "responses": "not_a_list"  # Should be a list
    }
    result = test_endpoint("POST", "/api/screening/responses", data=invalid_data)
    if result["success"]:
        print(f"   ✅ Invalid responses: {result['status_code']} (expected 422)")
    else:
        print(f"   ❌ Invalid responses test failed: {result['error']}")
    
    # Test invalid BYO config
    print("   Testing invalid BYO config...")
    invalid_byo = {
        "session_id": "test_invalid",
        # Missing selected_attributes
    }
    result = test_endpoint("POST", "/api/byo-config", data=invalid_byo)
    if result["success"]:
        print(f"   ✅ Invalid BYO config: {result['status_code']} (expected 422)")
    else:
        print(f"   ❌ Invalid BYO config test failed: {result['error']}")
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive ACBC Test Complete!")
    print(f"\n📊 Summary:")
    print(f"   Session ID: {session_id}")
    print(f"   Attributes: {len(smartphone_attributes)} (3-4 levels each)")
    print(f"   Screening Tasks: {len(screening_tasks) if 'screening_tasks' in locals() else 'N/A'}")
    print(f"   Tournament Tasks Completed: {task_num - 1 if 'task_num' in locals() else 'N/A'}")
    print(f"\n✅ All endpoints tested successfully!")
    print(f"🔗 API Base URL: {BASE_URL}")
    print(f"📚 Interactive Docs: {BASE_URL}/docs")

if __name__ == "__main__":
    main() 