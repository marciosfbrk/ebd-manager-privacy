#!/usr/bin/env python3
"""
Additional edge case tests for floating point precision
"""

import requests
import json

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=')[1].strip()
    except:
        pass
    return "http://localhost:8001"

BASE_URL = get_backend_url() + "/api"

def test_edge_cases():
    """Test various edge cases for floating point precision"""
    
    # Get turma and students
    response = requests.get(f"{BASE_URL}/turmas")
    turmas = response.json()
    turma_id = turmas[0]['id']
    
    response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
    students = response.json()
    
    test_cases = [
        {"name": "Original issue: 17.00", "individual": 8.50, "expected_total": 17.00},
        {"name": "Edge case: 10.01", "individual": 5.005, "expected_total": 10.01},
        {"name": "Edge case: 0.03", "individual": 0.015, "expected_total": 0.03},
        {"name": "Edge case: 99.99", "individual": 49.995, "expected_total": 99.99},
    ]
    
    for i, test_case in enumerate(test_cases):
        test_date = f"2025-07-{13 + i*7}"  # Different Sundays
        print(f"\n=== {test_case['name']} ===")
        print(f"Testing on {test_date}")
        
        # Create bulk attendance
        bulk_data = []
        for j, student in enumerate(students[:2]):
            bulk_data.append({
                "aluno_id": student['id'],
                "status": "presente",
                "oferta": test_case['individual'],
                "biblias_entregues": 0,
                "revistas_entregues": 0
            })
        
        # Save bulk attendance
        response = requests.post(f"{BASE_URL}/attendance/bulk/{turma_id}", 
                               params={"data": test_date},
                               json=bulk_data)
        
        if response.status_code != 200:
            print(f"❌ Failed to save: {response.text}")
            continue
        
        # Check reload
        response = requests.get(f"{BASE_URL}/attendance", 
                              params={"turma_id": turma_id, "data": test_date})
        
        if response.status_code != 200:
            print(f"❌ Failed to reload: {response.text}")
            continue
        
        attendance_records = response.json()
        individual_offers = [record.get('oferta', 0) for record in attendance_records]
        total_sum = sum(individual_offers)
        
        print(f"Individual offers: {individual_offers}")
        print(f"Sum: {total_sum}")
        print(f"Expected: {test_case['expected_total']}")
        
        # Check dashboard
        response = requests.get(f"{BASE_URL}/reports/dashboard", 
                              params={"data": test_date})
        
        if response.status_code == 200:
            reports = response.json()
            test_report = next((r for r in reports if r['turma_id'] == turma_id), None)
            if test_report:
                dashboard_total = test_report['total_ofertas']
                print(f"Dashboard total: {dashboard_total}")
                
                # Check if values are close enough (within 0.01 tolerance for floating point)
                if abs(total_sum - test_case['expected_total']) < 0.01 and abs(dashboard_total - test_case['expected_total']) < 0.01:
                    print("✅ PASS: Values are within acceptable precision")
                else:
                    print("❌ FAIL: Precision issue detected")
            else:
                print("❌ No dashboard report found")
        else:
            print(f"❌ Dashboard failed: {response.text}")

if __name__ == "__main__":
    test_edge_cases()