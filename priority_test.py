#!/usr/bin/env python3
"""
Priority Test Suite for EBD Manager System - Focus on Corrected Endpoints
Tests the specific endpoints mentioned in the review request with 2025-07-13 date
"""

import requests
import json
from datetime import datetime, date
import uuid

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

# Test with specific date from review request
TEST_DATE = "2025-07-13"  # Sunday as specified in review request
NON_SUNDAY_DATE = "2025-07-14"  # Monday for validation tests

print(f"Using test date: {TEST_DATE} (should be Sunday)")
print(f"Using non-Sunday date: {NON_SUNDAY_DATE} (for validation)")

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
        print(f"\n=== PRIORITY TEST SUMMARY ===")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

results = TestResults()

def verify_sunday_date():
    """Verify that 2025-07-13 is indeed a Sunday"""
    try:
        date_obj = datetime.strptime(TEST_DATE, "%Y-%m-%d").date()
        is_sunday = date_obj.weekday() == 6  # Sunday is 6
        if is_sunday:
            results.success("Date validation - 2025-07-13 is Sunday")
            return True
        else:
            results.failure("Date validation", f"2025-07-13 is not Sunday (weekday: {date_obj.weekday()})")
            return False
    except Exception as e:
        results.failure("Date validation", str(e))
        return False

