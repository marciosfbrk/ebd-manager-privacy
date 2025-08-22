#!/usr/bin/env python3
"""
COMPREHENSIVE CALL CONTROL TEST
Testing all scenarios for the call control system
"""

import requests
import json
from datetime import datetime, date, timedelta
import uuid
import sys
import os

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
print(f"🔍 COMPREHENSIVE TESTING: Call Control System at {BASE_URL}")

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def success(self, test_name):
        self.passed += 1
        print(f"✅ {test_name}")
        
    def failure(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n=== COMPREHENSIVE TEST SUMMARY ===")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

results = TestResults()

def get_test_data():
    """Get turma and students for testing"""
    try:
        # Get turmas
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code != 200:
            return None, None
        turmas = response.json()
        if not turmas:
            return None, None
        turma_id = turmas[0]['id']
        
        # Get students
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
        if response.status_code != 200:
            return turma_id, None
        students = response.json()
        if not students:
            return turma_id, None
            
        return turma_id, students[0]['id']
    except:
        return None, None

def test_specific_scenarios():
    """Test the specific scenarios mentioned in the review request"""
    print("\n=== TESTING SPECIFIC REVIEW SCENARIOS ===")
    
    turma_id, student_id = get_test_data()
    if not turma_id or not student_id:
        results.failure("Get test data", "Could not get turma and student data")
        return
    
    print(f"📝 Using turma_id: {turma_id}")
    print(f"📝 Using student_id: {student_id}")
    
    # SCENARIO 1: Login as professor kell@ebd.com / 123456
    print("\n--- SCENARIO 1: Login as professor kell@ebd.com / 123456 ---")
    try:
        login_data = {"email": "kell@ebd.com", "senha": "123456"}
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('tipo') == 'professor':
                results.success("SCENARIO 1 - Login kell@ebd.com works as professor")
                kell_user_id = user_data.get('user_id')
            else:
                results.failure("SCENARIO 1", f"Expected professor, got {user_data.get('tipo')}")
                return
        else:
            results.failure("SCENARIO 1", f"Login failed: {response.status_code}")
            return
    except Exception as e:
        results.failure("SCENARIO 1", str(e))
        return
    
    # SCENARIO 2: Try to make a call for past date (2024-08-17)
    print("\n--- SCENARIO 2: Try call for past date 2024-08-17 ---")
    past_date = "2024-08-17"
    
    # First check if it's a Sunday
    try:
        date_obj = datetime.strptime(past_date, "%Y-%m-%d")
        is_sunday = date_obj.weekday() == 6
        print(f"📅 Date {past_date} is {'a Sunday' if is_sunday else 'NOT a Sunday'}")
    except:
        is_sunday = False
    
    # If not Sunday, try with a past Sunday
    if not is_sunday:
        past_date = "2024-08-18"  # This should be a Sunday
        print(f"📅 Using corrected past Sunday: {past_date}")
    
    bulk_data = [{
        "aluno_id": student_id,
        "status": "presente",
        "oferta": 10.0,
        "biblias_entregues": 1,
        "revistas_entregues": 1
    }]
    
    try:
        response = requests.post(
            f"{BASE_URL}/attendance/bulk/{turma_id}",
            params={
                "data": past_date,
                "user_tipo": "professor",
                "user_id": kell_user_id
            },
            json=bulk_data
        )
        
        if response.status_code == 403:
            results.success("SCENARIO 2 - Past date correctly BLOCKED for professor (403)")
            print(f"   ✅ Blocking message: {response.json().get('detail', 'No detail')}")
        elif response.status_code == 200:
            results.failure("SCENARIO 2", "CRITICAL: Professor was able to make call for past date!")
        else:
            results.failure("SCENARIO 2", f"Unexpected response {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("SCENARIO 2", str(e))
    
    # SCENARIO 3: Verify system configuration is active
    print("\n--- SCENARIO 3: Verify GET /api/system-config ---")
    try:
        response = requests.get(f"{BASE_URL}/system-config")
        if response.status_code == 200:
            config = response.json()
            results.success("SCENARIO 3 - GET /api/system-config works")
            
            if config.get('bloqueio_chamada_ativo') == True:
                results.success("SCENARIO 3 - Blocking is ACTIVE")
            else:
                results.failure("SCENARIO 3", f"Blocking should be active, got {config.get('bloqueio_chamada_ativo')}")
            
            print(f"   📋 Configuration: blocking={config.get('bloqueio_chamada_ativo')}, time={config.get('horario_bloqueio')}")
        else:
            results.failure("SCENARIO 3", f"Config endpoint failed: {response.status_code}")
    except Exception as e:
        results.failure("SCENARIO 3", str(e))
    
    # SCENARIO 4: Test with admin (should work)
    print("\n--- SCENARIO 4: Test admin access to past date ---")
    try:
        admin_login = {"email": "admin@ebd.com", "senha": "123456"}
        response = requests.post(f"{BASE_URL}/login", json=admin_login)
        if response.status_code == 200:
            admin_data = response.json()
            admin_user_id = admin_data.get('user_id')
            
            response = requests.post(
                f"{BASE_URL}/attendance/bulk/{turma_id}",
                params={
                    "data": past_date,
                    "user_tipo": "admin",
                    "user_id": admin_user_id
                },
                json=bulk_data
            )
            
            if response.status_code == 200:
                results.success("SCENARIO 4 - Admin can make calls for past dates")
            elif response.status_code == 400 and "domingo" in response.text.lower():
                results.success("SCENARIO 4 - Admin blocked only by Sunday validation (expected)")
            else:
                results.failure("SCENARIO 4", f"Admin should work, got {response.status_code}: {response.text}")
        else:
            results.failure("SCENARIO 4", "Admin login failed")
    except Exception as e:
        results.failure("SCENARIO 4", str(e))

def test_time_based_blocking():
    """Test time-based blocking logic"""
    print("\n=== TESTING TIME-BASED BLOCKING ===")
    
    turma_id, student_id = get_test_data()
    if not turma_id or not student_id:
        results.failure("Time test setup", "Could not get test data")
        return
    
    # Test with today's date (if it's a Sunday) or next Sunday
    today = date.today()
    if today.weekday() == 6:  # Today is Sunday
        test_date = today
    else:
        # Get next Sunday
        days_ahead = 6 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        test_date = today + timedelta(days_ahead)
    
    print(f"📅 Testing with date: {test_date} (today is {today})")
    
    bulk_data = [{
        "aluno_id": student_id,
        "status": "presente",
        "oferta": 5.0,
        "biblias_entregues": 0,
        "revistas_entregues": 1
    }]
    
    # Test professor access to today/future Sunday
    try:
        response = requests.post(
            f"{BASE_URL}/attendance/bulk/{turma_id}",
            params={
                "data": test_date.isoformat(),
                "user_tipo": "professor",
                "user_id": "test-professor-id"
            },
            json=bulk_data
        )
        
        current_time = datetime.now().time()
        blocking_time = datetime.strptime("13:00", "%H:%M").time()
        
        print(f"🕐 Current time: {current_time}")
        print(f"🕐 Blocking time: {blocking_time}")
        
        if test_date == today and current_time > blocking_time:
            # Should be blocked because it's after 13:00 today
            if response.status_code == 403:
                results.success("Time blocking - Professor correctly blocked after 13:00")
            else:
                results.failure("Time blocking", f"Should be blocked after 13:00, got {response.status_code}")
        elif test_date > today:
            # Future date - should work regardless of time
            if response.status_code == 200:
                results.success("Time blocking - Professor can make future calls")
            else:
                results.failure("Time blocking", f"Professor should access future dates, got {response.status_code}")
        else:
            # Today before 13:00 - should work
            if response.status_code == 200:
                results.success("Time blocking - Professor can make calls before 13:00")
            else:
                results.failure("Time blocking", f"Professor should work before 13:00, got {response.status_code}")
                
    except Exception as e:
        results.failure("Time blocking test", str(e))

def test_user_types():
    """Test different user types"""
    print("\n=== TESTING DIFFERENT USER TYPES ===")
    
    turma_id, student_id = get_test_data()
    if not turma_id or not student_id:
        results.failure("User types test setup", "Could not get test data")
        return
    
    past_sunday = "2024-12-15"  # A past Sunday
    bulk_data = [{"aluno_id": student_id, "status": "presente", "oferta": 5.0}]
    
    user_types = [
        ("admin", "Should work"),
        ("moderador", "Should work"), 
        ("professor", "Should be blocked")
    ]
    
    for user_type, expected in user_types:
        print(f"\n--- Testing user_tipo: {user_type} ({expected}) ---")
        try:
            response = requests.post(
                f"{BASE_URL}/attendance/bulk/{turma_id}",
                params={
                    "data": past_sunday,
                    "user_tipo": user_type,
                    "user_id": f"test-{user_type}-id"
                },
                json=bulk_data
            )
            
            if user_type in ['admin', 'moderador']:
                if response.status_code == 200:
                    results.success(f"User type {user_type} - Can make past calls (expected)")
                elif response.status_code == 400 and "domingo" in response.text.lower():
                    results.success(f"User type {user_type} - Blocked only by Sunday validation (acceptable)")
                else:
                    results.failure(f"User type {user_type}", f"Should work, got {response.status_code}: {response.text}")
            else:  # professor
                if response.status_code == 403:
                    results.success(f"User type {user_type} - Correctly blocked from past calls")
                else:
                    results.failure(f"User type {user_type}", f"Should be blocked, got {response.status_code}")
                    
        except Exception as e:
            results.failure(f"User type {user_type}", str(e))

def main():
    """Run comprehensive tests"""
    print("🔍 COMPREHENSIVE CALL CONTROL SYSTEM TEST")
    print("=" * 60)
    
    # Test the specific scenarios from the review request
    test_specific_scenarios()
    
    # Test time-based blocking logic
    test_time_based_blocking()
    
    # Test different user types
    test_user_types()
    
    # Show results
    results.summary()
    
    # Final assessment
    if results.failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        print("The call control system is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {results.failed} tests failed out of {results.passed + results.failed}")
        print("Review the errors above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)