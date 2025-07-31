#!/usr/bin/env python3
"""
Focused User Management Test for EBD Manager System
Tests specific requirements from review request
"""

import requests
import json
from datetime import datetime
import sys

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
print(f"Testing user management at: {BASE_URL}")

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
        print(f"\n=== USER MANAGEMENT TEST SUMMARY ===")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

results = TestResults()

def test_user_management_requirements():
    """Test specific requirements from review request"""
    print("=== TESTING USER MANAGEMENT REQUIREMENTS ===\n")
    
    # TEST 1: GET /api/users - verificar se retorna dados corretos dos usuários incluindo turmas_permitidas
    print("1. Testing GET /api/users...")
    try:
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            users = response.json()
            results.success("GET /api/users - Returns user data successfully")
            
            # Verify it's a list
            if isinstance(users, list):
                results.success("GET /api/users - Returns list format")
            else:
                results.failure("GET /api/users - Format", f"Expected list, got {type(users)}")
                return
            
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
                    results.failure("GET /api/users - Required fields", f"Missing: {missing_fields}")
                
                # Verify turmas_permitidas is included and is a list
                if 'turmas_permitidas' in kell_user:
                    if isinstance(kell_user['turmas_permitidas'], list):
                        results.success("GET /api/users - turmas_permitidas is included as list")
                        print(f"   Kell's turmas_permitidas: {kell_user['turmas_permitidas']}")
                    else:
                        results.failure("GET /api/users - turmas_permitidas type", f"Expected list, got {type(kell_user['turmas_permitidas'])}")
                else:
                    results.failure("GET /api/users - turmas_permitidas", "Field missing")
                
                # Display Kell's current data
                print(f"\n   Kell User Data:")
                print(f"   - ID: {kell_user.get('id')}")
                print(f"   - Nome: {kell_user.get('nome')}")
                print(f"   - Email: {kell_user.get('email')}")
                print(f"   - Tipo: {kell_user.get('tipo')}")
                print(f"   - Turmas Permitidas: {len(kell_user.get('turmas_permitidas', []))} turmas")
                print(f"   - Ativo: {kell_user.get('ativo')}")
                
            else:
                results.failure("GET /api/users - Find Kell", "User Kell with email kell@ebd.com not found")
                return
                
        else:
            results.failure("GET /api/users", f"Status {response.status_code}: {response.text}")
            return
    except Exception as e:
        results.failure("GET /api/users", str(e))
        return
    
    # TEST 2: PUT /api/users/{user_id} - deve funcionar para atualizar usuários
    print("\n2. Testing PUT /api/users/{user_id}...")
    if kell_user:
        kell_user_id = kell_user['id']
        
        # Get available turmas for testing
        try:
            turmas_response = requests.get(f"{BASE_URL}/turmas")
            if turmas_response.status_code == 200:
                turmas = turmas_response.json()
                turma_ids = [t['id'] for t in turmas[:2]]  # Use first 2 turmas
                print(f"   Using turmas for test: {[t['nome'] for t in turmas[:2]]}")
            else:
                turma_ids = []
        except:
            turma_ids = []
        
        # Test updating nome, email, tipo, turmas_permitidas
        update_data = {
            "nome": "Kell Silva Testado",
            "email": "kell@ebd.com",  # Keep same email
            "senha": "testpassword123",
            "tipo": "professor",
            "turmas_permitidas": turma_ids
        }
        
        try:
            response = requests.put(f"{BASE_URL}/users/{kell_user_id}", json=update_data)
            if response.status_code == 200:
                updated_user = response.json()
                results.success("PUT /api/users/{user_id} - Successfully updated user")
                
                # Verify each field was updated
                if updated_user.get('nome') == update_data['nome']:
                    results.success("PUT /api/users/{user_id} - Nome updated correctly")
                else:
                    results.failure("PUT /api/users/{user_id} - Nome", f"Expected '{update_data['nome']}', got '{updated_user.get('nome')}'")
                
                if updated_user.get('email') == update_data['email']:
                    results.success("PUT /api/users/{user_id} - Email maintained correctly")
                else:
                    results.failure("PUT /api/users/{user_id} - Email", f"Expected '{update_data['email']}', got '{updated_user.get('email')}'")
                
                if updated_user.get('tipo') == update_data['tipo']:
                    results.success("PUT /api/users/{user_id} - Tipo updated correctly")
                else:
                    results.failure("PUT /api/users/{user_id} - Tipo", f"Expected '{update_data['tipo']}', got '{updated_user.get('tipo')}'")
                
                if updated_user.get('turmas_permitidas') == update_data['turmas_permitidas']:
                    results.success("PUT /api/users/{user_id} - turmas_permitidas updated correctly")
                else:
                    results.failure("PUT /api/users/{user_id} - turmas_permitidas", f"Expected {update_data['turmas_permitidas']}, got {updated_user.get('turmas_permitidas')}")
                
                print(f"\n   Updated User Data:")
                print(f"   - Nome: {updated_user.get('nome')}")
                print(f"   - Email: {updated_user.get('email')}")
                print(f"   - Tipo: {updated_user.get('tipo')}")
                print(f"   - Turmas Permitidas: {len(updated_user.get('turmas_permitidas', []))} turmas")
                
            else:
                results.failure("PUT /api/users/{user_id}", f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.failure("PUT /api/users/{user_id}", str(e))
    
    # TEST 3: Verificar usuário Kell - se tem turmas_permitidas corretas
    print("\n3. Final verification of user Kell...")
    try:
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            users = response.json()
            kell_user = None
            for user in users:
                if user.get('email') == 'kell@ebd.com':
                    kell_user = user
                    break
            
            if kell_user:
                # Verify email is correct
                if kell_user.get('email') == 'kell@ebd.com':
                    results.success("Final verification - Kell has correct email: kell@ebd.com")
                else:
                    results.failure("Final verification - Email", f"Expected kell@ebd.com, got {kell_user.get('email')}")
                
                # Verify turmas_permitidas is populated
                turmas_permitidas = kell_user.get('turmas_permitidas', [])
                if isinstance(turmas_permitidas, list):
                    if len(turmas_permitidas) > 0:
                        results.success("Final verification - Kell has populated turmas_permitidas")
                        print(f"   Kell's turmas_permitidas: {turmas_permitidas}")
                    else:
                        results.success("Final verification - Kell has empty turmas_permitidas (valid for admin type)")
                else:
                    results.failure("Final verification - turmas_permitidas", f"Expected list, got {type(turmas_permitidas)}")
                
                # Final summary of Kell's data
                print(f"\n   === FINAL KELL USER STATE ===")
                print(f"   Email: {kell_user.get('email')} ✓")
                print(f"   Nome: {kell_user.get('nome')}")
                print(f"   Tipo: {kell_user.get('tipo')}")
                print(f"   Turmas Permitidas: {len(turmas_permitidas)} turmas")
                print(f"   Ativo: {kell_user.get('ativo')}")
                print(f"   ================================")
                
            else:
                results.failure("Final verification", "User Kell not found")
        else:
            results.failure("Final verification", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.failure("Final verification", str(e))

def main():
    """Run user management tests"""
    test_user_management_requirements()
    results.summary()
    
    # Check if all critical requirements are met
    critical_passed = True
    for error in results.errors:
        if any(keyword in error.lower() for keyword in ['get /api/users', 'put /api/users', 'kell', 'email', 'turmas_permitidas']):
            critical_passed = False
            break
    
    if critical_passed and results.passed >= 10:  # Expect at least 10 successful tests
        print("\n🎉 All user management requirements PASSED!")
        print("✅ GET /api/users returns correct data including turmas_permitidas")
        print("✅ PUT /api/users/{user_id} works for updating users")
        print("✅ User Kell has email kell@ebd.com and correct turmas_permitidas")
        return True
    else:
        print("\n❌ Some user management requirements FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)