def test_1_init_sample_data():
    """TESTE PRIORITÁRIO 1: POST /api/init-sample-data"""
    print("\n🔥 PRIORITY TEST 1: Initialize Sample Data")
    try:
        response = requests.post(f"{BASE_URL}/init-sample-data")
        if response.status_code == 200:
            data = response.json()
            if "turmas" in data and "alunos" in data and data["turmas"] == 3 and data["alunos"] == 4:
                results.success("POST /api/init-sample-data - Creates correct turmas and students")
                return data
            else:
                results.failure("POST /api/init-sample-data", f"Incorrect data created: {data}")
        else:
            results.failure("POST /api/init-sample-data", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/init-sample-data", str(e))
    return None

def test_2_bulk_attendance_critical():
    """TESTE PRIORITÁRIO 2: POST /api/attendance/bulk/{turma_id}?data=2025-07-13"""
    print("\n🔥 PRIORITY TEST 2: Bulk Attendance with 2025-07-13")
    
    # Get turmas first
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code != 200:
            results.failure("Bulk Attendance Setup", "Could not get turmas")
            return
        
        turmas = response.json()
        if not turmas:
            results.failure("Bulk Attendance Setup", "No turmas found")
            return
        
        turma_id = turmas[0]['id']
        
        # Get students for this turma
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
        if response.status_code != 200:
            results.failure("Bulk Attendance Setup", "Could not get students")
            return
        
        students = response.json()
        if not students:
            results.failure("Bulk Attendance Setup", "No students found for turma")
            return
        
        # Create bulk attendance data for Sunday 2025-07-13
        bulk_data = []
        for i, student in enumerate(students[:2]):  # Test with first 2 students
            bulk_data.append({
                "aluno_id": student['id'],
                "status": "presente" if i == 0 else "visitante",
                "oferta": 15.0 if i == 0 else 5.0,
                "biblias_entregues": 1 if i == 0 else 0,
                "revistas_entregues": 1 if i == 0 else 1
            })
        
        # Test POST /api/attendance/bulk/{turma_id} with 2025-07-13
        response = requests.post(f"{BASE_URL}/attendance/bulk/{turma_id}", 
                               params={"data": TEST_DATE},
                               json=bulk_data)
        if response.status_code == 200:
            result = response.json()
            if "message" in result:
                results.success(f"POST /api/attendance/bulk/{{turma_id}} - Saves attendance for {TEST_DATE}")
                
                # Verify data was saved by retrieving it
                response = requests.get(f"{BASE_URL}/attendance", 
                                      params={"turma_id": turma_id, "data": TEST_DATE})
                if response.status_code == 200:
                    saved_attendance = response.json()
                    if len(saved_attendance) == len(bulk_data):
                        results.success("Bulk Attendance Verification - Data correctly saved and retrievable")
                    else:
                        results.failure("Bulk Attendance Verification", f"Expected {len(bulk_data)} records, found {len(saved_attendance)}")
                else:
                    results.failure("Bulk Attendance Verification", "Could not retrieve saved data")
            else:
                results.failure("POST /api/attendance/bulk/{turma_id}", f"Invalid response: {result}")
        else:
            results.failure("POST /api/attendance/bulk/{turma_id}", f"Status {response.status_code}: {response.text}")
        
        return turma_id, students
        
    except Exception as e:
        results.failure("Bulk Attendance", str(e))
        return None, None

def test_3_student_transfer_critical(students):
    """TESTE PRIORITÁRIO 3: POST /api/students/{id}/transfer"""
    print("\n🔥 PRIORITY TEST 3: Student Transfer")
    
    if not students or len(students) < 1:
        results.failure("Student Transfer", "No students available for transfer test")
        return
    
    try:
        # Get all turmas
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code != 200:
            results.failure("Student Transfer Setup", "Could not get turmas")
            return
        
        turmas = response.json()
        if len(turmas) < 2:
            results.failure("Student Transfer Setup", "Need at least 2 turmas for transfer test")
            return
        
        student = students[0]
        current_turma_id = student['turma_id']
        new_turma = next((t for t in turmas if t['id'] != current_turma_id), None)
        
        if not new_turma:
            results.failure("Student Transfer Setup", "Could not find different turma for transfer")
            return
        
        # Test transfer
        transfer_data = {"nova_turma_id": new_turma['id']}
        response = requests.post(f"{BASE_URL}/students/{student['id']}/transfer", 
                               json=transfer_data)
        if response.status_code == 200:
            updated_student = response.json()
            if updated_student['turma_id'] == new_turma['id']:
                results.success("POST /api/students/{id}/transfer - Successfully transfers student between turmas")
            else:
                results.failure("POST /api/students/{id}/transfer", f"Transfer failed: turma_id still {updated_student['turma_id']}")
        else:
            results.failure("POST /api/students/{id}/transfer", f"Status {response.status_code}: {response.text}")
            
    except Exception as e:
        results.failure("Student Transfer", str(e))

def test_4_sunday_validation_critical():
    """TESTE PRIORITÁRIO 4: Sunday Validation for 2025-07-13"""
    print("\n🔥 PRIORITY TEST 4: Sunday Validation")
    
    # Test that 2025-07-13 is accepted as Sunday
    try:
        # Get a student and turma for testing
        response = requests.get(f"{BASE_URL}/students")
        if response.status_code != 200:
            results.failure("Sunday Validation Setup", "Could not get students")
            return
        
        students = response.json()
        if not students:
            results.failure("Sunday Validation Setup", "No students found")
            return
        
        student = students[0]
        
        # Test attendance creation with 2025-07-13 (should work)
        attendance_data = {
            "aluno_id": student['id'],
            "turma_id": student['turma_id'],
            "data": TEST_DATE,
            "status": "presente",
            "oferta": 10.0
        }
        response = requests.post(f"{BASE_URL}/attendance", json=attendance_data)
        if response.status_code == 200:
            results.success(f"Sunday Validation - {TEST_DATE} accepted as valid Sunday")
        else:
            results.failure("Sunday Validation", f"2025-07-13 rejected: Status {response.status_code}: {response.text}")
        
        # Test with non-Sunday date (should fail)
        attendance_data["data"] = NON_SUNDAY_DATE
        response = requests.post(f"{BASE_URL}/attendance", json=attendance_data)
        if response.status_code == 400:
            results.success(f"Sunday Validation - {NON_SUNDAY_DATE} correctly rejected as non-Sunday")
        else:
            results.failure("Sunday Validation", f"Non-Sunday date should be rejected, got status {response.status_code}")
            
    except Exception as e:
        results.failure("Sunday Validation", str(e))

def test_5_crud_students_critical():
    """TESTE PRIORITÁRIO 5: CRUD Students Operations"""
    print("\n🔥 PRIORITY TEST 5: CRUD Students")
    
    try:
        # Get a turma for student creation
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code != 200:
            results.failure("CRUD Students Setup", "Could not get turmas")
            return
        
        turmas = response.json()
        if not turmas:
            results.failure("CRUD Students Setup", "No turmas found")
            return
        
        turma_id = turmas[0]['id']
        
        # Test CREATE student
        new_student = {
            "nome_completo": "Ana Carolina Silva",
            "data_nascimento": "1992-03-25",
            "contato": "ana.carolina@email.com",
            "turma_id": turma_id
        }
        response = requests.post(f"{BASE_URL}/students", json=new_student)
        if response.status_code == 200:
            student = response.json()
            student_id = student['id']
            results.success("POST /api/students - Create student successfully")
            
            # Test UPDATE student
            update_data = {
                "nome_completo": "Ana Carolina Silva Santos",
                "contato": "ana.santos@email.com"
            }
            response = requests.put(f"{BASE_URL}/students/{student_id}", json=update_data)
            if response.status_code == 200:
                updated_student = response.json()
                if updated_student['nome_completo'] == update_data['nome_completo']:
                    results.success("PUT /api/students/{id} - Update student successfully")
                else:
                    results.failure("PUT /api/students/{id}", "Update did not apply correctly")
            else:
                results.failure("PUT /api/students/{id}", f"Status {response.status_code}: {response.text}")
            
            # Test DELETE student (soft delete)
            response = requests.delete(f"{BASE_URL}/students/{student_id}")
            if response.status_code == 200:
                # Verify soft delete by checking if student is not in active list
                response = requests.get(f"{BASE_URL}/students")
                if response.status_code == 200:
                    active_students = response.json()
                    active_ids = [s['id'] for s in active_students]
                    if student_id not in active_ids:
                        results.success("DELETE /api/students/{id} - Soft delete student successfully")
                    else:
                        results.failure("DELETE /api/students/{id}", "Student still appears in active list")
                else:
                    results.failure("DELETE /api/students/{id}", "Could not verify soft delete")
            else:
                results.failure("DELETE /api/students/{id}", f"Status {response.status_code}: {response.text}")
                
        else:
            results.failure("POST /api/students", f"Status {response.status_code}: {response.text}")
            
    except Exception as e:
        results.failure("CRUD Students", str(e))

def main():
    """Run priority tests as specified in review request"""
    print("=== EBD MANAGER PRIORITY TEST SUITE ===")
    print("Testing corrected endpoints with focus on 2025-07-13 date\n")
    
    # Verify the test date is Sunday
    if not verify_sunday_date():
        print("❌ CRITICAL: Test date validation failed")
        results.summary()
        return
    
    # Priority Test 1: Initialize sample data (MUST BE FIRST)
    test_1_init_sample_data()
    
    # Priority Test 2: Bulk attendance with 2025-07-13 (CRITICAL)
    turma_id, students = test_2_bulk_attendance_critical()
    
    # Priority Test 3: Student transfer (CRITICAL)
    test_3_student_transfer_critical(students)
    
    # Priority Test 4: Sunday validation (CRITICAL)
    test_4_sunday_validation_critical()
    
    # Priority Test 5: CRUD Students (CRITICAL)
    test_5_crud_students_critical()
    
    # Final summary
    results.summary()
    
    if results.failed == 0:
        print("\n🎉 ALL PRIORITY TESTS PASSED!")
        print("✅ Corrections have resolved serialization and functionality issues")
        print("✅ System ready for production use")
    else:
        print(f"\n⚠️  {results.failed} priority test(s) failed - needs attention")

if __name__ == "__main__":
    main()