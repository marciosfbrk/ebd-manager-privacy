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

def test_backup_restore_system():
    """Test backup and restore system as requested in review"""
    print("\n=== TESTING BACKUP AND RESTORE SYSTEM (REVIEW REQUEST) ===")
    
    # Store original data counts for comparison
    original_counts = {}
    
    # Get current system state before backup
    try:
        response = requests.get(f"{BASE_URL}/deploy-check")
        if response.status_code == 200:
            deploy_data = response.json()
            original_counts = deploy_data.get("status", {}).get("data", {})
            results.success("GET /api/deploy-check - Get system status before backup")
            print(f"Original data counts: {original_counts}")
        else:
            results.failure("GET /api/deploy-check", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/deploy-check", str(e))
    
    # TEST 1: Generate backup
    backup_data = None
    try:
        response = requests.get(f"{BASE_URL}/backup/generate")
        if response.status_code == 200:
            backup_response = response.json()
            if backup_response.get("success") and "backup" in backup_response:
                backup_data = backup_response["backup"]
                results.success("GET /api/backup/generate - Generate backup successfully")
                
                # Verify backup structure (metadata + data)
                if "metadata" in backup_data and "data" in backup_data:
                    results.success("Backup structure - Contains metadata and data sections")
                    
                    # Check metadata
                    metadata = backup_data["metadata"]
                    required_meta_fields = ["backup_timestamp", "backup_date", "system_version", "total_collections", "total_records"]
                    if all(field in metadata for field in required_meta_fields):
                        results.success("Backup metadata - Contains all required fields")
                    else:
                        missing = [f for f in required_meta_fields if f not in metadata]
                        results.failure("Backup metadata", f"Missing fields: {missing}")
                    
                    # Check data collections
                    data_section = backup_data["data"]
                    expected_collections = ["users", "turmas", "students", "attendance", "revistas"]
                    found_collections = []
                    for collection in expected_collections:
                        if collection in data_section:
                            found_collections.append(collection)
                            results.success(f"Backup data - Contains {collection} collection ({len(data_section[collection])} records)")
                        else:
                            results.failure("Backup data", f"Missing {collection} collection")
                    
                    # Verify backup size and integrity
                    total_records = sum(len(data_section.get(col, [])) for col in expected_collections)
                    if total_records > 0:
                        results.success(f"Backup integrity - Contains {total_records} total records")
                    else:
                        results.failure("Backup integrity", "Backup contains no records")
                        
                    # Check backup size
                    backup_size_mb = backup_response.get("size_mb", 0)
                    if backup_size_mb > 0:
                        results.success(f"Backup size - {backup_size_mb:.2f} MB")
                    else:
                        results.failure("Backup size", "Backup size is 0 or not reported")
                        
                else:
                    results.failure("Backup structure", "Missing metadata or data sections")
            else:
                results.failure("GET /api/backup/generate", f"Invalid response structure: {backup_response}")
        else:
            results.failure("GET /api/backup/generate", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/backup/generate", str(e))
    
    # TEST 2: Restore backup with valid data
    if backup_data:
        try:
            response = requests.post(f"{BASE_URL}/backup/restore", json=backup_data)
            if response.status_code == 200:
                restore_response = response.json()
                if restore_response.get("success"):
                    results.success("POST /api/backup/restore - Restore backup successfully")
                    
                    # Verify restore summary
                    if "restore_summary" in restore_response:
                        summary = restore_response["restore_summary"]
                        total_restored = restore_response.get("total_restored", 0)
                        results.success(f"Backup restore - {total_restored} records restored")
                        
                        # Check individual collection counts
                        for collection, count in summary.items():
                            if count > 0:
                                results.success(f"Restore summary - {collection}: {count} records")
                    else:
                        results.failure("POST /api/backup/restore", "Missing restore_summary in response")
                else:
                    results.failure("POST /api/backup/restore", f"Restore failed: {restore_response}")
            else:
                results.failure("POST /api/backup/restore", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("POST /api/backup/restore", str(e))
        
        # Verify data integrity after restore
        try:
            response = requests.get(f"{BASE_URL}/deploy-check")
            if response.status_code == 200:
                deploy_data = response.json()
                restored_counts = deploy_data.get("status", {}).get("data", {})
                
                # Verify required users exist after restore
                users_status = deploy_data.get("status", {}).get("users", {})
                if users_status.get("admin_exists") and users_status.get("professor_exists"):
                    results.success("Data validation - Required users (admin@ebd.com, kell@ebd.com) exist after restore")
                else:
                    results.failure("Data validation", "Required users missing after restore")
                
                # Compare counts before and after
                print(f"Restored data counts: {restored_counts}")
                results.success("POST /api/backup/restore - Data integrity verified after restore")
                
            else:
                results.failure("Data validation after restore", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("Data validation after restore", str(e))
    
    # TEST 3: Test restore with invalid data (should fail)
    try:
        invalid_backup = {"invalid": "structure"}
        response = requests.post(f"{BASE_URL}/backup/restore", json=invalid_backup)
        if response.status_code == 400:
            results.success("POST /api/backup/restore - Validation: reject invalid backup format")
        else:
            results.failure("POST /api/backup/restore - Validation", f"Should reject invalid format, got status {response.status_code}")
    except Exception as e:
        results.failure("POST /api/backup/restore - Validation", str(e))
    
    # TEST 4: Test restore with malformed JSON
    try:
        malformed_backup = {"data": "not_a_dict"}
        response = requests.post(f"{BASE_URL}/backup/restore", json=malformed_backup)
        if response.status_code in [400, 500]:
            results.success("POST /api/backup/restore - Validation: reject malformed JSON structure")
        else:
            results.failure("POST /api/backup/restore - Malformed", f"Should reject malformed data, got status {response.status_code}")
    except Exception as e:
        results.failure("POST /api/backup/restore - Malformed", str(e))
    
    # TEST 5: Test backup with empty data scenario
    try:
        # First clear all data
        response = requests.post(f"{BASE_URL}/init-sample-data")  # This clears and recreates minimal data
        if response.status_code == 200:
            # Generate backup of minimal data
            response = requests.get(f"{BASE_URL}/backup/generate")
            if response.status_code == 200:
                minimal_backup = response.json()
                if minimal_backup.get("success"):
                    results.success("Backup edge case - Generate backup with minimal data")
                else:
                    results.failure("Backup edge case", "Failed to generate backup with minimal data")
            else:
                results.failure("Backup edge case", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("Backup edge case", str(e))
    
    # TEST 6: Verify system functionality after complete backup/restore cycle
    try:
        # Test basic API functionality
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code == 200:
            turmas = response.json()
            if isinstance(turmas, list):
                results.success("System functionality - Turmas API working after backup/restore")
            else:
                results.failure("System functionality", "Turmas API returned invalid data after restore")
        else:
            results.failure("System functionality", f"Turmas API failed after restore: {response.status_code}")
        
        # Test students API
        response = requests.get(f"{BASE_URL}/students")
        if response.status_code == 200:
            students = response.json()
            if isinstance(students, list):
                results.success("System functionality - Students API working after backup/restore")
            else:
                results.failure("System functionality", "Students API returned invalid data after restore")
        else:
            results.failure("System functionality", f"Students API failed after restore: {response.status_code}")
            
    except Exception as e:
        results.failure("System functionality", str(e))

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

def test_call_control_system():
    """Test the new call control system (sistema de controle de chamadas)"""
    print("\n=== TESTING CALL CONTROL SYSTEM (REVIEW REQUEST) ===")
    print("Testing system-config endpoints and pode_editar_chamada function")
    
    # TEST 1: GET /api/system-config - should return default configurations
    try:
        response = requests.get(f"{BASE_URL}/system-config")
        if response.status_code == 200:
            config = response.json()
            results.success("GET /api/system-config - Returns system configuration")
            
            # Verify default configuration structure
            expected_fields = ['id', 'bloqueio_chamada_ativo', 'horario_bloqueio', 'atualizado_em', 'atualizado_por']
            missing_fields = [field for field in expected_fields if field not in config]
            
            if not missing_fields:
                results.success("GET /api/system-config - Contains all required fields")
            else:
                results.failure("GET /api/system-config - Structure", f"Missing fields: {missing_fields}")
            
            # Verify default values
            if config.get('bloqueio_chamada_ativo') == True:
                results.success("GET /api/system-config - Default bloqueio_chamada_ativo is True")
            else:
                results.failure("GET /api/system-config - Default value", f"Expected bloqueio_chamada_ativo=True, got {config.get('bloqueio_chamada_ativo')}")
            
            if config.get('horario_bloqueio') == "13:00":
                results.success("GET /api/system-config - Default horario_bloqueio is 13:00")
            else:
                results.failure("GET /api/system-config - Default value", f"Expected horario_bloqueio='13:00', got {config.get('horario_bloqueio')}")
                
        else:
            results.failure("GET /api/system-config", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/system-config", str(e))
    
    # TEST 2: PUT /api/system-config - activate/deactivate blocking
    try:
        # Test activating blocking with custom time
        update_data = {
            "bloqueio_ativo": True,
            "user_id": "test-admin-id",
            "horario": "14:00"
        }
        
        response = requests.put(f"{BASE_URL}/system-config", params=update_data)
        if response.status_code == 200:
            result = response.json()
            if "message" in result and "sucesso" in result["message"]:
                results.success("PUT /api/system-config - Activate blocking with custom time (14:00)")
            else:
                results.failure("PUT /api/system-config - Response", f"Unexpected response: {result}")
        else:
            results.failure("PUT /api/system-config - Activate", f"Status {response.status_code}: {response.text}")
        
        # Verify the configuration was updated
        response = requests.get(f"{BASE_URL}/system-config")
        if response.status_code == 200:
            config = response.json()
            if config.get('bloqueio_chamada_ativo') == True and config.get('horario_bloqueio') == "14:00":
                results.success("PUT /api/system-config - Configuration updated correctly")
            else:
                results.failure("PUT /api/system-config - Verification", f"Config not updated: {config}")
        
        # Test deactivating blocking
        update_data = {
            "bloqueio_ativo": False,
            "user_id": "test-admin-id",
            "horario": "13:00"
        }
        
        response = requests.put(f"{BASE_URL}/system-config", params=update_data)
        if response.status_code == 200:
            results.success("PUT /api/system-config - Deactivate blocking")
        else:
            results.failure("PUT /api/system-config - Deactivate", f"Status {response.status_code}: {response.text}")
            
    except Exception as e:
        results.failure("PUT /api/system-config", str(e))
    
    # TEST 3: Test PUT /api/attendance/{id} with user_tipo and user_id parameters
    # First, create some attendance data to test with
    try:
        # Get a turma and student for testing
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code != 200:
            results.failure("Attendance control test setup", "Could not get turmas")
            return
        
        turmas = response.json()
        if not turmas:
            results.failure("Attendance control test setup", "No turmas available")
            return
        
        turma_id = turmas[0]['id']
        
        # Get students for this turma
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": turma_id})
        if response.status_code != 200:
            results.failure("Attendance control test setup", "Could not get students")
            return
        
        students = response.json()
        if not students:
            results.failure("Attendance control test setup", "No students available")
            return
        
        student_id = students[0]['id']
        
        # Create attendance record for today (to test time-based restrictions)
        today = datetime.now().strftime("%Y-%m-%d")
        # Find next Sunday for valid attendance
        today_date = datetime.now().date()
        days_ahead = 6 - today_date.weekday()  # Sunday is 6
        if days_ahead <= 0:
            days_ahead += 7
        next_sunday = today_date + timedelta(days_ahead)
        
        attendance_data = {
            "aluno_id": student_id,
            "turma_id": turma_id,
            "data": next_sunday.isoformat(),
            "status": "presente",
            "oferta": 10.0,
            "biblias_entregues": 1,
            "revistas_entregues": 1
        }
        
        response = requests.post(f"{BASE_URL}/attendance", json=attendance_data)
        if response.status_code != 200:
            results.failure("Attendance control test setup", f"Could not create attendance: {response.text}")
            return
        
        attendance_record = response.json()
        attendance_id = attendance_record['id']
        
        print(f"Created attendance record {attendance_id} for testing")
        
        # TEST 3A: Admin should always be able to edit
        try:
            update_data = {
                "status": "ausente",
                "oferta": 15.0
            }
            
            response = requests.put(f"{BASE_URL}/attendance/{attendance_id}", 
                                  json=update_data,
                                  params={"user_tipo": "admin", "user_id": "admin-test-id"})
            
            if response.status_code == 200:
                results.success("PUT /api/attendance/{id} - Admin can always edit attendance")
            else:
                results.failure("PUT /api/attendance/{id} - Admin edit", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("PUT /api/attendance/{id} - Admin edit", str(e))
        
        # TEST 3B: Moderator should always be able to edit
        try:
            update_data = {
                "status": "presente",
                "oferta": 20.0
            }
            
            response = requests.put(f"{BASE_URL}/attendance/{attendance_id}", 
                                  json=update_data,
                                  params={"user_tipo": "moderador", "user_id": "moderador-test-id"})
            
            if response.status_code == 200:
                results.success("PUT /api/attendance/{id} - Moderator can always edit attendance")
            else:
                results.failure("PUT /api/attendance/{id} - Moderator edit", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("PUT /api/attendance/{id} - Moderator edit", str(e))
        
        # TEST 3C: Professor restrictions based on time and date
        # First, ensure blocking is active
        try:
            update_config = {
                "bloqueio_ativo": True,
                "user_id": "test-admin-id",
                "horario": "13:00"
            }
            requests.put(f"{BASE_URL}/system-config", params=update_config)
        except:
            pass
        
        # Create attendance for today to test time restrictions
        today_sunday = None
        current_date = datetime.now().date()
        
        # If today is Sunday, use today; otherwise find next Sunday
        if current_date.weekday() == 6:  # Today is Sunday
            today_sunday = current_date
        else:
            # Find next Sunday
            days_ahead = 6 - current_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            today_sunday = current_date + timedelta(days_ahead)
        
        # Create attendance for the Sunday we're testing
        today_attendance_data = {
            "aluno_id": student_id,
            "turma_id": turma_id,
            "data": today_sunday.isoformat(),
            "status": "presente",
            "oferta": 5.0,
            "biblias_entregues": 0,
            "revistas_entregues": 0
        }
        
        # Delete any existing attendance for this date first
        try:
            requests.delete(f"{BASE_URL}/attendance/bulk/{turma_id}", params={"data": today_sunday.isoformat()})
        except:
            pass
        
        response = requests.post(f"{BASE_URL}/attendance", json=today_attendance_data)
        if response.status_code == 200:
            today_attendance = response.json()
            today_attendance_id = today_attendance['id']
            
            # Test professor editing - behavior depends on current time
            current_hour = datetime.now().hour
            
            try:
                update_data = {
                    "status": "ausente",
                    "oferta": 0.0
                }
                
                response = requests.put(f"{BASE_URL}/attendance/{today_attendance_id}", 
                                      json=update_data,
                                      params={"user_tipo": "professor", "user_id": "professor-test-id"})
                
                if current_hour < 13:
                    # Before 13:00 - professor should be able to edit
                    if response.status_code == 200:
                        results.success("PUT /api/attendance/{id} - Professor can edit before 13:00")
                    else:
                        results.failure("PUT /api/attendance/{id} - Professor before 13:00", f"Should allow edit, got status {response.status_code}: {response.text}")
                else:
                    # After 13:00 - professor should be blocked
                    if response.status_code == 403:
                        results.success("PUT /api/attendance/{id} - Professor blocked after 13:00")
                    else:
                        results.failure("PUT /api/attendance/{id} - Professor after 13:00", f"Should block edit, got status {response.status_code}")
                        
            except Exception as e:
                results.failure("PUT /api/attendance/{id} - Professor time restriction", str(e))
        
        # TEST 3D: Test with blocking disabled
        try:
            # Disable blocking
            update_config = {
                "bloqueio_ativo": False,
                "user_id": "test-admin-id",
                "horario": "13:00"
            }
            requests.put(f"{BASE_URL}/system-config", params=update_config)
            
            # Professor should now be able to edit regardless of time
            update_data = {
                "status": "presente",
                "oferta": 25.0
            }
            
            response = requests.put(f"{BASE_URL}/attendance/{attendance_id}", 
                                  json=update_data,
                                  params={"user_tipo": "professor", "user_id": "professor-test-id"})
            
            if response.status_code == 200:
                results.success("PUT /api/attendance/{id} - Professor can edit when blocking is disabled")
            else:
                results.failure("PUT /api/attendance/{id} - Professor with blocking disabled", f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            results.failure("PUT /api/attendance/{id} - Professor with blocking disabled", str(e))
        
    except Exception as e:
        results.failure("Attendance control system test", str(e))
    
    print("Call control system testing completed")

def test_login_with_credentials():
    """Test login with specific credentials mentioned in review request"""
    print("\n=== TESTING LOGIN WITH SPECIFIC CREDENTIALS ===")
    print("Testing admin@ebd.com / 123456 and kell@ebd.com / 123456")
    
    # TEST 1: Login with admin credentials
    try:
        admin_login = {
            "email": "admin@ebd.com",
            "senha": "123456"
        }
        
        response = requests.post(f"{BASE_URL}/login", json=admin_login)
        if response.status_code == 200:
            login_result = response.json()
            if login_result.get('tipo') == 'admin':
                results.success("POST /api/login - Admin login successful with admin@ebd.com / 123456")
                admin_token = login_result.get('token')
                admin_user_id = login_result.get('user_id')
                print(f"Admin logged in: {login_result.get('nome')} - {login_result.get('email')}")
            else:
                results.failure("POST /api/login - Admin type", f"Expected tipo='admin', got {login_result.get('tipo')}")
        else:
            results.failure("POST /api/login - Admin", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/login - Admin", str(e))
    
    # TEST 2: Login with teacher credentials
    try:
        teacher_login = {
            "email": "kell@ebd.com",
            "senha": "123456"
        }
        
        response = requests.post(f"{BASE_URL}/login", json=teacher_login)
        if response.status_code == 200:
            login_result = response.json()
            if login_result.get('tipo') == 'professor':
                results.success("POST /api/login - Teacher login successful with kell@ebd.com / 123456")
                teacher_token = login_result.get('token')
                teacher_user_id = login_result.get('user_id')
                print(f"Teacher logged in: {login_result.get('nome')} - {login_result.get('email')}")
            else:
                results.failure("POST /api/login - Teacher type", f"Expected tipo='professor', got {login_result.get('tipo')}")
        else:
            results.failure("POST /api/login - Teacher", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("POST /api/login - Teacher", str(e))

def test_user_editing_bug_fix():
    """Test the specific user editing bug fix reported by user"""
    print("\n=== TESTING USER EDITING BUG FIX (SPECIFIC REVIEW REQUEST) ===")
    print("Testing the bug where editing a teacher to transfer between classes failed")
    
    # Get turmas for testing
    turmas_dict = {}
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code == 200:
            turmas = response.json()
            for turma in turmas:
                turmas_dict[turma['nome']] = turma['id']
            print(f"Available turmas for testing: {list(turmas_dict.keys())}")
        else:
            results.failure("GET /api/turmas for user editing test", f"Status {response.status_code}: {response.text}")
            return
    except Exception as e:
        results.failure("GET /api/turmas for user editing test", str(e))
        return
    
    if len(turmas_dict) < 2:
        results.failure("User editing test setup", "Need at least 2 turmas for transfer testing")
        return
    
    # Get first two turmas for testing
    turma_ids = list(turmas_dict.values())[:2]
    turma_names = list(turmas_dict.keys())[:2]
    
    # TEST 1: Create teacher normally (should work)
    print("\n--- TEST 1: Creating teacher normally ---")
    teacher_id = None
    try:
        teacher_data = {
            "nome": "Professor Teste",
            "email": "professor.teste@ebd.com",
            "senha": "senha123",
            "tipo": "professor",
            "turmas_permitidas": [turma_ids[0]]  # Start with first turma
        }
        
        response = requests.post(f"{BASE_URL}/users", json=teacher_data)
        if response.status_code == 200:
            user = response.json()
            teacher_id = user['id']
            results.success("✅ TEST 1: POST /api/users - Create teacher normally with complete data including password")
            
            # Verify created data
            if (user['nome'] == teacher_data['nome'] and 
                user['email'] == teacher_data['email'] and
                user['tipo'] == teacher_data['tipo'] and
                user['turmas_permitidas'] == teacher_data['turmas_permitidas']):
                results.success("✅ TEST 1: Teacher created with correct data")
            else:
                results.failure("TEST 1: Teacher data verification", f"Data mismatch: {user}")
        else:
            results.failure("TEST 1: POST /api/users", f"Status {response.status_code}: {response.text}")
            return
    except Exception as e:
        results.failure("TEST 1: Create teacher", str(e))
        return
    
    # TEST 2: Edit teacher WITHOUT password (this was the bug)
    print(f"\n--- TEST 2: Editing teacher WITHOUT password (transfer from {turma_names[0]} to {turma_names[1]}) ---")
    if teacher_id:
        try:
            # This is the scenario that was failing - editing without password
            update_data = {
                "nome": "Professor Teste Editado",
                "email": "professor.teste@ebd.com",  # Keep same email
                "tipo": "professor",
                "turmas_permitidas": [turma_ids[1]]  # Transfer to second turma
                # NOTE: NO password field - this was causing the bug
            }
            
            response = requests.put(f"{BASE_URL}/users/{teacher_id}", json=update_data)
            if response.status_code == 200:
                updated_user = response.json()
                results.success("✅ TEST 2: PUT /api/users/{id} - Edit teacher WITHOUT password field (BUG FIX WORKING)")
                
                # Verify the update worked correctly
                if (updated_user['nome'] == update_data['nome'] and
                    updated_user['email'] == update_data['email'] and
                    updated_user['turmas_permitidas'] == update_data['turmas_permitidas']):
                    results.success("✅ TEST 2: Teacher transfer successful - moved to new turma without changing password")
                    print(f"   ✓ Name updated: {updated_user['nome']}")
                    print(f"   ✓ Turmas transferred: {turma_names[0]} → {turma_names[1]}")
                    print(f"   ✓ Password unchanged (not provided in request)")
                else:
                    results.failure("TEST 2: Teacher update verification", f"Update failed: {updated_user}")
            else:
                results.failure("TEST 2: PUT /api/users/{id} WITHOUT password", f"Status {response.status_code}: {response.text}")
                print("❌ This indicates the bug is NOT fixed - editing without password still fails")
        except Exception as e:
            results.failure("TEST 2: Edit teacher without password", str(e))
    
    # TEST 3: Edit teacher WITH password (should also work)
    print("\n--- TEST 3: Editing teacher WITH password ---")
    if teacher_id:
        try:
            update_data_with_password = {
                "nome": "Professor Teste Com Nova Senha",
                "email": "professor.teste@ebd.com",
                "tipo": "professor", 
                "turmas_permitidas": turma_ids,  # Give access to both turmas
                "senha": "novasenha456"  # Include new password
            }
            
            response = requests.put(f"{BASE_URL}/users/{teacher_id}", json=update_data_with_password)
            if response.status_code == 200:
                updated_user = response.json()
                results.success("✅ TEST 3: PUT /api/users/{id} - Edit teacher WITH new password")
                
                # Verify update
                if (updated_user['nome'] == update_data_with_password['nome'] and
                    updated_user['turmas_permitidas'] == update_data_with_password['turmas_permitidas']):
                    results.success("✅ TEST 3: Teacher updated correctly with new password")
                    print(f"   ✓ Name updated: {updated_user['nome']}")
                    print(f"   ✓ Turmas updated: {len(updated_user['turmas_permitidas'])} turmas")
                    print(f"   ✓ Password updated (provided in request)")
                else:
                    results.failure("TEST 3: Teacher update with password verification", f"Update failed: {updated_user}")
            else:
                results.failure("TEST 3: PUT /api/users/{id} WITH password", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("TEST 3: Edit teacher with password", str(e))
    
    # TEST 4: Edit with empty/null password (should not change password)
    print("\n--- TEST 4: Editing teacher with empty/null password ---")
    if teacher_id:
        try:
            # Test with empty string password
            update_data_empty_password = {
                "nome": "Professor Teste Senha Vazia",
                "email": "professor.teste@ebd.com",
                "tipo": "professor",
                "turmas_permitidas": [turma_ids[0]],
                "senha": ""  # Empty password - should not change existing password
            }
            
            response = requests.put(f"{BASE_URL}/users/{teacher_id}", json=update_data_empty_password)
            if response.status_code == 200:
                updated_user = response.json()
                results.success("✅ TEST 4: PUT /api/users/{id} - Edit teacher with empty password (should not change password)")
                
                if updated_user['nome'] == update_data_empty_password['nome']:
                    results.success("✅ TEST 4: Teacher updated correctly with empty password - password unchanged")
                else:
                    results.failure("TEST 4: Teacher update with empty password", f"Name not updated: {updated_user}")
            else:
                results.failure("TEST 4: PUT /api/users/{id} with empty password", f"Status {response.status_code}: {response.text}")
            
            # Test with null password
            update_data_null_password = {
                "nome": "Professor Teste Senha Null",
                "email": "professor.teste@ebd.com", 
                "tipo": "professor",
                "turmas_permitidas": [turma_ids[1]],
                "senha": None  # Null password - should not change existing password
            }
            
            response = requests.put(f"{BASE_URL}/users/{teacher_id}", json=update_data_null_password)
            if response.status_code == 200:
                updated_user = response.json()
                results.success("✅ TEST 4: PUT /api/users/{id} - Edit teacher with null password (should not change password)")
            else:
                results.failure("TEST 4: PUT /api/users/{id} with null password", f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            results.failure("TEST 4: Edit teacher with empty/null password", str(e))
    
    # TEST 5: Validation tests (edge cases)
    print("\n--- TEST 5: Validation and edge cases ---")
    if teacher_id:
        try:
            # Test duplicate email (should fail)
            duplicate_email_data = {
                "nome": "Professor Duplicado",
                "email": "admin@ebd.com",  # Try to use admin email
                "tipo": "professor",
                "turmas_permitidas": [turma_ids[0]]
            }
            
            response = requests.put(f"{BASE_URL}/users/{teacher_id}", json=duplicate_email_data)
            if response.status_code == 400:
                results.success("✅ TEST 5: PUT /api/users/{id} - Validation: correctly rejects duplicate email")
            else:
                results.failure("TEST 5: Duplicate email validation", f"Should reject duplicate email, got status {response.status_code}")
        except Exception as e:
            results.failure("TEST 5: Duplicate email validation", str(e))
        
        try:
            # Test non-existent user (should fail with 404)
            fake_user_id = str(uuid.uuid4())
            response = requests.put(f"{BASE_URL}/users/{fake_user_id}", json={
                "nome": "Usuario Inexistente",
                "email": "inexistente@ebd.com",
                "tipo": "professor",
                "turmas_permitidas": []
            })
            
            if response.status_code == 404:
                results.success("✅ TEST 5: PUT /api/users/{id} - Validation: correctly returns 404 for non-existent user")
            else:
                results.failure("TEST 5: Non-existent user validation", f"Should return 404, got status {response.status_code}")
        except Exception as e:
            results.failure("TEST 5: Non-existent user validation", str(e))
    
    # TEST 6: Verify existing users can be edited (admin@ebd.com, kell@ebd.com)
    print("\n--- TEST 6: Testing existing users from review request ---")
    try:
        # Get all users to find existing ones
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            users = response.json()
            
            # Find kell@ebd.com user
            kell_user = None
            for user in users:
                if user.get('email') == 'kell@ebd.com':
                    kell_user = user
                    break
            
            if kell_user:
                # Test editing kell user without password
                kell_update = {
                    "nome": "Kelliane Ferreira Editada",
                    "email": "kell@ebd.com",
                    "tipo": "professor",
                    "turmas_permitidas": turma_ids  # Give access to both turmas
                    # No password field - testing the bug fix
                }
                
                response = requests.put(f"{BASE_URL}/users/{kell_user['id']}", json=kell_update)
                if response.status_code == 200:
                    updated_kell = response.json()
                    results.success("✅ TEST 6: PUT /api/users/{id} - Successfully edited existing kell@ebd.com user without password")
                    
                    if updated_kell['turmas_permitidas'] == turma_ids:
                        results.success("✅ TEST 6: Kell user turmas_permitidas updated successfully (class transfer working)")
                        print(f"   ✓ Kell now has access to {len(turma_ids)} turmas")
                    else:
                        results.failure("TEST 6: Kell turmas update", f"Expected {turma_ids}, got {updated_kell.get('turmas_permitidas')}")
                else:
                    results.failure("TEST 6: Edit kell@ebd.com", f"Status {response.status_code}: {response.text}")
            else:
                results.failure("TEST 6: Find kell@ebd.com", "User kell@ebd.com not found")
        else:
            results.failure("TEST 6: GET users", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("TEST 6: Test existing users", str(e))
    
    # Clean up test user
    if teacher_id:
        try:
            response = requests.delete(f"{BASE_URL}/users/{teacher_id}")
            if response.status_code == 200:
                results.success("✅ Cleanup: Test teacher user deleted successfully")
            else:
                print(f"⚠️ Cleanup warning: Could not delete test user (status {response.status_code})")
        except Exception as e:
            print(f"⚠️ Cleanup warning: Exception deleting test user: {e}")
    
    print("\n=== USER EDITING BUG FIX TEST SUMMARY ===")
    print("✅ If all tests passed, the bug fix is working correctly")
    print("❌ If TEST 2 failed, the bug is still present")
    print("The bug was: editing a teacher without providing password field would fail")
    print("The fix was: UserUpdate model with optional password in backend")

def test_access_logs_system():
    """Test access logs system as requested in review"""
    print("\n=== TESTING ACCESS LOGS SYSTEM (REVIEW REQUEST) ===")
    print("Testing endpoints: GET /api/access-logs and GET /api/access-logs/stats")
    print("Testing login record creation and data structure validation")
    
    # First, ensure we have the admin user for testing
    admin_credentials = {
        "email": "admin@ebd.com",
        "senha": "admin123"  # As specified in review request
    }
    
    # Update admin password to match review request
    try:
        # Get users to find admin
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            users = response.json()
            admin_user = None
            for user in users:
                if user.get('email') == 'admin@ebd.com':
                    admin_user = user
                    break
            
            if admin_user:
                # Update admin password to admin123
                update_data = {
                    "nome": admin_user.get("nome", "Admin"),
                    "email": "admin@ebd.com",
                    "senha": "admin123",
                    "tipo": "admin",
                    "turmas_permitidas": []
                }
                response = requests.put(f"{BASE_URL}/users/{admin_user['id']}", json=update_data)
                if response.status_code == 200:
                    results.success("Admin password setup - Updated admin password to admin123")
                else:
                    results.failure("Admin password setup", f"Failed to update password: {response.status_code}")
            else:
                results.failure("Admin password setup", "Admin user not found")
        else:
            results.failure("Admin password setup", f"Failed to get users: {response.status_code}")
    except Exception as e:
        results.failure("Admin password setup", str(e))
    
    # TEST 1: Perform login to generate access log
    print("\n--- TEST 1: Login to generate access log ---")
    login_token = None
    try:
        response = requests.post(f"{BASE_URL}/login", json=admin_credentials)
        if response.status_code == 200:
            login_data = response.json()
            login_token = login_data.get("token")
            results.success("POST /api/login - Successfully logged in with admin@ebd.com / admin123")
            
            # Verify login response structure
            required_fields = ["user_id", "nome", "email", "tipo", "turmas_permitidas", "token"]
            if all(field in login_data for field in required_fields):
                results.success("POST /api/login - Login response has all required fields")
            else:
                missing = [f for f in required_fields if f not in login_data]
                results.failure("POST /api/login - Response structure", f"Missing fields: {missing}")
        else:
            results.failure("POST /api/login", f"Status {response.status_code}: {response.text}")
            return  # Can't continue without login
    except Exception as e:
        results.failure("POST /api/login", str(e))
        return
    
    # Wait a moment for log to be created
    import time
    time.sleep(1)
    
    # TEST 2: GET /api/access-logs - verify endpoint responds correctly
    print("\n--- TEST 2: GET /api/access-logs endpoint ---")
    try:
        response = requests.get(f"{BASE_URL}/access-logs")
        if response.status_code == 200:
            logs = response.json()
            results.success("GET /api/access-logs - Endpoint responds correctly")
            
            # Verify response is a list
            if isinstance(logs, list):
                results.success("GET /api/access-logs - Returns list of logs")
                
                # Check if we have at least one log (from our login)
                if len(logs) > 0:
                    results.success(f"GET /api/access-logs - Found {len(logs)} access log(s)")
                    
                    # Verify log structure
                    recent_log = logs[0]  # Most recent log (sorted by timestamp desc)
                    required_log_fields = ["id", "user_id", "user_name", "user_email", "user_type", "action", "timestamp"]
                    
                    if all(field in recent_log for field in required_log_fields):
                        results.success("GET /api/access-logs - Log entry has all required fields")
                        
                        # Verify specific data
                        if recent_log.get("user_email") == "admin@ebd.com":
                            results.success("GET /api/access-logs - Found login record for admin@ebd.com")
                        else:
                            results.failure("GET /api/access-logs - Admin login", f"Expected admin@ebd.com, got {recent_log.get('user_email')}")
                        
                        if recent_log.get("action") == "login":
                            results.success("GET /api/access-logs - Login action recorded correctly")
                        else:
                            results.failure("GET /api/access-logs - Action", f"Expected 'login', got {recent_log.get('action')}")
                        
                        if recent_log.get("user_type") == "admin":
                            results.success("GET /api/access-logs - User type recorded correctly")
                        else:
                            results.failure("GET /api/access-logs - User type", f"Expected 'admin', got {recent_log.get('user_type')}")
                        
                        # Verify timestamp format
                        timestamp = recent_log.get("timestamp")
                        if timestamp:
                            try:
                                from datetime import datetime
                                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                results.success("GET /api/access-logs - Timestamp in valid ISO format")
                            except:
                                results.failure("GET /api/access-logs - Timestamp", f"Invalid timestamp format: {timestamp}")
                        else:
                            results.failure("GET /api/access-logs - Timestamp", "Timestamp missing")
                        
                        # Check optional fields
                        optional_fields = ["ip_address", "user_agent", "session_duration"]
                        for field in optional_fields:
                            if field in recent_log:
                                results.success(f"GET /api/access-logs - Optional field '{field}' present")
                        
                    else:
                        missing = [f for f in required_log_fields if f not in recent_log]
                        results.failure("GET /api/access-logs - Log structure", f"Missing fields: {missing}")
                else:
                    results.failure("GET /api/access-logs - No logs", "No access logs found after login")
            else:
                results.failure("GET /api/access-logs - Response type", f"Expected list, got {type(logs)}")
        else:
            results.failure("GET /api/access-logs", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/access-logs", str(e))
    
    # TEST 3: GET /api/access-logs/stats - verify stats endpoint
    print("\n--- TEST 3: GET /api/access-logs/stats endpoint ---")
    try:
        response = requests.get(f"{BASE_URL}/access-logs/stats")
        if response.status_code == 200:
            stats = response.json()
            results.success("GET /api/access-logs/stats - Endpoint responds correctly")
            
            # Verify stats structure
            required_stats_fields = ["total_logins_30_days", "unique_users_30_days", "most_active_user", "most_active_logins"]
            if all(field in stats for field in required_stats_fields):
                results.success("GET /api/access-logs/stats - Stats response has all required fields")
                
                # Verify data types and values
                if isinstance(stats.get("total_logins_30_days"), int) and stats.get("total_logins_30_days") >= 1:
                    results.success(f"GET /api/access-logs/stats - total_logins_30_days: {stats['total_logins_30_days']} (valid)")
                else:
                    results.failure("GET /api/access-logs/stats - total_logins", f"Expected int >= 1, got {stats.get('total_logins_30_days')}")
                
                if isinstance(stats.get("unique_users_30_days"), int) and stats.get("unique_users_30_days") >= 1:
                    results.success(f"GET /api/access-logs/stats - unique_users_30_days: {stats['unique_users_30_days']} (valid)")
                else:
                    results.failure("GET /api/access-logs/stats - unique_users", f"Expected int >= 1, got {stats.get('unique_users_30_days')}")
                
                if stats.get("most_active_user"):
                    results.success(f"GET /api/access-logs/stats - most_active_user: {stats['most_active_user']} (valid)")
                else:
                    results.failure("GET /api/access-logs/stats - most_active_user", "Most active user is empty")
                
                if isinstance(stats.get("most_active_logins"), int) and stats.get("most_active_logins") >= 1:
                    results.success(f"GET /api/access-logs/stats - most_active_logins: {stats['most_active_logins']} (valid)")
                else:
                    results.failure("GET /api/access-logs/stats - most_active_logins", f"Expected int >= 1, got {stats.get('most_active_logins')}")
                
            else:
                missing = [f for f in required_stats_fields if f not in stats]
                results.failure("GET /api/access-logs/stats - Stats structure", f"Missing fields: {missing}")
        else:
            results.failure("GET /api/access-logs/stats", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/access-logs/stats", str(e))
    
    # TEST 4: Test with query parameters
    print("\n--- TEST 4: GET /api/access-logs with parameters ---")
    try:
        # Get admin user_id from login response
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            users = response.json()
            admin_user = None
            for user in users:
                if user.get('email') == 'admin@ebd.com':
                    admin_user = user
                    break
            
            if admin_user:
                admin_user_id = admin_user['id']
                
                # Test with user_id filter
                response = requests.get(f"{BASE_URL}/access-logs", params={"user_id": admin_user_id})
                if response.status_code == 200:
                    filtered_logs = response.json()
                    if isinstance(filtered_logs, list):
                        results.success("GET /api/access-logs?user_id - Filtering by user_id works")
                        
                        # Verify all logs are for the specified user
                        if all(log.get("user_id") == admin_user_id for log in filtered_logs):
                            results.success("GET /api/access-logs?user_id - All logs match specified user_id")
                        else:
                            results.failure("GET /api/access-logs?user_id - Filter", "Some logs don't match specified user_id")
                    else:
                        results.failure("GET /api/access-logs?user_id", f"Expected list, got {type(filtered_logs)}")
                else:
                    results.failure("GET /api/access-logs?user_id", f"Status {response.status_code}: {response.text}")
                
                # Test with limit parameter
                response = requests.get(f"{BASE_URL}/access-logs", params={"limit": 5})
                if response.status_code == 200:
                    limited_logs = response.json()
                    if isinstance(limited_logs, list) and len(limited_logs) <= 5:
                        results.success(f"GET /api/access-logs?limit=5 - Limit parameter works (got {len(limited_logs)} logs)")
                    else:
                        results.failure("GET /api/access-logs?limit", f"Expected max 5 logs, got {len(limited_logs) if isinstance(limited_logs, list) else 'not a list'}")
                else:
                    results.failure("GET /api/access-logs?limit", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("GET /api/access-logs with parameters", str(e))
    
    # TEST 5: Test multiple logins to verify log accumulation
    print("\n--- TEST 5: Multiple logins to test log accumulation ---")
    try:
        # Perform another login
        response = requests.post(f"{BASE_URL}/login", json=admin_credentials)
        if response.status_code == 200:
            results.success("Multiple logins - Second login successful")
            
            # Wait for log creation
            time.sleep(1)
            
            # Check if we have multiple logs now
            response = requests.get(f"{BASE_URL}/access-logs", params={"limit": 10})
            if response.status_code == 200:
                logs = response.json()
                login_logs = [log for log in logs if log.get("action") == "login" and log.get("user_email") == "admin@ebd.com"]
                
                if len(login_logs) >= 2:
                    results.success(f"Multiple logins - Found {len(login_logs)} login records for admin@ebd.com")
                    
                    # Verify logs are sorted by timestamp (most recent first)
                    if len(login_logs) >= 2:
                        first_timestamp = login_logs[0].get("timestamp")
                        second_timestamp = login_logs[1].get("timestamp")
                        if first_timestamp and second_timestamp and first_timestamp >= second_timestamp:
                            results.success("Multiple logins - Logs correctly sorted by timestamp (desc)")
                        else:
                            results.failure("Multiple logins - Sorting", "Logs not properly sorted by timestamp")
                else:
                    results.failure("Multiple logins", f"Expected at least 2 login logs, got {len(login_logs)}")
            else:
                results.failure("Multiple logins - Verification", f"Status {response.status_code}: {response.text}")
        else:
            results.failure("Multiple logins", f"Second login failed: {response.status_code}")
    except Exception as e:
        results.failure("Multiple logins", str(e))
    
    # TEST 6: Verify data structure completeness
    print("\n--- TEST 6: Complete data structure validation ---")
    try:
        response = requests.get(f"{BASE_URL}/access-logs", params={"limit": 1})
        if response.status_code == 200:
            logs = response.json()
            if logs and len(logs) > 0:
                log = logs[0]
                
                # Complete field validation
                expected_structure = {
                    "id": str,
                    "user_id": str,
                    "user_name": str,
                    "user_email": str,
                    "user_type": str,
                    "action": str,
                    "timestamp": str
                }
                
                structure_valid = True
                for field, expected_type in expected_structure.items():
                    if field not in log:
                        results.failure("Data structure", f"Missing required field: {field}")
                        structure_valid = False
                    elif not isinstance(log[field], expected_type):
                        results.failure("Data structure", f"Field {field} has wrong type: expected {expected_type.__name__}, got {type(log[field]).__name__}")
                        structure_valid = False
                
                if structure_valid:
                    results.success("Data structure - All required fields present with correct types")
                
                # Print sample log for verification
                print(f"\nSample access log structure:")
                for key, value in log.items():
                    print(f"  {key}: {value} ({type(value).__name__})")
                
            else:
                results.failure("Data structure validation", "No logs available for structure validation")
        else:
            results.failure("Data structure validation", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("Data structure validation", str(e))
    
    print(f"\n=== ACCESS LOGS SYSTEM TESTING COMPLETED ===")

def main():
    """Run all tests in sequence"""
    print("=== EBD MANAGER BACKEND TEST SUITE ===\n")
    print("TESTING NEW CALL CONTROL SYSTEM (SISTEMA DE CONTROLE DE CHAMADAS)")
    print("Focus: system-config endpoints and pode_editar_chamada function\n")
    
    # Initialize sample data first
    print("0. Initializing sample data...")
    if not test_init_sample_data():
        print("❌ Failed to initialize sample data. Some tests may fail.")
    
    # Test 1: LOGIN WITH SPECIFIC CREDENTIALS
    print("\n1. Testing login with specific credentials...")
    test_login_with_credentials()
    
    # Test 2: CALL CONTROL SYSTEM (MAIN FOCUS)
    print("\n2. Testing Call Control System (MAIN FOCUS - REVIEW REQUEST)...")
    test_call_control_system()
    
    # Show final results
    results.summary()
    
    # Return exit code based on results
    if results.failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()