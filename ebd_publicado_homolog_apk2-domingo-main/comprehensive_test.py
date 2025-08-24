#!/usr/bin/env python3
"""
Additional comprehensive tests for EBD Manager System
Tests edge cases and additional validations
"""

import requests
import json
from datetime import datetime, date, timedelta
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

def get_next_sunday():
    """Get next Sunday date for testing"""
    today = date.today()
    days_ahead = 6 - today.weekday()  # Sunday is 6
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days_ahead)

SUNDAY_DATE = get_next_sunday()

def test_comprehensive_workflow():
    """Test complete workflow with real data"""
    print("=== COMPREHENSIVE WORKFLOW TEST ===")
    
    # 1. Initialize data
    response = requests.post(f"{BASE_URL}/init-sample-data")
    assert response.status_code == 200, f"Init failed: {response.text}"
    print("✅ Sample data initialized")
    
    # 2. Get turmas and students
    turmas_response = requests.get(f"{BASE_URL}/turmas")
    assert turmas_response.status_code == 200
    turmas = turmas_response.json()
    assert len(turmas) >= 3
    genesis_turma = next(t for t in turmas if t['nome'] == 'Gênesis')
    print("✅ Turmas retrieved")
    
    students_response = requests.get(f"{BASE_URL}/students", params={"turma_id": genesis_turma['id']})
    assert students_response.status_code == 200
    students = students_response.json()
    assert len(students) >= 2  # Márcio and Késia should be in Gênesis
    print("✅ Students retrieved")
    
    # 3. Create attendance records for multiple students
    attendance_records = []
    for i, student in enumerate(students[:2]):
        attendance_data = {
            "aluno_id": student['id'],
            "turma_id": genesis_turma['id'],
            "data": SUNDAY_DATE.isoformat(),
            "status": "presente" if i == 0 else "ausente",
            "oferta": 15.0 if i == 0 else 0.0,
            "biblias_entregues": 1 if i == 0 else 0,
            "revistas_entregues": 1 if i == 0 else 0
        }
        response = requests.post(f"{BASE_URL}/attendance", json=attendance_data)
        assert response.status_code == 200, f"Attendance creation failed: {response.text}"
        attendance_records.append(response.json())
    print("✅ Individual attendance records created")
    
    # 4. Test dashboard report
    report_response = requests.get(f"{BASE_URL}/reports/dashboard", 
                                 params={"data": SUNDAY_DATE.isoformat()})
    assert report_response.status_code == 200
    reports = report_response.json()
    
    # Find Genesis report
    genesis_report = next(r for r in reports if r['turma_nome'] == 'Gênesis')
    assert genesis_report['matriculados'] >= 2
    assert genesis_report['presentes'] == 1
    assert genesis_report['ausentes'] == genesis_report['matriculados'] - 1
    assert genesis_report['total_ofertas'] == 15.0
    assert genesis_report['total_biblias'] == 1
    assert genesis_report['total_revistas'] == 1
    print("✅ Dashboard report calculations correct")
    
    # 5. Test bulk attendance (should replace individual records)
    bulk_data = []
    for i, student in enumerate(students):
        bulk_data.append({
            "aluno_id": student['id'],
            "turma_id": genesis_turma['id'],
            "data": SUNDAY_DATE.isoformat(),
            "status": "presente",
            "oferta": 5.0,
            "biblias_entregues": 0,
            "revistas_entregues": 1
        })
    
    bulk_response = requests.post(f"{BASE_URL}/attendance/bulk/{genesis_turma['id']}", 
                                params={"data": SUNDAY_DATE.isoformat()},
                                json=bulk_data)
    assert bulk_response.status_code == 200
    print("✅ Bulk attendance saved")
    
    # 6. Verify bulk attendance replaced individual records
    final_report_response = requests.get(f"{BASE_URL}/reports/dashboard", 
                                       params={"data": SUNDAY_DATE.isoformat()})
    assert final_report_response.status_code == 200
    final_reports = final_report_response.json()
    
    final_genesis_report = next(r for r in final_reports if r['turma_nome'] == 'Gênesis')
    assert final_genesis_report['presentes'] == len(students)  # All should be present now
    assert final_genesis_report['ausentes'] == 0  # No absents
    assert final_genesis_report['total_ofertas'] == len(students) * 5.0
    print("✅ Bulk attendance correctly replaced individual records")
    
    print("\n🎉 COMPREHENSIVE WORKFLOW TEST PASSED!")

def test_uuid_validation():
    """Test that all IDs are valid UUIDs"""
    print("\n=== UUID VALIDATION TEST ===")
    
    # Get turmas and validate UUIDs
    response = requests.get(f"{BASE_URL}/turmas")
    turmas = response.json()
    for turma in turmas:
        try:
            uuid.UUID(turma['id'])
        except ValueError:
            raise AssertionError(f"Invalid UUID for turma: {turma['id']}")
    print("✅ All turma IDs are valid UUIDs")
    
    # Get students and validate UUIDs
    response = requests.get(f"{BASE_URL}/students")
    students = response.json()
    for student in students:
        try:
            uuid.UUID(student['id'])
            uuid.UUID(student['turma_id'])
        except ValueError:
            raise AssertionError(f"Invalid UUID for student: {student['id']} or turma_id: {student['turma_id']}")
    print("✅ All student IDs and turma_ids are valid UUIDs")
    
    print("🎉 UUID VALIDATION TEST PASSED!")

def test_data_integrity():
    """Test data integrity and constraints"""
    print("\n=== DATA INTEGRITY TEST ===")
    
    # Test that deleted turmas don't appear in active list
    new_turma = {"nome": "Turma Teste Delete", "descricao": "Para teste"}
    response = requests.post(f"{BASE_URL}/turmas", json=new_turma)
    turma = response.json()
    turma_id = turma['id']
    
    # Delete the turma
    requests.delete(f"{BASE_URL}/turmas/{turma_id}")
    
    # Verify it's not in active list
    response = requests.get(f"{BASE_URL}/turmas")
    active_turmas = response.json()
    active_ids = [t['id'] for t in active_turmas]
    assert turma_id not in active_ids
    print("✅ Soft delete works for turmas")
    
    # Test that students can't be created with non-existent turma
    fake_turma_id = str(uuid.uuid4())
    invalid_student = {
        "nome_completo": "Teste Invalid",
        "data_nascimento": "1990-01-01",
        "contato": "test@test.com",
        "turma_id": fake_turma_id
    }
    response = requests.post(f"{BASE_URL}/students", json=invalid_student)
    assert response.status_code == 404
    print("✅ Student creation validates turma existence")
    
    print("🎉 DATA INTEGRITY TEST PASSED!")

if __name__ == "__main__":
    try:
        test_comprehensive_workflow()
        test_uuid_validation()
        test_data_integrity()
        print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)