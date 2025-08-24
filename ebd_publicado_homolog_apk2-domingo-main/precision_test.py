#!/usr/bin/env python3
"""
Specific test for the floating point precision issue reported by user
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
print(f"Testing backend at: {BASE_URL}")

def test_exact_scenario():
    """Test the exact scenario reported by user"""
    
    # Initialize sample data first
    print("1. Initializing sample data...")
    response = requests.post(f"{BASE_URL}/init-sample-data")
    if response.status_code != 200:
        print(f"❌ Failed to initialize data: {response.text}")
        return
    print("✅ Sample data initialized")
    
    # Get a turma
    response = requests.get(f"{BASE_URL}/turmas")
    if response.status_code != 200:
        print(f"❌ Failed to get turmas: {response.text}")
        return
    
    turmas = response.json()
    turma_id = turmas[0]['id']
    turma_nome = turmas[0]['nome']
    print(f"Using turma: {turma_nome}")
    
    # Get students for this turma
    response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
    if response.status_code != 200:
        print(f"❌ Failed to get students: {response.text}")
        return
    
    students = response.json()
    if len(students) < 2:
        print(f"❌ Need at least 2 students, found {len(students)}")
        return
    
    print(f"Found {len(students)} students in turma")
    
    # Test the exact scenario: 2 students present, total offer 17.00
    test_date = "2025-07-13"  # Sunday as specified in review
    
    print(f"\n2. Testing scenario: 2 students present, total offer 17.00 on {test_date}")
    
    # Create bulk attendance: 2 students, each with 8.50 offer
    bulk_data = []
    for i, student in enumerate(students[:2]):
        bulk_data.append({
            "aluno_id": student['id'],
            "status": "presente",
            "oferta": 8.50,  # Each gets exactly 8.50
            "biblias_entregues": 0,
            "revistas_entregues": 0
        })
    
    # Save bulk attendance
    response = requests.post(f"{BASE_URL}/attendance/bulk/{turma_id}", 
                           params={"data": test_date},
                           json=bulk_data)
    
    if response.status_code != 200:
        print(f"❌ Failed to save bulk attendance: {response.text}")
        return
    
    print("✅ Bulk attendance saved successfully")
    
    # Test reload scenario - GET attendance data
    print(f"\n3. Testing reload scenario - GET /api/attendance")
    response = requests.get(f"{BASE_URL}/attendance", 
                          params={"turma_id": turma_id, "data": test_date})
    
    if response.status_code != 200:
        print(f"❌ Failed to get attendance: {response.text}")
        return
    
    attendance_records = response.json()
    individual_offers = [record.get('oferta', 0) for record in attendance_records]
    total_sum = sum(individual_offers)
    
    print(f"Individual offers after reload: {individual_offers}")
    print(f"Sum of individual offers: {total_sum}")
    
    # Check if sum is exactly 17.00
    if total_sum == 17.00:
        print("✅ PASS: Sum of offers is exactly 17.00 (no precision loss)")
    else:
        print(f"❌ FAIL: Sum is {total_sum}, expected 17.00 (precision issue detected)")
    
    # Test dashboard report
    print(f"\n4. Testing dashboard report")
    response = requests.get(f"{BASE_URL}/reports/dashboard", 
                          params={"data": test_date})
    
    if response.status_code != 200:
        print(f"❌ Failed to get dashboard: {response.text}")
        return
    
    reports = response.json()
    test_report = None
    for report in reports:
        if report['turma_id'] == turma_id:
            test_report = report
            break
    
    if test_report:
        dashboard_total = test_report['total_ofertas']
        print(f"Dashboard total_ofertas: {dashboard_total}")
        
        if dashboard_total == 17.00:
            print("✅ PASS: Dashboard shows exactly 17.00")
        else:
            print(f"❌ FAIL: Dashboard shows {dashboard_total}, expected 17.00")
    else:
        print("❌ No report found for test turma")
    
    print(f"\n=== FINAL RESULT ===")
    if total_sum == 17.00 and (test_report and test_report['total_ofertas'] == 17.00):
        print("🎉 SUCCESS: Floating point precision issue has been FIXED!")
        print("   - User enters 17.00")
        print("   - After save and reload, value remains 17.00")
        print("   - Dashboard shows 17.00")
    else:
        print("❌ ISSUE PERSISTS: Floating point precision problem still exists")

if __name__ == "__main__":
    test_exact_scenario()