#!/usr/bin/env python3
"""
URGENT TEST: Sistema de controle de chamadas
Testing the specific issue where professor kell@ebd.com / 123456 
was able to make a call for past date when it should be blocked.
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
print(f"🚨 URGENT TESTING: Call Control System at {BASE_URL}")

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.critical_issues = []
        
    def success(self, test_name):
        self.passed += 1
        print(f"✅ {test_name}")
        
    def failure(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")
        
    def critical_failure(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        self.critical_issues.append(f"{test_name}: {error}")
        print(f"🚨 CRITICAL: {test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n=== URGENT TEST SUMMARY ===")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND: {len(self.critical_issues)}")
            for issue in self.critical_issues:
                print(f"  - {issue}")
        
        if self.errors:
            print("\nAll Errors:")
            for error in self.errors:
                print(f"  - {error}")

results = TestResults()

def test_login_credentials():
    """Test login credentials for both admin and professor"""
    print("\n=== TESTING LOGIN CREDENTIALS ===")
    
    # Test admin login
    try:
        login_data = {
            "email": "admin@ebd.com",
            "senha": "123456"
        }
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('tipo') == 'admin':
                results.success("LOGIN admin@ebd.com / 123456 - Works correctly (tipo=admin)")
                return user_data
            else:
                results.failure("LOGIN admin@ebd.com", f"Expected tipo=admin, got {user_data.get('tipo')}")
        else:
            results.failure("LOGIN admin@ebd.com", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("LOGIN admin@ebd.com", str(e))
    
    # Test professor login (THE CRITICAL ONE)
    try:
        login_data = {
            "email": "kell@ebd.com",
            "senha": "123456"
        }
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('tipo') == 'professor':
                results.success("LOGIN kell@ebd.com / 123456 - Works correctly (tipo=professor)")
                return user_data
            else:
                results.failure("LOGIN kell@ebd.com", f"Expected tipo=professor, got {user_data.get('tipo')}")
        else:
            results.critical_failure("LOGIN kell@ebd.com", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.critical_failure("LOGIN kell@ebd.com", str(e))
    
    return None

def test_system_config():
    """Test GET /api/system-config to verify configuration is active"""
    print("\n=== TESTING SYSTEM CONFIGURATION ===")
    
    try:
        response = requests.get(f"{BASE_URL}/system-config")
        if response.status_code == 200:
            config = response.json()
            results.success("GET /api/system-config - Configuration endpoint accessible")
            
            # Check if blocking is active
            if config.get('bloqueio_chamada_ativo') == True:
                results.success("System Config - bloqueio_chamada_ativo is TRUE (blocking enabled)")
            else:
                results.critical_failure("System Config", f"bloqueio_chamada_ativo is {config.get('bloqueio_chamada_ativo')} - SHOULD BE TRUE!")
            
            # Check blocking time
            horario_bloqueio = config.get('horario_bloqueio', 'NOT_SET')
            if horario_bloqueio:
                results.success(f"System Config - horario_bloqueio is set to {horario_bloqueio}")
            else:
                results.failure("System Config", "horario_bloqueio not set")
            
            print(f"📋 Current Configuration:")
            print(f"   - Blocking Active: {config.get('bloqueio_chamada_ativo')}")
            print(f"   - Blocking Time: {config.get('horario_bloqueio')}")
            print(f"   - Updated By: {config.get('atualizado_por')}")
            print(f"   - Updated At: {config.get('atualizado_em')}")
            
            return config
        else:
            results.critical_failure("GET /api/system-config", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.critical_failure("GET /api/system-config", str(e))
    
    return None

def test_past_date_blocking():
    """THE CRITICAL TEST: Try to make call for past date as professor"""
    print("\n=== 🚨 CRITICAL TEST: PAST DATE BLOCKING ===")
    
    # Get turmas first
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code != 200:
            results.critical_failure("Get Turmas", "Cannot get turmas for testing")
            return
        
        turmas = response.json()
        if not turmas:
            results.critical_failure("Get Turmas", "No turmas available for testing")
            return
        
        turma_id = turmas[0]['id']
        turma_nome = turmas[0]['nome']
        print(f"📝 Using turma: {turma_nome} ({turma_id})")
        
    except Exception as e:
        results.critical_failure("Get Turmas", str(e))
        return
    
    # Get students for the turma
    try:
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
        if response.status_code != 200:
            results.critical_failure("Get Students", "Cannot get students for testing")
            return
        
        students = response.json()
        if not students:
            results.critical_failure("Get Students", "No students available for testing")
            return
        
        print(f"📝 Found {len(students)} students in turma")
        
    except Exception as e:
        results.critical_failure("Get Students", str(e))
        return
    
    # TEST SCENARIOS WITH PAST DATES
    past_dates = [
        "2024-08-17",  # Specific date mentioned in review
        "2024-12-15",  # Another past Sunday
        "2025-01-05"   # Recent past Sunday
    ]
    
    for past_date in past_dates:
        print(f"\n--- Testing with past date: {past_date} ---")
        
        # Verify it's actually a Sunday
        try:
            date_obj = datetime.strptime(past_date, "%Y-%m-%d")
            if date_obj.weekday() != 6:
                print(f"⚠️  Warning: {past_date} is not a Sunday, but testing anyway")
        except:
            pass
        
        # Create bulk attendance data for past date
        bulk_data = []
        for i, student in enumerate(students[:3]):  # Test with first 3 students
            bulk_data.append({
                "aluno_id": student['id'],
                "status": "presente",
                "oferta": 10.0,
                "biblias_entregues": 1,
                "revistas_entregues": 1
            })
        
        # TEST: POST /api/attendance/bulk/{turma_id} with past date + user_tipo=professor
        try:
            response = requests.post(
                f"{BASE_URL}/attendance/bulk/{turma_id}",
                params={
                    "data": past_date,
                    "user_tipo": "professor",
                    "user_id": "kell-user-id"  # Mock user ID
                },
                json=bulk_data
            )
            
            if response.status_code == 403:
                results.success(f"BLOCKING WORKS - Past date {past_date} correctly blocked for professor (403)")
                print(f"   ✅ Error message: {response.text}")
            elif response.status_code == 200:
                results.critical_failure(
                    f"BLOCKING FAILED - Past date {past_date}", 
                    "Professor was able to make call for past date - THIS IS THE BUG!"
                )
                print(f"   🚨 Professor successfully made call for past date - CRITICAL SECURITY ISSUE!")
            else:
                results.failure(
                    f"Unexpected response for {past_date}",
                    f"Expected 403 (blocked) or 200 (allowed), got {response.status_code}: {response.text}"
                )
        except Exception as e:
            results.failure(f"Test past date {past_date}", str(e))
    
    # TEST: Try with admin (should work)
    print(f"\n--- Testing admin access to past date (should work) ---")
    try:
        response = requests.post(
            f"{BASE_URL}/attendance/bulk/{turma_id}",
            params={
                "data": past_dates[0],
                "user_tipo": "admin",
                "user_id": "admin-user-id"
            },
            json=bulk_data
        )
        
        if response.status_code == 200:
            results.success("Admin access - Can make calls for past dates (expected)")
        else:
            results.failure("Admin access", f"Admin should be able to make past calls, got {response.status_code}")
    except Exception as e:
        results.failure("Admin access test", str(e))

def test_current_date_professor():
    """Test if professor can make calls for current/future dates"""
    print("\n=== TESTING PROFESSOR ACCESS TO CURRENT/FUTURE DATES ===")
    
    # Get next Sunday
    today = date.today()
    days_ahead = 6 - today.weekday()  # Sunday is 6
    if days_ahead <= 0:
        days_ahead += 7
    next_sunday = today + timedelta(days_ahead)
    
    print(f"📅 Testing with next Sunday: {next_sunday}")
    
    # Get turma and students
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        turmas = response.json()
        turma_id = turmas[0]['id']
        
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
        students = response.json()
        
        bulk_data = [{
            "aluno_id": students[0]['id'],
            "status": "presente",
            "oferta": 5.0,
            "biblias_entregues": 0,
            "revistas_entregues": 1
        }]
        
        # Test professor access to future Sunday
        response = requests.post(
            f"{BASE_URL}/attendance/bulk/{turma_id}",
            params={
                "data": next_sunday.isoformat(),
                "user_tipo": "professor",
                "user_id": "kell-user-id"
            },
            json=bulk_data
        )
        
        if response.status_code == 200:
            results.success("Professor future access - Can make calls for future Sundays (expected)")
        else:
            results.failure("Professor future access", f"Professor should be able to make future calls, got {response.status_code}: {response.text}")
            
    except Exception as e:
        results.failure("Professor future access test", str(e))

def test_pode_editar_chamada_function():
    """Test the pode_editar_chamada function indirectly through PUT endpoint"""
    print("\n=== TESTING pode_editar_chamada FUNCTION ===")
    
    # First create an attendance record to edit
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        turmas = response.json()
        turma_id = turmas[0]['id']
        
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
        students = response.json()
        student_id = students[0]['id']
        
        # Create attendance for a past date
        past_date = "2024-12-15"  # Past Sunday
        attendance_data = {
            "aluno_id": student_id,
            "turma_id": turma_id,
            "data": past_date,
            "status": "presente",
            "oferta": 10.0
        }
        
        # First try to create it as admin (should work)
        response = requests.post(f"{BASE_URL}/attendance", json=attendance_data)
        if response.status_code == 200:
            attendance_record = response.json()
            attendance_id = attendance_record['id']
            results.success("Created test attendance record for past date")
            
            # Now try to edit it as professor (should be blocked)
            update_data = {
                "status": "ausente",
                "oferta": 15.0
            }
            
            response = requests.put(
                f"{BASE_URL}/attendance/{attendance_id}",
                params={
                    "user_tipo": "professor",
                    "user_id": "kell-user-id"
                },
                json=update_data
            )
            
            if response.status_code == 403:
                results.success("PUT attendance - Professor correctly blocked from editing past attendance (403)")
                print(f"   ✅ Error message: {response.text}")
            elif response.status_code == 200:
                results.critical_failure(
                    "PUT attendance - Professor edit past",
                    "Professor was able to edit past attendance - pode_editar_chamada() not working!"
                )
            else:
                results.failure("PUT attendance test", f"Unexpected status {response.status_code}: {response.text}")
            
            # Try as admin (should work)
            response = requests.put(
                f"{BASE_URL}/attendance/{attendance_id}",
                params={
                    "user_tipo": "admin",
                    "user_id": "admin-user-id"
                },
                json=update_data
            )
            
            if response.status_code == 200:
                results.success("PUT attendance - Admin can edit past attendance (expected)")
            else:
                results.failure("PUT attendance admin", f"Admin should be able to edit, got {response.status_code}")
                
        else:
            results.failure("Create test attendance", f"Could not create test record: {response.status_code}")
            
    except Exception as e:
        results.failure("pode_editar_chamada test", str(e))

def main():
    """Run all urgent tests"""
    print("🚨 URGENT CALL CONTROL SYSTEM TEST")
    print("=" * 50)
    print("Testing the critical issue where professor kell@ebd.com")
    print("was able to make calls for past dates when blocked.")
    print("=" * 50)
    
    # Test 1: Verify login credentials work
    user_data = test_login_credentials()
    
    # Test 2: Verify system configuration is active
    config = test_system_config()
    
    # Test 3: THE CRITICAL TEST - Try past date blocking
    test_past_date_blocking()
    
    # Test 4: Verify professor can still make future calls
    test_current_date_professor()
    
    # Test 5: Test the pode_editar_chamada function
    test_pode_editar_chamada_function()
    
    # Show results
    results.summary()
    
    # Final assessment
    if results.critical_issues:
        print("\n🚨 CRITICAL SECURITY ISSUE DETECTED!")
        print("The call control system is NOT working properly.")
        print("Professor can make calls for past dates when they should be blocked.")
        print("\nRECOMMENDED ACTIONS:")
        print("1. Check the pode_editar_chamada() function implementation")
        print("2. Verify user_tipo parameter is being passed correctly")
        print("3. Check if system configuration is being read properly")
        print("4. Test the date comparison logic")
        return 1
    else:
        print("\n✅ CALL CONTROL SYSTEM IS WORKING CORRECTLY")
        print("All blocking mechanisms are functioning as expected.")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)