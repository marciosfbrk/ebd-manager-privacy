#!/usr/bin/env python3
"""
Backend Test Suite for EBD Manager System
Tests all API endpoints with focus on critical validations
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
print(f"Testing backend at: {BASE_URL}")

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
        print(f"\n=== TEST SUMMARY ===")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

results = TestResults()

def get_next_sunday():
    """Get next Sunday date for testing"""
    today = date.today()
    days_ahead = 6 - today.weekday()  # Sunday is 6
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days_ahead)

def get_non_sunday():
    """Get a non-Sunday date for testing validation"""
    today = date.today()
    if today.weekday() != 6:  # If not Sunday
        return today
    return today + timedelta(days=1)  # Monday

# Test data
SUNDAY_DATE = get_next_sunday()
NON_SUNDAY_DATE = get_non_sunday()

print(f"Using Sunday date for tests: {SUNDAY_DATE}")
print(f"Using non-Sunday date for validation tests: {NON_SUNDAY_DATE}")

def test_init_sample_data():
    """Test POST /api/init-sample-data - MUST TEST FIRST"""
    try:
        response = requests.post(f"{BASE_URL}/init-sample-data")
        if response.status_code == 200:
            data = response.json()
            if "turmas" in data and "alunos" in data:
                results.success("POST /api/init-sample-data - Initialize sample data")
                return True
            else:
                results.failure("POST /api/init-sample-data", f"Invalid response format: {data}")
        else:
            results.failure("POST /api/init-sample-data", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/init-sample-data", str(e))
    return False

def test_turmas_crud():
    """Test CRUD operations for turmas"""
    turma_id = None
    
    # Test GET /api/turmas (list)
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code == 200:
            turmas = response.json()
            if isinstance(turmas, list) and len(turmas) >= 3:
                # Check for expected turmas from sample data
                turma_names = [t['nome'] for t in turmas]
                expected_names = ['Gênesis', 'Primários', 'Juvenil']
                if all(name in turma_names for name in expected_names):
                    results.success("GET /api/turmas - List turmas with sample data")
                    turma_id = turmas[0]['id']  # Use first turma for other tests
                else:
                    results.failure("GET /api/turmas", f"Missing expected turmas. Found: {turma_names}")
            else:
                results.failure("GET /api/turmas", f"Expected list with 3+ turmas, got: {turmas}")
        else:
            results.failure("GET /api/turmas", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/turmas", str(e))
    
    # Test POST /api/turmas (create)
    new_turma_id = None
    try:
        new_turma = {
            "nome": "Teste Turma",
            "descricao": "Turma para testes"
        }
        response = requests.post(f"{BASE_URL}/turmas", json=new_turma)
        if response.status_code == 200:
            turma = response.json()
            if turma['nome'] == new_turma['nome'] and 'id' in turma:
                # Verify UUID format
                try:
                    uuid.UUID(turma['id'])
                    results.success("POST /api/turmas - Create turma with UUID")
                    new_turma_id = turma['id']
                except ValueError:
                    results.failure("POST /api/turmas", f"Invalid UUID format: {turma['id']}")
            else:
                results.failure("POST /api/turmas", f"Invalid response: {turma}")
        else:
            results.failure("POST /api/turmas", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/turmas", str(e))
    
    # Test PUT /api/turmas/{id} (update)
    if new_turma_id:
        try:
            update_data = {
                "nome": "Turma Atualizada",
                "descricao": "Descrição atualizada"
            }
            response = requests.put(f"{BASE_URL}/turmas/{new_turma_id}", json=update_data)
            if response.status_code == 200:
                turma = response.json()
                if turma['nome'] == update_data['nome']:
                    results.success("PUT /api/turmas/{id} - Update turma")
                else:
                    results.failure("PUT /api/turmas/{id}", f"Update failed: {turma}")
            else:
                results.failure("PUT /api/turmas/{id}", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("PUT /api/turmas/{id}", str(e))
    
    # Test DELETE /api/turmas/{id} (soft delete)
    if new_turma_id:
        try:
            response = requests.delete(f"{BASE_URL}/turmas/{new_turma_id}")
            if response.status_code == 200:
                # Verify it's soft deleted (not in active list)
                response = requests.get(f"{BASE_URL}/turmas")
                if response.status_code == 200:
                    turmas = response.json()
                    active_ids = [t['id'] for t in turmas]
                    if new_turma_id not in active_ids:
                        results.success("DELETE /api/turmas/{id} - Soft delete turma")
                    else:
                        results.failure("DELETE /api/turmas/{id}", "Turma still appears in active list")
                else:
                    results.failure("DELETE /api/turmas/{id}", "Could not verify soft delete")
            else:
                results.failure("DELETE /api/turmas/{id}", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("DELETE /api/turmas/{id}", str(e))
    
    return turma_id

def test_students_crud(turma_id):
    """Test CRUD operations for students"""
    if not turma_id:
        results.failure("Students CRUD", "No valid turma_id available")
        return None
    
    student_id = None
    
    # Test GET /api/students (list)
    try:
        response = requests.get(f"{BASE_URL}/students")
        if response.status_code == 200:
            students = response.json()
            if isinstance(students, list) and len(students) >= 4:
                # Check for expected students from sample data
                student_names = [s['nome_completo'] for s in students]
                expected_names = ['Márcio Ferreira', 'Késia Ferreira', 'Gustavo Ferreira', 'Gael Ferreira']
                if all(name in student_names for name in expected_names):
                    results.success("GET /api/students - List students with sample data")
                    student_id = students[0]['id']
                else:
                    results.failure("GET /api/students", f"Missing expected students. Found: {student_names}")
            else:
                results.failure("GET /api/students", f"Expected list with 4+ students, got: {len(students) if isinstance(students, list) else 'not a list'}")
        else:
            results.failure("GET /api/students", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/students", str(e))
    
    # Test POST /api/students (create)
    new_student_id = None
    try:
        new_student = {
            "nome_completo": "João Silva",
            "data_nascimento": "1990-01-15",
            "contato": "joao@email.com",
            "turma_id": turma_id
        }
        response = requests.post(f"{BASE_URL}/students", json=new_student)
        if response.status_code == 200:
            student = response.json()
            if student['nome_completo'] == new_student['nome_completo'] and 'id' in student:
                # Verify UUID format
                try:
                    uuid.UUID(student['id'])
                    results.success("POST /api/students - Create student with UUID")
                    new_student_id = student['id']
                except ValueError:
                    results.failure("POST /api/students", f"Invalid UUID format: {student['id']}")
            else:
                results.failure("POST /api/students", f"Invalid response: {student}")
        else:
            results.failure("POST /api/students", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/students", str(e))
    
    # Test validation: create student with invalid turma_id
    try:
        invalid_student = {
            "nome_completo": "Maria Invalid",
            "data_nascimento": "1995-05-20",
            "contato": "maria@email.com",
            "turma_id": str(uuid.uuid4())  # Non-existent turma
        }
        response = requests.post(f"{BASE_URL}/students", json=invalid_student)
        if response.status_code == 404:
            results.success("POST /api/students - Validation: reject invalid turma_id")
        else:
            results.failure("POST /api/students - Validation", f"Should reject invalid turma_id, got status {response.status_code}")
    except Exception as e:
        results.failure("POST /api/students - Validation", str(e))
    
    # Test PUT /api/students/{id} (update)
    if new_student_id:
        try:
            update_data = {
                "nome_completo": "João Silva Atualizado",
                "contato": "joao.novo@email.com"
            }
            response = requests.put(f"{BASE_URL}/students/{new_student_id}", json=update_data)
            if response.status_code == 200:
                student = response.json()
                if student['nome_completo'] == update_data['nome_completo']:
                    results.success("PUT /api/students/{id} - Update student")
                else:
                    results.failure("PUT /api/students/{id}", f"Update failed: {student}")
            else:
                results.failure("PUT /api/students/{id}", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("PUT /api/students/{id}", str(e))
    
    # Test POST /api/students/{id}/transfer
    if new_student_id:
        # Get another turma for transfer
        try:
            response = requests.get(f"{BASE_URL}/turmas")
            if response.status_code == 200:
                turmas = response.json()
                other_turma = next((t for t in turmas if t['id'] != turma_id), None)
                if other_turma:
                    transfer_data = {"nova_turma_id": other_turma['id']}
                    response = requests.post(f"{BASE_URL}/students/{new_student_id}/transfer", 
                                           json=transfer_data)
                    if response.status_code == 200:
                        results.success("POST /api/students/{id}/transfer - Transfer student")
                    else:
                        results.failure("POST /api/students/{id}/transfer", f"Status {response.status_code}: {response.text}")
                else:
                    results.failure("POST /api/students/{id}/transfer", "No other turma available for transfer")
        except Exception as e:
            results.failure("POST /api/students/{id}/transfer", str(e))
    
    # Test DELETE /api/students/{id} (soft delete)
    if new_student_id:
        try:
            response = requests.delete(f"{BASE_URL}/students/{new_student_id}")
            if response.status_code == 200:
                # Verify it's soft deleted
                response = requests.get(f"{BASE_URL}/students")
                if response.status_code == 200:
                    students = response.json()
                    active_ids = [s['id'] for s in students]
                    if new_student_id not in active_ids:
                        results.success("DELETE /api/students/{id} - Soft delete student")
                    else:
                        results.failure("DELETE /api/students/{id}", "Student still appears in active list")
                else:
                    results.failure("DELETE /api/students/{id}", "Could not verify soft delete")
            else:
                results.failure("DELETE /api/students/{id}", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("DELETE /api/students/{id}", str(e))
    
    return student_id

def test_attendance_system(turma_id, student_id):
    """Test attendance system with critical validations"""
    if not turma_id or not student_id:
        results.failure("Attendance System", "No valid turma_id or student_id available")
        return
    
    # Test POST /api/attendance with Sunday validation
    try:
        attendance_data = {
            "aluno_id": student_id,
            "turma_id": turma_id,
            "data": SUNDAY_DATE.isoformat(),
            "status": "presente",
            "oferta": 10.50,
            "biblias_entregues": 1,
            "revistas_entregues": 1
        }
        response = requests.post(f"{BASE_URL}/attendance", json=attendance_data)
        if response.status_code == 200:
            attendance = response.json()
            if 'id' in attendance and attendance['status'] == 'presente':
                results.success("POST /api/attendance - Create attendance on Sunday")
            else:
                results.failure("POST /api/attendance", f"Invalid response: {attendance}")
        else:
            results.failure("POST /api/attendance", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/attendance", str(e))
    
    # Test Sunday validation - should reject non-Sunday dates
    try:
        invalid_attendance = {
            "aluno_id": student_id,
            "turma_id": turma_id,
            "data": NON_SUNDAY_DATE.isoformat(),
            "status": "presente"
        }
        response = requests.post(f"{BASE_URL}/attendance", json=invalid_attendance)
        if response.status_code == 400:
            results.success("POST /api/attendance - Validation: reject non-Sunday dates")
        else:
            results.failure("POST /api/attendance - Validation", f"Should reject non-Sunday, got status {response.status_code}")
    except Exception as e:
        results.failure("POST /api/attendance - Validation", str(e))
    
    # Test GET /api/attendance
    try:
        response = requests.get(f"{BASE_URL}/attendance", params={"turma_id": turma_id, "data": SUNDAY_DATE.isoformat()})
        if response.status_code == 200:
            attendance_list = response.json()
            if isinstance(attendance_list, list):
                results.success("GET /api/attendance - List attendance by turma and date")
            else:
                results.failure("GET /api/attendance", f"Expected list, got: {attendance_list}")
        else:
            results.failure("GET /api/attendance", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/attendance", str(e))

def test_bulk_attendance(turma_id):
    """Test bulk attendance endpoint"""
    if not turma_id:
        results.failure("Bulk Attendance", "No valid turma_id available")
        return
    
    # Get students for the turma
    try:
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
        if response.status_code != 200:
            results.failure("Bulk Attendance", "Could not get students for turma")
            return
        
        students = response.json()
        if not students:
            results.failure("Bulk Attendance", "No students found for turma")
            return
        
        # Create bulk attendance data
        bulk_data = []
        for i, student in enumerate(students[:2]):  # Test with first 2 students
            bulk_data.append({
                "aluno_id": student['id'],
                "turma_id": turma_id,
                "data": SUNDAY_DATE.isoformat(),
                "status": "presente" if i == 0 else "ausente",
                "oferta": 5.0 if i == 0 else 0.0,
                "biblias_entregues": 1 if i == 0 else 0,
                "revistas_entregues": 1 if i == 0 else 0
            })
        
        # Test POST /api/attendance/bulk/{turma_id}
        response = requests.post(f"{BASE_URL}/attendance/bulk/{turma_id}", 
                               params={"data": SUNDAY_DATE.isoformat()},
                               json=bulk_data)
        if response.status_code == 200:
            result = response.json()
            if "message" in result and "registros" in result["message"]:
                results.success("POST /api/attendance/bulk/{turma_id} - Save bulk attendance")
            else:
                results.failure("POST /api/attendance/bulk/{turma_id}", f"Invalid response: {result}")
        else:
            results.failure("POST /api/attendance/bulk/{turma_id}", f"Status {response.status_code}: {response.text}")
        
        # Test Sunday validation for bulk
        response = requests.post(f"{BASE_URL}/attendance/bulk/{turma_id}", 
                               params={"data": NON_SUNDAY_DATE.isoformat()},
                               json=bulk_data)
        if response.status_code == 400:
            results.success("POST /api/attendance/bulk/{turma_id} - Validation: reject non-Sunday")
        else:
            results.failure("POST /api/attendance/bulk/{turma_id} - Validation", f"Should reject non-Sunday, got status {response.status_code}")
            
    except Exception as e:
        results.failure("Bulk Attendance", str(e))

def test_reports_dashboard():
    """Test reports dashboard endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/reports/dashboard", 
                              params={"data": SUNDAY_DATE.isoformat()})
        if response.status_code == 200:
            reports = response.json()
            if isinstance(reports, list):
                # Verify report structure
                if reports:
                    report = reports[0]
                    required_fields = ['turma_nome', 'turma_id', 'data', 'matriculados', 
                                     'presentes', 'ausentes', 'visitantes', 'pos_chamada',
                                     'total_ofertas', 'total_biblias', 'total_revistas']
                    if all(field in report for field in required_fields):
                        # Verify calculation: ausentes = matriculados - presentes
                        if report['ausentes'] == report['matriculados'] - report['presentes']:
                            results.success("GET /api/reports/dashboard - Dashboard report with correct calculations")
                        else:
                            results.failure("GET /api/reports/dashboard", f"Incorrect calculation: ausentes={report['ausentes']}, matriculados={report['matriculados']}, presentes={report['presentes']}")
                    else:
                        missing = [f for f in required_fields if f not in report]
                        results.failure("GET /api/reports/dashboard", f"Missing fields: {missing}")
                else:
                    results.success("GET /api/reports/dashboard - Empty report list (valid)")
            else:
                results.failure("GET /api/reports/dashboard", f"Expected list, got: {reports}")
        else:
            results.failure("GET /api/reports/dashboard", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/reports/dashboard", str(e))

def test_floating_point_precision():
    """Test specific floating point precision issue with offers - CRITICAL TEST"""
    print("\n=== TESTING FLOATING POINT PRECISION ISSUE ===")
    
    # Use specific date from the review request
    test_date = "2025-07-13"
    
    # First, get a turma and its students
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code != 200:
            results.failure("Float Precision Test", "Could not get turmas")
            return
        
        turmas = response.json()
        if not turmas:
            results.failure("Float Precision Test", "No turmas available")
            return
        
        turma_id = turmas[0]['id']
        turma_nome = turmas[0]['nome']
        
        # Get students for this turma
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
        if response.status_code != 200:
            results.failure("Float Precision Test", "Could not get students")
            return
        
        students = response.json()
        if len(students) < 2:
            results.failure("Float Precision Test", "Need at least 2 students for test")
            return
        
        # TEST 1: POST /api/attendance/bulk/{turma_id}?data=2025-07-13
        # Simulate scenario: 2 students present, total offer of 17.00
        # Each should receive exactly 8.50 (17.00 / 2)
        print(f"Testing with turma: {turma_nome} ({turma_id})")
        print(f"Using {len(students[:2])} students for precision test")
        
        bulk_data = []
        for i, student in enumerate(students[:2]):
            bulk_data.append({
                "aluno_id": student['id'],
                "status": "presente",
                "oferta": 8.50,  # Each student gets exactly 8.50
                "biblias_entregues": 0,
                "revistas_entregues": 0
            })
        
        # Save bulk attendance with total offer of 17.00 (2 x 8.50)
        response = requests.post(f"{BASE_URL}/attendance/bulk/{turma_id}", 
                               params={"data": test_date},
                               json=bulk_data)
        
        if response.status_code == 200:
            results.success("POST /api/attendance/bulk - Save 17.00 total offer (2 x 8.50)")
        else:
            results.failure("POST /api/attendance/bulk", f"Status {response.status_code}: {response.text}")
            return
        
        # TEST 2: GET /api/attendance?turma_id={turma_id}&data=2025-07-13
        # Verify sum of individual offers returns exactly 17.00
        response = requests.get(f"{BASE_URL}/attendance", 
                              params={"turma_id": turma_id, "data": test_date})
        
        if response.status_code == 200:
            attendance_records = response.json()
            total_ofertas = sum(record.get('oferta', 0) for record in attendance_records)
            
            # Check if total is exactly 17.00 (not 16.919999999999995)
            if total_ofertas == 17.00:
                results.success(f"GET /api/attendance - Sum of offers is exactly 17.00 (got {total_ofertas})")
            else:
                results.failure("GET /api/attendance - Precision Issue", 
                              f"Expected 17.00, got {total_ofertas} (precision error detected)")
            
            # Also check individual values
            individual_offers = [record.get('oferta', 0) for record in attendance_records]
            print(f"Individual offers: {individual_offers}")
            
            if all(offer == 8.50 for offer in individual_offers):
                results.success("GET /api/attendance - Individual offers are exactly 8.50 each")
            else:
                results.failure("GET /api/attendance - Individual Precision", 
                              f"Expected all 8.50, got {individual_offers}")
        else:
            results.failure("GET /api/attendance", f"Status {response.status_code}: {response.text}")
            return
        
        # TEST 3: GET /api/reports/dashboard?data=2025-07-13
        # Verify total_ofertas shows 17.00 and not imprecise value
        response = requests.get(f"{BASE_URL}/reports/dashboard", 
                              params={"data": test_date})
        
        if response.status_code == 200:
            reports = response.json()
            
            # Find the report for our test turma
            test_report = None
            for report in reports:
                if report['turma_id'] == turma_id:
                    test_report = report
                    break
            
            if test_report:
                total_ofertas = test_report['total_ofertas']
                
                if total_ofertas == 17.00:
                    results.success(f"GET /api/reports/dashboard - total_ofertas is exactly 17.00 (got {total_ofertas})")
                else:
                    results.failure("GET /api/reports/dashboard - Precision Issue", 
                                  f"Expected 17.00, got {total_ofertas} (precision error in dashboard)")
                
                # Additional checks
                print(f"Dashboard report for {turma_nome}:")
                print(f"  - Matriculados: {test_report['matriculados']}")
                print(f"  - Presentes: {test_report['presentes']}")
                print(f"  - Total Ofertas: {test_report['total_ofertas']}")
                
            else:
                results.failure("GET /api/reports/dashboard", f"No report found for turma {turma_nome}")
        else:
            results.failure("GET /api/reports/dashboard", f"Status {response.status_code}: {response.text}")
        
        # TEST 4: Test with different precision scenarios
        print("\n--- Testing additional precision scenarios ---")
        
        # Test with 17.01 (should remain 17.01)
        bulk_data_2 = []
        for i, student in enumerate(students[:2]):
            bulk_data_2.append({
                "aluno_id": student['id'],
                "status": "presente", 
                "oferta": 8.505,  # This should round to 8.51 each = 17.02 total
                "biblias_entregues": 0,
                "revistas_entregues": 0
            })
        
        # Clear previous data and test new scenario
        test_date_2 = "2025-07-20"  # Another Sunday
        response = requests.post(f"{BASE_URL}/attendance/bulk/{turma_id}", 
                               params={"data": test_date_2},
                               json=bulk_data_2)
        
        if response.status_code == 200:
            # Check the result
            response = requests.get(f"{BASE_URL}/attendance", 
                                  params={"turma_id": turma_id, "data": test_date_2})
            
            if response.status_code == 200:
                attendance_records = response.json()
                total_ofertas = sum(record.get('oferta', 0) for record in attendance_records)
                individual_offers = [record.get('oferta', 0) for record in attendance_records]
                
                print(f"Precision test 2 - Individual offers: {individual_offers}")
                print(f"Precision test 2 - Total: {total_ofertas}")
                
                # Check if values are properly rounded to 2 decimal places
                all_properly_rounded = all(
                    len(str(offer).split('.')[-1]) <= 2 if '.' in str(offer) else True 
                    for offer in individual_offers
                )
                
                if all_properly_rounded:
                    results.success("Precision Test 2 - All values properly rounded to 2 decimal places")
                else:
                    results.failure("Precision Test 2", f"Values not properly rounded: {individual_offers}")
        
    except Exception as e:
        results.failure("Float Precision Test", f"Exception: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

def test_user_management_endpoints():
    """Test user management endpoints as requested in review"""
    print("\n=== TESTING USER MANAGEMENT ENDPOINTS (REVIEW REQUEST) ===")
    
    # First, create initial admin if not exists
    try:
        response = requests.post(f"{BASE_URL}/init-admin")
        if response.status_code == 200:
            results.success("POST /api/init-admin - Create initial admin user")
        elif response.status_code == 400:
            results.success("POST /api/init-admin - Admin already exists (expected)")
        else:
            results.failure("POST /api/init-admin", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/init-admin", str(e))
    
    # Get turmas for user permissions
    turmas_dict = {}
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code == 200:
            turmas = response.json()
            for turma in turmas:
                turmas_dict[turma['nome']] = turma['id']
            print(f"Available turmas for user permissions: {list(turmas_dict.keys())}")
        else:
            results.failure("GET /api/turmas for user test", f"Status {response.status_code}: {response.text}")
            return
    except Exception as e:
        results.failure("GET /api/turmas for user test", str(e))
        return
    
    # Create user Kell with specific requirements
    kell_user_id = None
    try:
        # Select some turmas for Kell's permissions
        selected_turmas = list(turmas_dict.values())[:3] if turmas_dict else []
        
        kell_data = {
            "nome": "Kell Silva",
            "email": "kell@ebd.com",
            "senha": "kell123",
            "tipo": "professor",
            "turmas_permitidas": selected_turmas
        }
        
        response = requests.post(f"{BASE_URL}/users", json=kell_data)
        if response.status_code == 200:
            user = response.json()
            kell_user_id = user['id']
            results.success("POST /api/users - Create user Kell with email kell@ebd.com")
            
            # Verify user data
            if user['email'] == "kell@ebd.com" and user['nome'] == "Kell Silva":
                results.success("POST /api/users - Kell user has correct email and name")
            else:
                results.failure("POST /api/users - Kell data", f"Expected kell@ebd.com, got {user.get('email')}")
            
            # Verify turmas_permitidas
            if user['turmas_permitidas'] == selected_turmas:
                results.success("POST /api/users - Kell user has correct turmas_permitidas")
            else:
                results.failure("POST /api/users - Kell turmas", f"Expected {selected_turmas}, got {user.get('turmas_permitidas')}")
        else:
            results.failure("POST /api/users - Create Kell", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/users - Create Kell", str(e))
    
    # TEST 1: GET /api/users - verify it returns correct user data including turmas_permitidas
    try:
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            users = response.json()
            if isinstance(users, list):
                results.success("GET /api/users - Returns list of users")
                
                # Find Kell user
                kell_user = None
                for user in users:
                    if user.get('email') == 'kell@ebd.com':
                        kell_user = user
                        break
                
                if kell_user:
                    results.success("GET /api/users - Found user Kell with email kell@ebd.com")
                    
                    # Verify required fields
                    required_fields = ['id', 'nome', 'email', 'tipo', 'turmas_permitidas', 'ativo']
                    missing_fields = [field for field in required_fields if field not in kell_user]
                    
                    if not missing_fields:
                        results.success("GET /api/users - Kell user has all required fields")
                    else:
                        results.failure("GET /api/users - Kell fields", f"Missing fields: {missing_fields}")
                    
                    # Verify turmas_permitidas is populated
                    if 'turmas_permitidas' in kell_user and isinstance(kell_user['turmas_permitidas'], list):
                        if len(kell_user['turmas_permitidas']) > 0:
                            results.success("GET /api/users - Kell has populated turmas_permitidas")
                        else:
                            results.success("GET /api/users - Kell has empty turmas_permitidas (valid for admin)")
                    else:
                        results.failure("GET /api/users - Kell turmas_permitidas", "turmas_permitidas field missing or invalid")
                else:
                    results.failure("GET /api/users - Find Kell", "User Kell with email kell@ebd.com not found")
                
                # Verify admin user also exists
                admin_user = None
                for user in users:
                    if user.get('email') == 'admin@ebd.com':
                        admin_user = user
                        break
                
                if admin_user:
                    results.success("GET /api/users - Found admin user with email admin@ebd.com")
                else:
                    results.failure("GET /api/users - Find admin", "Admin user not found")
                    
            else:
                results.failure("GET /api/users", f"Expected list, got: {type(users)}")
        else:
            results.failure("GET /api/users", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/users", str(e))
    
    # TEST 2: PUT /api/users/{user_id} - should work for updating users
    if kell_user_id:
        try:
            # Update Kell's information
            update_data = {
                "nome": "Kell Silva Updated",
                "email": "kell@ebd.com",  # Keep same email
                "senha": "newpassword123",
                "tipo": "professor",
                "turmas_permitidas": list(turmas_dict.values())[:2] if turmas_dict else []  # Different turmas
            }
            
            response = requests.put(f"{BASE_URL}/users/{kell_user_id}", json=update_data)
            if response.status_code == 200:
                updated_user = response.json()
                results.success("PUT /api/users/{user_id} - Successfully updated user Kell")
                
                # Verify updates
                if updated_user['nome'] == "Kell Silva Updated":
                    results.success("PUT /api/users/{user_id} - Name updated correctly")
                else:
                    results.failure("PUT /api/users/{user_id} - Name update", f"Expected 'Kell Silva Updated', got '{updated_user.get('nome')}'")
                
                if updated_user['email'] == "kell@ebd.com":
                    results.success("PUT /api/users/{user_id} - Email maintained correctly")
                else:
                    results.failure("PUT /api/users/{user_id} - Email", f"Expected 'kell@ebd.com', got '{updated_user.get('email')}'")
                
                if updated_user['tipo'] == "professor":
                    results.success("PUT /api/users/{user_id} - Type updated correctly")
                else:
                    results.failure("PUT /api/users/{user_id} - Type", f"Expected 'professor', got '{updated_user.get('tipo')}'")
                
                if updated_user['turmas_permitidas'] == update_data['turmas_permitidas']:
                    results.success("PUT /api/users/{user_id} - turmas_permitidas updated correctly")
                else:
                    results.failure("PUT /api/users/{user_id} - turmas_permitidas", f"Expected {update_data['turmas_permitidas']}, got {updated_user.get('turmas_permitidas')}")
                    
            else:
                results.failure("PUT /api/users/{user_id}", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("PUT /api/users/{user_id}", str(e))
        
        # Test updating with invalid data
        try:
            invalid_update = {
                "nome": "Kell Invalid",
                "email": "admin@ebd.com",  # Try to use existing admin email
                "senha": "password",
                "tipo": "professor",
                "turmas_permitidas": []
            }
            
            response = requests.put(f"{BASE_URL}/users/{kell_user_id}", json=invalid_update)
            if response.status_code == 400:
                results.success("PUT /api/users/{user_id} - Validation: reject duplicate email")
            else:
                results.failure("PUT /api/users/{user_id} - Validation", f"Should reject duplicate email, got status {response.status_code}")
        except Exception as e:
            results.failure("PUT /api/users/{user_id} - Validation", str(e))
    
    # TEST 3: Verify user Kell final state
    if kell_user_id:
        try:
            response = requests.get(f"{BASE_URL}/users")
            if response.status_code == 200:
                users = response.json()
                kell_user = None
                for user in users:
                    if user.get('id') == kell_user_id:
                        kell_user = user
                        break
                
                if kell_user:
                    print(f"\n--- Final Kell User Verification ---")
                    print(f"ID: {kell_user.get('id')}")
                    print(f"Nome: {kell_user.get('nome')}")
                    print(f"Email: {kell_user.get('email')}")
                    print(f"Tipo: {kell_user.get('tipo')}")
                    print(f"Turmas Permitidas: {len(kell_user.get('turmas_permitidas', []))} turmas")
                    print(f"Ativo: {kell_user.get('ativo')}")
                    
                    # Final verification
                    if (kell_user.get('email') == 'kell@ebd.com' and 
                        isinstance(kell_user.get('turmas_permitidas'), list) and
                        kell_user.get('ativo') == True):
                        results.success("Final verification - User Kell has correct email kell@ebd.com and populated turmas_permitidas")
                    else:
                        results.failure("Final verification - User Kell", "Does not meet all requirements")
                else:
                    results.failure("Final verification", "Could not find updated Kell user")
        except Exception as e:
            results.failure("Final verification", str(e))

def test_revistas_endpoints():
    """Test revista endpoints as requested in review"""
    print("\n=== TESTING REVISTA ENDPOINTS (REVIEW REQUEST) ===")
    
    # First, initialize church data to have proper turmas
    try:
        response = requests.post(f"{BASE_URL}/init-church-data")
        if response.status_code == 200:
            results.success("POST /api/init-church-data - Initialize church data for revista tests")
        else:
            results.failure("POST /api/init-church-data", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/init-church-data", str(e))
    
    # Get turmas to find specific ones mentioned in review
    turmas_dict = {}
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code == 200:
            turmas = response.json()
            for turma in turmas:
                turmas_dict[turma['nome']] = turma['id']
            print(f"Available turmas: {list(turmas_dict.keys())}")
        else:
            results.failure("GET /api/turmas for revista test", f"Status {response.status_code}: {response.text}")
            return
    except Exception as e:
        results.failure("GET /api/turmas for revista test", str(e))
        return
    
    # Create the 5 new revistas mentioned in the review request
    revistas_data = [
        {
            "tema": "A Liberdade em Cristo — Vivendo o verdadeiro Evangelho conforme a Carta de Paulo aos Gálatas",
            "turma_nome": "Jovens",
            "licoes_count": 13
        },
        {
            "tema": "Grandes Cartas para Nós", 
            "turma_nome": "Adolescentes",
            "licoes_count": 13
        },
        {
            "tema": "Recebendo o Batismo no Espírito Santo",
            "turma_nome": "Pré-Adolescentes", 
            "licoes_count": 13
        },
        {
            "tema": "Verdades que Jesus ensinou",
            "turma_nome": "Juniores",
            "licoes_count": 13
        },
        {
            "tema": "As aventuras de um Grande Missionário",
            "turma_nome": "Primarios",
            "licoes_count": 13
        }
    ]
    
    # Create revistas for each turma
    created_revistas = []
    for revista_info in revistas_data:
        turma_nome = revista_info["turma_nome"]
        if turma_nome not in turmas_dict:
            results.failure(f"Create revista for {turma_nome}", f"Turma {turma_nome} not found")
            continue
        
        # Generate 13 lições with proper dates (Sundays starting from 2025-07-06)
        licoes = []
        start_date = datetime(2025, 7, 6)  # First Sunday
        for i in range(13):
            licao_date = start_date + timedelta(weeks=i)
            licoes.append({
                "titulo": f"Lição {i+1} - {revista_info['tema'][:30]}...",
                "data": licao_date.strftime("%Y-%m-%d")
            })
        
        revista_data = {
            "tema": revista_info["tema"],
            "licoes": licoes,
            "turma_ids": [turmas_dict[turma_nome]]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/revistas", json=revista_data)
            if response.status_code == 200:
                result = response.json()
                created_revistas.append(result["revista"])
                results.success(f"POST /api/revistas - Create revista for {turma_nome}")
            else:
                results.failure(f"POST /api/revistas for {turma_nome}", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure(f"POST /api/revistas for {turma_nome}", str(e))
    
    # Also create the existing adult revista to have 6 total
    try:
        response = requests.post(f"{BASE_URL}/init-revista-adultos")
        if response.status_code == 200:
            results.success("POST /api/init-revista-adultos - Create adult revista")
        else:
            results.failure("POST /api/init-revista-adultos", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/init-revista-adultos", str(e))
    
    # TEST 1: GET /api/revistas - should return all 6 revistas
    try:
        response = requests.get(f"{BASE_URL}/revistas")
        if response.status_code == 200:
            revistas = response.json()
            if isinstance(revistas, list):
                if len(revistas) == 6:
                    results.success(f"GET /api/revistas - Returns all 6 revistas (found {len(revistas)})")
                    
                    # Verify each revista has required fields
                    for revista in revistas:
                        required_fields = ['id', 'tema', 'licoes', 'turma_ids', 'ativa']
                        if all(field in revista for field in required_fields):
                            results.success(f"GET /api/revistas - Revista '{revista['tema'][:50]}...' has all required fields")
                        else:
                            missing = [f for f in required_fields if f not in revista]
                            results.failure(f"GET /api/revistas - Revista structure", f"Missing fields: {missing}")
                else:
                    results.failure("GET /api/revistas", f"Expected 6 revistas, got {len(revistas)}")
            else:
                results.failure("GET /api/revistas", f"Expected list, got: {type(revistas)}")
        else:
            results.failure("GET /api/revistas", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/revistas", str(e))
    
    # TEST 2: GET /api/revistas/turma/{turma_id} for Jovens specifically
    if "Jovens" in turmas_dict:
        jovens_turma_id = turmas_dict["Jovens"]
        try:
            response = requests.get(f"{BASE_URL}/revistas/turma/{jovens_turma_id}")
            if response.status_code == 200:
                revista = response.json()
                if revista and "tema" in revista:
                    expected_tema = "A Liberdade em Cristo — Vivendo o verdadeiro Evangelho conforme a Carta de Paulo aos Gálatas"
                    if revista["tema"] == expected_tema:
                        results.success("GET /api/revistas/turma/{turma_id} - Jovens revista has correct tema")
                        
                        # Verify 13 lições
                        if "licoes" in revista and len(revista["licoes"]) == 13:
                            results.success("GET /api/revistas/turma/{turma_id} - Jovens revista has exactly 13 lições")
                            
                            # Verify lições have titles and dates
                            licoes_valid = True
                            for licao in revista["licoes"]:
                                if not ("titulo" in licao and "data" in licao):
                                    licoes_valid = False
                                    break
                            
                            if licoes_valid:
                                results.success("GET /api/revistas/turma/{turma_id} - All lições have título and data")
                            else:
                                results.failure("GET /api/revistas/turma/{turma_id} - Lições structure", "Some lições missing título or data")
                        else:
                            results.failure("GET /api/revistas/turma/{turma_id} - Jovens lições", f"Expected 13 lições, got {len(revista.get('licoes', []))}")
                    else:
                        results.failure("GET /api/revistas/turma/{turma_id} - Jovens tema", f"Expected '{expected_tema}', got '{revista.get('tema', 'N/A')}'")
                else:
                    results.failure("GET /api/revistas/turma/{turma_id} - Jovens", "No revista found or invalid structure")
            else:
                results.failure("GET /api/revistas/turma/{turma_id} - Jovens", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("GET /api/revistas/turma/{turma_id} - Jovens", str(e))
    
    # TEST 3: Verify all 5 new revistas have correct data
    expected_revistas = {
        "Jovens": "A Liberdade em Cristo — Vivendo o verdadeiro Evangelho conforme a Carta de Paulo aos Gálatas",
        "Adolescentes": "Grandes Cartas para Nós",
        "Pré-Adolescentes": "Recebendo o Batismo no Espírito Santo", 
        "Juniores": "Verdades que Jesus ensinou",
        "Primarios": "As aventuras de um Grande Missionário"
    }
    
    for turma_nome, expected_tema in expected_revistas.items():
        if turma_nome in turmas_dict:
            turma_id = turmas_dict[turma_nome]
            try:
                response = requests.get(f"{BASE_URL}/revistas/turma/{turma_id}")
                if response.status_code == 200:
                    revista = response.json()
                    if revista and revista.get("tema") == expected_tema:
                        results.success(f"Revista verification - {turma_nome} has correct tema")
                        
                        # Check 13 lições
                        if len(revista.get("licoes", [])) == 13:
                            results.success(f"Revista verification - {turma_nome} has exactly 13 lições")
                        else:
                            results.failure(f"Revista verification - {turma_nome} lições", f"Expected 13, got {len(revista.get('licoes', []))}")
                        
                        # Check turma_ids linkage
                        if turma_id in revista.get("turma_ids", []):
                            results.success(f"Revista verification - {turma_nome} turma_id correctly linked")
                        else:
                            results.failure(f"Revista verification - {turma_nome} linkage", f"turma_id {turma_id} not in turma_ids {revista.get('turma_ids', [])}")
                    else:
                        results.failure(f"Revista verification - {turma_nome}", f"Expected tema '{expected_tema}', got '{revista.get('tema', 'N/A')}'")
                else:
                    results.failure(f"Revista verification - {turma_nome}", f"Status {response.status_code}: {response.text}")
            except Exception as e:
                results.failure(f"Revista verification - {turma_nome}", str(e))
    
    # TEST 4: Verify dates are correct (Sundays starting from 2025-07-06)
    if "Jovens" in turmas_dict:
        try:
            response = requests.get(f"{BASE_URL}/revistas/turma/{turmas_dict['Jovens']}")
            if response.status_code == 200:
                revista = response.json()
                if revista and "licoes" in revista:
                    licoes = revista["licoes"]
                    if licoes:
                        # Check first date
                        first_date = licoes[0]["data"]
                        if first_date == "2025-07-06":
                            results.success("Revista dates - First lição starts on 2025-07-06")
                        else:
                            results.failure("Revista dates", f"Expected first date 2025-07-06, got {first_date}")
                        
                        # Check if all dates are Sundays
                        all_sundays = True
                        for licao in licoes:
                            date_obj = datetime.strptime(licao["data"], "%Y-%m-%d")
                            if date_obj.weekday() != 6:  # Sunday is 6
                                all_sundays = False
                                break
                        
                        if all_sundays:
                            results.success("Revista dates - All lição dates are Sundays")
                        else:
                            results.failure("Revista dates", "Some lição dates are not Sundays")
        except Exception as e:
            results.failure("Revista dates verification", str(e))

def main():
    """Run all tests in sequence"""
    print("=== EBD MANAGER BACKEND TEST SUITE ===\n")
    
    # Test 1: Initialize sample data (MUST BE FIRST)
    print("1. Testing sample data initialization...")
    if not test_init_sample_data():
        print("❌ CRITICAL: Sample data initialization failed. Cannot continue with other tests.")
        results.summary()
        return
    
    # Test 2: CRUD Turmas
    print("\n2. Testing CRUD operations for Turmas...")
    turma_id = test_turmas_crud()
    
    # Test 3: CRUD Students
    print("\n3. Testing CRUD operations for Students...")
    student_id = test_students_crud(turma_id)
    
    # Test 4: Attendance System
    print("\n4. Testing Attendance System...")
    test_attendance_system(turma_id, student_id)
    
    # Test 5: Bulk Attendance
    print("\n5. Testing Bulk Attendance...")
    test_bulk_attendance(turma_id)
    
    # Test 6: Reports Dashboard
    print("\n6. Testing Reports Dashboard...")
    test_reports_dashboard()
    
    # Test 7: CRITICAL - Floating Point Precision Issue
    print("\n7. Testing Floating Point Precision (CRITICAL)...")
    test_floating_point_precision()
    
    # Test 8: USER MANAGEMENT ENDPOINTS (REVIEW REQUEST)
    print("\n8. Testing User Management Endpoints (Review Request)...")
    test_user_management_endpoints()
    
    # Test 9: REVISTA ENDPOINTS (REVIEW REQUEST)
    print("\n9. Testing Revista Endpoints (Review Request)...")
    test_revistas_endpoints()
    
    # Final summary
    results.summary()
    
    # Return exit code based on results
    if results.failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()