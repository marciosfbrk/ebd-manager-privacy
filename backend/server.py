from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date, timedelta
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class AttendanceStatus(str, Enum):
    PRESENT = "presente"
    ABSENT = "ausente"
    VISITOR = "visitante"
    POST_CALL = "pos_chamada"

class UserRole(str, Enum):
    ADMIN = "secretaria"
    PROFESSOR = "professor"

# Models
class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome_completo: str
    data_nascimento: str  # Store as string to avoid MongoDB serialization issues
    contato: str
    turma_id: str
    ativo: bool = True
    criado_em: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class Licao(BaseModel):
    titulo: str
    data: str  # Format: YYYY-MM-DD

class Revista(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tema: str
    licoes: List[Licao]
    turma_ids: List[str]  # IDs das turmas que usam esta revista
    ativa: bool = True
    criada_em: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class RevistaCreate(BaseModel):
    tema: str
    licoes: List[Licao]
    turma_ids: List[str]

class StudentCreate(BaseModel):
    nome_completo: str
    data_nascimento: str
    contato: str
    turma_id: str

class StudentUpdate(BaseModel):
    nome_completo: Optional[str] = None
    data_nascimento: Optional[str] = None
    contato: Optional[str] = None
    turma_id: Optional[str] = None

class StudentTransfer(BaseModel):
    nova_turma_id: str

class Turma(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    descricao: Optional[str] = None
    ativa: bool = True
    criada_em: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class TurmaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None

class Attendance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aluno_id: str
    turma_id: str
    data: str  # Store as string to avoid MongoDB serialization issues
    status: AttendanceStatus
    oferta: Optional[float] = 0.0
    biblias_entregues: Optional[int] = 0
    revistas_entregues: Optional[int] = 0
    criado_em: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class AttendanceCreate(BaseModel):
    aluno_id: str
    turma_id: str
    data: str
    status: AttendanceStatus
    oferta: Optional[float] = 0.0
    biblias_entregues: Optional[int] = 0
    revistas_entregues: Optional[int] = 0

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    oferta: Optional[float] = None
    biblias_entregues: Optional[int] = None
    revistas_entregues: Optional[int] = None

class AttendanceReport(BaseModel):
    turma_nome: str
    turma_id: str
    data: str
    matriculados: int
    presentes: int
    ausentes: int
    visitantes: int
    pos_chamada: int
    total_ofertas: float
    total_biblias: int
    total_revistas: int

class BulkAttendanceItem(BaseModel):
    aluno_id: str
    status: AttendanceStatus
    oferta: Optional[float] = 0.0
    biblias_entregues: Optional[int] = 0
    revistas_entregues: Optional[int] = 0

# Helper functions
def is_sunday(date_str: str) -> bool:
    """Check if a date string represents a Sunday"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        return date_obj.weekday() == 6  # Sunday is 6
    except:
        return False

# Routes - Turmas
@api_router.post("/turmas", response_model=Turma)
async def create_turma(turma: TurmaCreate):
    turma_dict = turma.dict()
    turma_obj = Turma(**turma_dict)
    await db.turmas.insert_one(turma_obj.dict())
    return turma_obj

@api_router.get("/turmas", response_model=List[Turma])
async def get_turmas():
    turmas = await db.turmas.find({"ativa": True}).to_list(1000)
    return [Turma(**turma) for turma in turmas]

@api_router.get("/turmas/{turma_id}", response_model=Turma)
async def get_turma(turma_id: str):
    turma = await db.turmas.find_one({"id": turma_id, "ativa": True})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    return Turma(**turma)

@api_router.put("/turmas/{turma_id}", response_model=Turma)
async def update_turma(turma_id: str, turma_update: TurmaCreate):
    result = await db.turmas.update_one(
        {"id": turma_id, "ativa": True},
        {"$set": turma_update.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    turma = await db.turmas.find_one({"id": turma_id})
    return Turma(**turma)

@api_router.delete("/turmas/{turma_id}")
async def delete_turma(turma_id: str):
    result = await db.turmas.update_one(
        {"id": turma_id}, 
        {"$set": {"ativa": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    return {"message": "Turma removida com sucesso"}

# Routes - Students
@api_router.post("/students", response_model=Student)
async def create_student(student: StudentCreate):
    # Verificar se a turma existe
    turma = await db.turmas.find_one({"id": student.turma_id, "ativa": True})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    student_dict = student.dict()
    student_obj = Student(**student_dict)
    await db.students.insert_one(student_obj.dict())
    return student_obj

@api_router.get("/students", response_model=List[Student])
async def get_students(turma_id: Optional[str] = None):
    filter_dict = {"ativo": True}
    if turma_id:
        filter_dict["turma_id"] = turma_id
    
    students = await db.students.find(filter_dict).to_list(1000)
    return [Student(**student) for student in students]

@api_router.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    student = await db.students.find_one({"id": student_id, "ativo": True})
    if not student:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return Student(**student)

@api_router.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: str, student_update: StudentUpdate):
    update_dict = {k: v for k, v in student_update.dict().items() if v is not None}
    
    if "turma_id" in update_dict:
        turma = await db.turmas.find_one({"id": update_dict["turma_id"], "ativa": True})
        if not turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    result = await db.students.update_one(
        {"id": student_id, "ativo": True},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    student = await db.students.find_one({"id": student_id})
    return Student(**student)

@api_router.delete("/students/{student_id}")
async def delete_student(student_id: str):
    result = await db.students.update_one(
        {"id": student_id}, 
        {"$set": {"ativo": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return {"message": "Aluno removido com sucesso"}

@api_router.post("/students/{student_id}/transfer")
async def transfer_student(student_id: str, transfer_data: StudentTransfer):
    # Verificar se o aluno existe
    student = await db.students.find_one({"id": student_id, "ativo": True})
    if not student:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Verificar se a nova turma existe
    turma = await db.turmas.find_one({"id": transfer_data.nova_turma_id, "ativa": True})
    if not turma:
        raise HTTPException(status_code=404, detail="Nova turma não encontrada")
    
    # Atualizar turma do aluno
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"turma_id": transfer_data.nova_turma_id}}
    )
    
    # Buscar aluno atualizado
    updated_student = await db.students.find_one({"id": student_id})
    return Student(**updated_student)

# Routes - Attendance
@api_router.post("/attendance", response_model=Attendance)
async def create_attendance(attendance: AttendanceCreate):
    # Verificar se é domingo
    if not is_sunday(attendance.data):
        raise HTTPException(status_code=400, detail="Chamada só pode ser feita aos domingos")
    
    # Verificar se o aluno existe
    student = await db.students.find_one({"id": attendance.aluno_id, "ativo": True})
    if not student:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Verificar se já existe chamada para este aluno nesta data
    existing = await db.attendance.find_one({
        "aluno_id": attendance.aluno_id,
        "data": attendance.data
    })
    if existing:
        raise HTTPException(status_code=400, detail="Chamada já existe para este aluno nesta data")
    
    attendance_dict = attendance.dict()
    attendance_obj = Attendance(**attendance_dict)
    await db.attendance.insert_one(attendance_obj.dict())
    return attendance_obj

@api_router.get("/attendance", response_model=List[Attendance])
async def get_attendance(turma_id: Optional[str] = None, data: Optional[str] = None):
    filter_dict = {}
    if turma_id:
        filter_dict["turma_id"] = turma_id
    if data:
        filter_dict["data"] = data
    
    attendance = await db.attendance.find(filter_dict).to_list(1000)
    return [Attendance(**att) for att in attendance]

@api_router.put("/attendance/{attendance_id}", response_model=Attendance)
async def update_attendance(attendance_id: str, attendance_update: AttendanceUpdate):
    update_dict = {k: v for k, v in attendance_update.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    result = await db.attendance.update_one(
        {"id": attendance_id},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Registro de chamada não encontrado")
    
    attendance = await db.attendance.find_one({"id": attendance_id})
    return Attendance(**attendance)

@api_router.delete("/attendance/{attendance_id}")
async def delete_attendance(attendance_id: str):
    result = await db.attendance.delete_one({"id": attendance_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Registro de chamada não encontrado")
    return {"message": "Registro de chamada removido com sucesso"}

# Routes - Reports
@api_router.get("/reports/dashboard", response_model=List[AttendanceReport])
async def get_dashboard_report(data: Optional[str] = None):
    if not data:
        data = datetime.now().strftime("%Y-%m-%d")
    
    # Buscar todas as turmas ativas
    turmas = await db.turmas.find({"ativa": True}).to_list(1000)
    
    reports = []
    for turma in turmas:
        # Contar alunos matriculados
        matriculados = await db.students.count_documents({
            "turma_id": turma["id"],
            "ativo": True
        })
        
        # Buscar presenças do dia
        attendance_records = await db.attendance.find({
            "turma_id": turma["id"],
            "data": data
        }).to_list(1000)
        
        # Calcular estatísticas
        presentes = len([a for a in attendance_records if a["status"] == "presente"])
        visitantes = len([a for a in attendance_records if a["status"] == "visitante"])
        pos_chamada = len([a for a in attendance_records if a["status"] == "pos_chamada"])
        ausentes = matriculados - presentes
        
        total_ofertas = round(sum(a.get("oferta", 0) for a in attendance_records), 2)
        total_biblias = sum(a.get("biblias_entregues", 0) for a in attendance_records)
        total_revistas = sum(a.get("revistas_entregues", 0) for a in attendance_records)
        
        report = AttendanceReport(
            turma_nome=turma["nome"],
            turma_id=turma["id"],
            data=data,
            matriculados=matriculados,
            presentes=presentes,
            ausentes=ausentes,
            visitantes=visitantes,
            pos_chamada=pos_chamada,
            total_ofertas=total_ofertas,
            total_biblias=total_biblias,
            total_revistas=total_revistas
        )
        reports.append(report)
    
    return reports

# Routes - Bulk Attendance for a turma
@api_router.post("/attendance/bulk/{turma_id}")
async def bulk_attendance(turma_id: str, data: str = Query(...), attendance_list: List[BulkAttendanceItem] = []):
    # Verificar se é domingo
    if not is_sunday(data):
        raise HTTPException(status_code=400, detail="Chamada só pode ser feita aos domingos")
    
    # Verificar se a turma existe
    turma = await db.turmas.find_one({"id": turma_id, "ativa": True})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # Remover registros existentes da data
    await db.attendance.delete_many({"turma_id": turma_id, "data": data})
    
    # Inserir novos registros
    if attendance_list:
        attendance_objects = []
        for att_data in attendance_list:
            att_dict = att_data.dict()
            att_dict["data"] = data
            att_dict["turma_id"] = turma_id
            attendance_obj = Attendance(**att_dict)
            attendance_objects.append(attendance_obj.dict())
        
        await db.attendance.insert_many(attendance_objects)
    
    return {"message": f"Chamada salva com sucesso para {len(attendance_list)} registros"}

# Initialize sample data
@api_router.post("/init-sample-data")
async def init_sample_data():
    # Limpar dados existentes
    await db.turmas.delete_many({})
    await db.students.delete_many({})
    await db.attendance.delete_many({})
    
    # Criar turmas de exemplo
    turmas = [
        {"id": str(uuid.uuid4()), "nome": "Gênesis", "descricao": "Turma dos adultos", "ativa": True, "criada_em": datetime.utcnow().isoformat()},
        {"id": str(uuid.uuid4()), "nome": "Primários", "descricao": "Turma das crianças", "ativa": True, "criada_em": datetime.utcnow().isoformat()},
        {"id": str(uuid.uuid4()), "nome": "Juvenil", "descricao": "Turma dos jovens", "ativa": True, "criada_em": datetime.utcnow().isoformat()}
    ]
    
    await db.turmas.insert_many(turmas)
    
    # Criar alunos de exemplo
    students = [
        {
            "id": str(uuid.uuid4()),
            "nome_completo": "Márcio Ferreira",
            "data_nascimento": "1980-05-15",
            "contato": "marcio@email.com",
            "turma_id": turmas[0]["id"],
            "ativo": True,
            "criado_em": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nome_completo": "Késia Ferreira",
            "data_nascimento": "1985-08-22",
            "contato": "kesia@email.com",
            "turma_id": turmas[0]["id"],
            "ativo": True,
            "criado_em": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nome_completo": "Gustavo Ferreira",
            "data_nascimento": "2010-03-10",
            "contato": "gustavo@email.com",
            "turma_id": turmas[1]["id"],
            "ativo": True,
            "criado_em": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nome_completo": "Gael Ferreira",
            "data_nascimento": "2012-12-05",
            "contato": "gael@email.com",
            "turma_id": turmas[1]["id"],
            "ativo": True,
            "criado_em": datetime.utcnow().isoformat()
        }
    ]
    
    await db.students.insert_many(students)
    
    return {"message": "Dados de exemplo criados com sucesso", "turmas": len(turmas), "alunos": len(students)}

# User Management Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    email: str
    senha_hash: str
    tipo: str  # 'admin' ou 'professor'
    turmas_permitidas: List[str] = []  # IDs das turmas que pode acessar (vazio = todas para admin)
    ativo: bool = True
    criado_em: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class UserCreate(BaseModel):
    nome: str
    email: str
    senha: str
    tipo: str  # 'admin' ou 'professor'
    turmas_permitidas: List[str] = []

class UserLogin(BaseModel):
    email: str
    senha: str

class LoginResponse(BaseModel):
    user_id: str
    nome: str
    email: str
    tipo: str
    turmas_permitidas: List[str]
    token: str

# Simple password hashing (you should use bcrypt in production)
def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

# Routes - User Management
@api_router.post("/login", response_model=LoginResponse)
async def login(login_data: UserLogin):
    # Buscar usuário por email
    user = await db.users.find_one({"email": login_data.email, "ativo": True})
    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    # Verificar senha
    if not verify_password(login_data.senha, user["senha_hash"]):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    # Gerar token simples (você deveria usar JWT em produção)
    token = str(uuid.uuid4())
    
    # Salvar sessão (simples)
    await db.sessions.insert_one({
        "token": token,
        "user_id": user["id"],
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
    })
    
    return LoginResponse(
        user_id=user["id"],
        nome=user["nome"],
        email=user["email"],
        tipo=user["tipo"],
        turmas_permitidas=user["turmas_permitidas"],
        token=token
    )

@api_router.post("/logout")
async def logout(token: str):
    await db.sessions.delete_one({"token": token})
    return {"message": "Logout realizado com sucesso"}

@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    # Verificar se email já existe
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email já está em uso")
    
    user_dict = user.dict()
    user_dict["senha_hash"] = hash_password(user_dict.pop("senha"))
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find({"ativo": True}).to_list(1000)
    return [User(**user) for user in users]

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await db.users.update_one(
        {"id": user_id}, 
        {"$set": {"ativo": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário removido com sucesso"}

# Middleware para verificar acesso
async def verify_access(token: str, turma_id: str = None):
    # Verificar sessão
    session = await db.sessions.find_one({"token": token})
    if not session:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    # Verificar se não expirou
    expires_at = datetime.fromisoformat(session["expires_at"])
    if datetime.utcnow() > expires_at:
        await db.sessions.delete_one({"token": token})
        raise HTTPException(status_code=401, detail="Sessão expirada")
    
    # Buscar usuário
    user = await db.users.find_one({"id": session["user_id"], "ativo": True})
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    
    # Verificar acesso à turma (se especificada)
    if turma_id and user["tipo"] == "professor":
        if turma_id not in user["turmas_permitidas"]:
            raise HTTPException(status_code=403, detail="Acesso negado a esta turma")
    
    return user

# Endpoint para verificar acesso
@api_router.get("/verify-access")
async def check_access(token: str, turma_id: str = None):
    user = await verify_access(token, turma_id)
    return {
        "user_id": user["id"],
        "nome": user["nome"],
        "tipo": user["tipo"],
        "turmas_permitidas": user["turmas_permitidas"]
    }
# Endpoint para criar usuário admin inicial
@api_router.post("/init-admin")
async def create_initial_admin():
    """Criar usuário administrador inicial - só funciona se não houver nenhum admin"""
    try:
        # Verificar se já existe admin
        existing_admin = await db.users.find_one({"tipo": "admin", "ativo": True})
        if existing_admin:
            raise HTTPException(status_code=400, detail="Já existe um administrador no sistema")
        
        # Criar admin padrão
        admin_data = {
            "id": str(uuid.uuid4()),
            "nome": "Márcio Ferreira",
            "email": "admin@ebd.com",
            "senha_hash": hash_password("123456"),  # Senha padrão
            "tipo": "admin",
            "turmas_permitidas": [],  # Admin tem acesso a todas
            "ativo": True,
            "criado_em": datetime.utcnow().isoformat()
        }
        
        await db.users.insert_one(admin_data)
        
        return {
            "message": "Administrador criado com sucesso",
            "email": "admin@ebd.com",
            "senha": "123456",
            "nome": "Márcio Ferreira"
        }
        
    except Exception as e:
        if "Já existe um administrador" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Erro ao criar administrador: {str(e)}")

@api_router.post("/init-church-data")
async def init_church_data():
    """Limpar dados existentes e criar dados reais da igreja"""
    try:
        # Limpar dados existentes
        await db.turmas.delete_many({})
        await db.students.delete_many({})
        await db.attendance.delete_many({})
        
        # Definir turmas e alunos conforme fornecido
        turmas_data = [
            {
                "nome": "Professores e Oficiais",
                "descricao": "Professores e Oficiais da Igreja",
                "alunos": [
                    "Pr. Henrique", "Pb Paulo", "Pb Elias", "Coop Carlos", "Coop Elias Filho", "Coop Jailton", 
                    "Coop Santiago", "Irmã Dorcas", "Irmã Ester Carvalho", "Irmã Marry", "Irmã Renata", "Irmã Rosa", 
                    "Irmão Rubens", "Izabelle", "Juliana Silva", "Kesia Ferreira", "Márcio Ferreira", "Pb Sebastião", 
                    "Tia Ana Paula", "Tia Deise", "Tia Eliane", "Tia Evelyn", "Tia Flávia André", "Tia Kelly", 
                    "Tia Lu", "Tia Natália", "Tia Riane", "Tio Italo", "Pb Carlinhos", "Sidney Custodio", 
                    "Juliane Reis", "Vitória Ferreira"
                ]
            },
            {
                "nome": "Genesis",
                "descricao": "Turma Genesis",
                "alunos": [
                    "Agatha Mirella Souza Martins", "Arthur Galvão Costa da Silva", "Benjamim Henrique de Carvalho André", 
                    "Helena Marques Dantas", "Lara Heloíse Santos de Jesus", "Luiza Oliveira Reis", "Manuela de Azevedo Santos", 
                    "Otton Gomes Santos Albuquerque", "Ayla Sophia Souza Martins", "Isadora de Oliveira Santos Alves", 
                    "Leandro Pedro de Lima", "Mariana Rodrigues Augusto", "Miguel Silva dos Santos"
                ]
            },
            {
                "nome": "Primarios",
                "descricao": "Turma dos Primários",
                "alunos": [
                    "Ana Beatriz Oliveira dos Santos", "Débora Nicole Galvão Costa da Silva", "Heloisa Santana de Moura", 
                    "Melissa de Azevedo Santos", "Heloisa Fernandes Carvalho", "Davi Henrique de Carvalho André", 
                    "Kaleb Henrique Gabriel Tavares", "Andre Felipe de Souza Viana", "Maria Ísis", "Raissa Reis Conti", 
                    "Lorenzo Gomes Pedro Tavares", "Isaac de Oliveira Santos Alves", "Lívia Santos Silva", 
                    "Laura Caroline Rodrigues", "Vítor Pedro de Lima", "Heitor Brito"
                ]
            },
            {
                "nome": "Juniores",
                "descricao": "Turma dos Juniores",
                "alunos": [
                    "Beatriz Pedro de Lima", "Davi Afonso Lana", "Enzo Leonardo Bitencourt Souza", 
                    "Felype Augusto Oliveira de Jesus", "Gustavo Lorenzo Ferreira", "Mariana Lima de Sousa", 
                    "Isabelle Sophia Da Costa De Almeida", "Luíza (Suellen Tayrone)", "Hadassah Victoria Gabriel Tavares", 
                    "Davi Caldeira Rodrigues", "Ana Luiza Santana de Moura", "Kemuel Brito"
                ]
            },
            {
                "nome": "Pré-Adolescentes",
                "descricao": "Turma dos Pré-Adolescentes",
                "alunos": [
                    "Enzo Gabriel Guimarães Fernandes", "Lorena Gomes Pedro Tavares", "Maria Luiza Sousa Brito", 
                    "Guilherme Santos Almeida", "Rebeca (filha do Rodrigo)", "Eduardo", "Anthony Isaac Santos de Jesus", 
                    "Ellen Beatrice Caldeira Rodrigues", "Manoela Oliveira Reis", "Miguel Paulo dos Santos", 
                    "Gabriel Santos Almeida"
                ]
            },
            {
                "nome": "Adolescentes",
                "descricao": "Turma dos Adolescentes",
                "alunos": [
                    "Any", "Daniel", "Jhenifer", "Jhonwesley", "Josué", "Karol", "Kauã", "Naely", "Isa", "Paulo", 
                    "Sofhia", "Victor Hugo", "Vitor Gabriel", "Vitória Ferreira", "Walacy", "Yasmin", "Ana Flávia", 
                    "Gabriela", "Arthur", "Jamilly Costa"
                ]
            },
            {
                "nome": "Jovens",
                "descricao": "Turma dos Jovens",
                "alunos": [
                    "Abmael", "Almir", "Ana", "Emanuel", "Gustavo", "Ingrid", "Janecelia", "Jhenniffer", "Júlio", 
                    "Kessia", "Misma", "Natalia Silva", "Solange", "Vitória Soares", "Yan", "Abner", "Dannilo Duany", 
                    "Lucas Brito", "Ana Carolina", "Danilo", "Matheus Assis", "Ademir Junior", "Pedro"
                ]
            },
            {
                "nome": "Dorcas (irmãs)",
                "descricao": "Turma das Irmãs Dorcas",
                "alunos": [
                    "Ana Aleixo", "Angelica", "Bruna", "Carla", "Carla Santana", "Claudia", "Cristiane Gomes", 
                    "Daiane Balleiro", "Denise Rodrigues", "Dirce dos Santos", "Eliane Cardoso", "Eliene Viana", 
                    "Érica", "Ester Ferreira", "Eula", "Evanilda", "Geni", "Geovan Silva", "Geovanna Tavares", 
                    "Gildete Dias dos Santos", "Graciete", "Graucia Campos", "Iraci", "Jô", "Jovina", "Jucileide", 
                    "Kennye", "Lenilde", "Lilian", "Lourdes Oliveira", "Maria", "Maria de Loudes Ayala", 
                    "Maria Helna Lourenço", "Marli de Paula", "Maya", "Nalva", "Neuza Guimarães", "Nilza Arcanjo", 
                    "Raimunda da Conceição", "Rosenilda", "Rute Morete", "Sandra Assis", "Sara Ribeiro", "Sarah Reis", 
                    "Simone Tavares", "Sandra Magalhães", "Tania", "Valdirene", "Vera Lucia Aparecida", "Vera Ricardo", 
                    "Laudiceia", "Rosana", "Augusta", "Deise Farias", "Mirian Menezes", "Regiane", "Danieli", 
                    "Gleyse", "Lucilene", "Tia Kesia", "Leicida", "Márcia Regina"
                ]
            },
            {
                "nome": "Ebenezer (Obreiros)",
                "descricao": "Turma dos Obreiros Ebenezer",
                "alunos": [
                    "Coop Antônio", "Coop Denys", "Coop Elias Barbosa", "Coop Emanuel", "Coop Evandro", 
                    "Coop Francisco", "Coop João Gregório", "Coop Roberto Dantas", "Coop Valdeci", "Diac Emílio", 
                    "Diac Luiz Borges", "Diac Marcos", "Pb Almir", "Pb Bernardo", "Pb Cosmo", "Pb Geovane", 
                    "Pb Ismael", "Pb Thiago Tavares", "Coop Walmir", "Coop Alessandro", "Pb Isaac", "Coop Edson"
                ]
            },
            {
                "nome": "Soldados de Cristo",
                "descricao": "Turma dos Soldados de Cristo",
                "alunos": [
                    "Alexandre Tavares", "Amilton", "André Afonso Lana", "Daniel Corsine", "Elias Barbosa", 
                    "Elizeu Barbosa", "Gerônimo", "Isaias Abreu", "Jair Benedito", "Jesiel José", "Jessé Araújo", 
                    "Joedilson", "Joel Cruz", "José Arcanjo", "José Domingos", "Luiz Felipe", "Manoel Lopes", 
                    "Messias Rodrigues", "Nylon", "Ronaldo Rabelo", "Tiago Henrique", "Fernando Paulo", "Gideão", 
                    "Djalma", "José Maria", "Willian Medeiros Alves", "Diego Augusto", "Reginaldo", "Daniel José", 
                    "Daniel Mousinho de Araújo", "Gabriel Lana"
                ]
            },
            {
                "nome": "Discipulados",
                "descricao": "Turma de Discipulados",
                "alunos": []
            }
        ]
        
        total_turmas = 0
        total_alunos = 0
        
        # Criar turmas e alunos
        for turma_data in turmas_data:
            # Criar turma
            turma_id = str(uuid.uuid4())
            turma = {
                "id": turma_id,
                "nome": turma_data["nome"],
                "descricao": turma_data["descricao"],
                "ativa": True,
                "criada_em": datetime.utcnow().isoformat()
            }
            await db.turmas.insert_one(turma)
            total_turmas += 1
            
            # Criar alunos da turma
            for nome_aluno in turma_data["alunos"]:
                aluno = {
                    "id": str(uuid.uuid4()),
                    "nome_completo": nome_aluno,
                    "data_nascimento": "2000-01-01",  # Data padrão, pode ser ajustada depois
                    "contato": "",  # Vazio por enquanto
                    "turma_id": turma_id,
                    "ativo": True,
                    "criado_em": datetime.utcnow().isoformat()
                }
                await db.students.insert_one(aluno)
                total_alunos += 1
        
        return {
            "message": "Dados da igreja criados com sucesso",
            "turmas": total_turmas,
            "alunos": total_alunos,
            "detalhes": {turma_data["nome"]: len(turma_data["alunos"]) for turma_data in turmas_data}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar dados da igreja: {str(e)}")
    """Criar dados de exemplo de chamada com ofertas para demonstrar relatórios"""
    try:
        # Buscar turmas e alunos
        turmas = await db.turmas.find({"ativa": True}).to_list(10)
        students = await db.students.find({"ativo": True}).to_list(10)
        
        if not turmas or not students:
            raise HTTPException(status_code=404, detail="Turmas ou alunos não encontrados. Execute init-sample-data primeiro.")
        
        # Data de exemplo (domingo)
        sample_date = "2025-07-13"
        
        # Limpar dados de attendance da data
        await db.attendance.delete_many({"data": sample_date})
        
        # Criar presenças de exemplo com ofertas variadas
        sample_attendance = []
        
        for turma in turmas:
            turma_students = [s for s in students if s["turma_id"] == turma["id"]]
            
            for i, student in enumerate(turma_students):
                # Variar as ofertas por turma para criar vencedores claros
                oferta_base = 10.0
                if turma["nome"] == "Gênesis":
                    oferta_base = 50.0  # Adultos doam mais
                elif turma["nome"] == "Juvenil":
                    oferta_base = 25.0  # Jovens doam valor médio
                elif turma["nome"] == "Primários":
                    oferta_base = 5.0   # Crianças doam menos
                
                attendance_record = {
                    "id": str(uuid.uuid4()),
                    "aluno_id": student["id"],
                    "turma_id": turma["id"],
                    "data": sample_date,
                    "status": "presente" if i % 2 == 0 else "presente",  # Maioria presente para ter boa frequência
                    "oferta": oferta_base + (i * 5.0),  # Variar ofertas
                    "biblias_entregues": 1 if i == 0 else 0,
                    "revistas_entregues": 1,
                    "criado_em": datetime.utcnow().isoformat()
                }
                sample_attendance.append(attendance_record)
        
        if sample_attendance:
            await db.attendance.insert_many(sample_attendance)
        
        return {
            "message": f"Dados de exemplo criados para {len(sample_attendance)} registros de presença",
            "data": sample_date,
            "registros": len(sample_attendance)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar dados de exemplo: {str(e)}")

# Ranking de Alunos
@api_router.get("/ranking/alunos")
async def get_alunos_ranking():
    """Retorna ranking de alunos por presença"""
    try:
        # Buscar todos os registros de presença
        attendance_records = await db.attendance.find({"status": "presente"}).to_list(10000)
        
        # Contar presenças por aluno
        aluno_presencas = {}
        for record in attendance_records:
            aluno_id = record["aluno_id"]
            if aluno_id not in aluno_presencas:
                aluno_presencas[aluno_id] = 0
            aluno_presencas[aluno_id] += 1
        
        # Buscar informações dos alunos
        students = await db.students.find({"ativo": True}).to_list(1000)
        student_dict = {s["id"]: s for s in students}
        
        # Buscar informações das turmas
        turmas = await db.turmas.find({"ativa": True}).to_list(100)
        turma_dict = {t["id"]: t for t in turmas}
        
        # Criar ranking
        ranking = []
        for aluno_id, presencas in aluno_presencas.items():
            if aluno_id in student_dict:
                student = student_dict[aluno_id]
                turma = turma_dict.get(student["turma_id"], {})
                
                ranking.append({
                    "posicao": 0,  # Will be set after sorting
                    "aluno_id": aluno_id,
                    "nome": student["nome_completo"],
                    "turma": turma.get("nome", "Turma não encontrada"),
                    "turma_id": student["turma_id"],
                    "total_presencas": presencas,
                    "domingos_presentes": presencas  # Cada registro é um domingo
                })
        
        # Ordenar por total de presenças (decrescente)
        ranking.sort(key=lambda x: x["total_presencas"], reverse=True)
        
        # Definir posições
        for i, item in enumerate(ranking):
            item["posicao"] = i + 1
        
        return {
            "message": "Ranking de alunos por presença",
            "total_alunos": len(ranking),
            "ranking": ranking[:50]  # Top 50
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ranking: {str(e)}")

@api_router.get("/ranking/professores-oficiais")
async def get_professores_oficiais_ranking():
    """Retorna ranking específico da turma Professores e Oficiais"""
    try:
        # Buscar turma Professores e Oficiais
        turma_prof = await db.turmas.find_one({"nome": "Professores e Oficiais", "ativa": True})
        if not turma_prof:
            raise HTTPException(status_code=404, detail="Turma Professores e Oficiais não encontrada")
        
        # Buscar alunos da turma
        students = await db.students.find({"turma_id": turma_prof["id"], "ativo": True}).to_list(100)
        
        # Buscar presenças dos alunos desta turma
        alunos_ids = [s["id"] for s in students]
        attendance_records = await db.attendance.find({
            "aluno_id": {"$in": alunos_ids},
            "status": "presente"
        }).to_list(10000)
        
        # Contar presenças por aluno
        aluno_presencas = {}
        for record in attendance_records:
            aluno_id = record["aluno_id"]
            if aluno_id not in aluno_presencas:
                aluno_presencas[aluno_id] = 0
            aluno_presencas[aluno_id] += 1
        
        # Criar ranking
        ranking = []
        for student in students:
            presencas = aluno_presencas.get(student["id"], 0)
            ranking.append({
                "posicao": 0,  # Will be set after sorting
                "aluno_id": student["id"],
                "nome": student["nome_completo"],
                "total_presencas": presencas,
                "domingos_presentes": presencas,
                "turma": "Professores e Oficiais"
            })
        
        # Ordenar por total de presenças (decrescente)
        ranking.sort(key=lambda x: x["total_presencas"], reverse=True)
        
        # Definir posições
        for i, item in enumerate(ranking):
            item["posicao"] = i + 1
        
        return {
            "message": "Ranking da turma Professores e Oficiais",
            "turma_nome": "Professores e Oficiais",
            "total_membros": len(ranking),
            "ranking": ranking
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ranking de professores: {str(e)}")

@api_router.get("/ranking/turmas")
async def get_turmas_ranking():
    """Retorna ranking de turmas por frequência média"""
    try:
        # Buscar dados do dashboard (que já calcula as estatísticas)
        dashboard_data = []
        
        # Buscar todas as turmas
        turmas = await db.turmas.find({"ativa": True}).to_list(100)
        
        for turma in turmas:
            # Buscar alunos matriculados
            matriculados = await db.students.count_documents({"turma_id": turma["id"], "ativo": True})
            
            # Buscar presenças da turma
            attendance_records = await db.attendance.find({
                "turma_id": turma["id"],
                "status": "presente"
            }).to_list(10000)
            
            # Contar domingos únicos com presença
            domingos_com_presenca = set()
            for record in attendance_records:
                domingos_com_presenca.add(record["data"])
            
            # Calcular frequência média
            total_presencas = len(attendance_records)
            total_domingos = len(domingos_com_presenca) if domingos_com_presenca else 1
            media_presencas = total_presencas / total_domingos if total_domingos > 0 else 0
            percentual_frequencia = (media_presencas / matriculados * 100) if matriculados > 0 else 0
            
            dashboard_data.append({
                "turma_id": turma["id"],
                "turma_nome": turma["nome"],
                "matriculados": matriculados,
                "media_presencas": round(media_presencas, 1),
                "percentual_frequencia": round(percentual_frequencia, 1),
                "total_presencas": total_presencas,
                "domingos_ativos": total_domingos
            })
        
        # Ordenar por percentual de frequência (decrescente)
        dashboard_data.sort(key=lambda x: x["percentual_frequencia"], reverse=True)
        
        # Definir posições
        for i, item in enumerate(dashboard_data):
            item["posicao"] = i + 1
        
        return {
            "message": "Ranking de turmas por frequência",
            "total_turmas": len(dashboard_data),
            "ranking": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ranking de turmas: {str(e)}")

# Routes - Revistas
@api_router.get("/revistas")
async def get_revistas():
    """Buscar todas as revistas ativas"""
    try:
        revistas_cursor = db.revistas.find({"ativa": True})
        revistas = []
        
        async for revista in revistas_cursor:
            # Remove _id do MongoDB e converte para formato JSON serializable
            revista_clean = {
                "id": revista.get("id"),
                "tema": revista.get("tema"),
                "licoes": revista.get("licoes", []),
                "turma_ids": revista.get("turma_ids", []),
                "ativa": revista.get("ativa", True),
                "criada_em": revista.get("criada_em")
            }
            revistas.append(revista_clean)
        
        return revistas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar revistas: {str(e)}")

@api_router.get("/revistas/turma/{turma_id}")
async def get_revista_by_turma(turma_id: str):
    """Buscar revista de uma turma específica"""
    try:
        revista = await db.revistas.find_one({"turma_ids": turma_id, "ativa": True})
        if not revista:
            return {"tema": None, "licoes": []}
        
        # Remove _id do MongoDB e converte para formato JSON serializable
        revista_clean = {
            "id": revista.get("id"),
            "tema": revista.get("tema"),
            "licoes": revista.get("licoes", []),
            "turma_ids": revista.get("turma_ids", []),
            "ativa": revista.get("ativa", True),
            "criada_em": revista.get("criada_em")
        }
        return revista_clean
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar revista da turma: {str(e)}")

@api_router.post("/revistas")
async def create_revista(revista: RevistaCreate):
    """Criar nova revista"""
    try:
        revista_data = {
            "id": str(uuid.uuid4()),
            "tema": revista.tema,
            "licoes": [licao.dict() for licao in revista.licoes],
            "turma_ids": revista.turma_ids,
            "ativa": True,
            "criada_em": datetime.utcnow().isoformat()
        }
        
        result = await db.revistas.insert_one(revista_data)
        revista_data["_id"] = str(result.inserted_id)
        return {"message": "Revista criada com sucesso", "revista": revista_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar revista: {str(e)}")

@api_router.put("/revistas/{revista_id}")
async def update_revista(revista_id: str, revista: RevistaCreate):
    """Atualizar revista existente"""
    try:
        revista_data = {
            "tema": revista.tema,
            "licoes": [licao.dict() for licao in revista.licoes],
            "turma_ids": revista.turma_ids,
        }
        
        result = await db.revistas.update_one(
            {"id": revista_id},
            {"$set": revista_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Revista não encontrada")
        
        return {"message": "Revista atualizada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar revista: {str(e)}")

@api_router.delete("/revistas/{revista_id}")
async def delete_revista(revista_id: str):
    """Desativar revista"""
    try:
        result = await db.revistas.update_one(
            {"id": revista_id},
            {"$set": {"ativa": False}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Revista não encontrada")
        
        return {"message": "Revista desativada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao desativar revista: {str(e)}")

# Endpoint para inicializar revista de adultos
@api_router.post("/init-revista-adultos")
async def init_revista_adultos():
    """Inicializar dados da revista de adultos para as turmas especificadas"""
    try:
        # Buscar IDs das turmas de adultos
        turmas_adultos = ["Professores e Oficiais", "Ebenezer (Obreiros)", "Dorcas (irmãs)", "Soldados de Cristo"]
        
        turmas = await db.turmas.find({"nome": {"$in": turmas_adultos}, "ativa": True}).to_list(10)
        turma_ids = [turma["id"] for turma in turmas]
        
        if not turma_ids:
            raise HTTPException(status_code=404, detail="Turmas de adultos não encontradas")
        
        # Verificar se já existe uma revista para essas turmas
        revista_existente = await db.revistas.find_one({"turma_ids": {"$in": turma_ids}, "ativa": True})
        if revista_existente:
            return {"message": "Revista de adultos já existe", "revista_id": revista_existente.get("id", "")}
        
        # Dados da revista de adultos
        revista_adultos = {
            "id": str(uuid.uuid4()),
            "tema": "A Igreja em Jerusalém — Doutrina, Comunhão e Fé: a base para o crescimento da Igreja em meio às perseguições",
            "licoes": [
                {"titulo": "A Igreja que nasceu no Pentecostes", "data": "2025-07-06"},
                {"titulo": "A Igreja de Jerusalém: um modelo a ser seguido", "data": "2025-07-13"},
                {"titulo": "Uma Igreja fiel à pregação do Evangelho", "data": "2025-07-20"},
                {"titulo": "Uma Igreja cheia do Espírito Santo", "data": "2025-07-27"},
                {"titulo": "Uma Igreja cheia de amor", "data": "2025-08-03"},
                {"titulo": "Uma Igreja não conivente com a mentira", "data": "2025-08-10"},
                {"titulo": "Uma Igreja que não teme a perseguição", "data": "2025-08-17"},
                {"titulo": "Uma Igreja que enfrenta os seus problemas", "data": "2025-08-24"},
                {"titulo": "Uma Igreja que se arrisca", "data": "2025-08-31"},
                {"titulo": "A expansão da Igreja", "data": "2025-09-07"},
                {"titulo": "Uma igreja hebreia na casa de um estrangeiro", "data": "2025-09-14"},
                {"titulo": "O caráter missionário da Igreja de Jerusalém", "data": "2025-09-21"},
                {"titulo": "Assembleia de Jerusalém", "data": "2025-09-28"}
            ],
            "turma_ids": turma_ids,
            "ativa": True,
            "criada_em": datetime.utcnow().isoformat()
        }
        
        await db.revistas.insert_one(revista_adultos)
        
        return {
            "message": "Revista de adultos criada com sucesso",
            "turmas_atendidas": [turma["nome"] for turma in turmas],
            "total_licoes": len(revista_adultos["licoes"]),
            "tema": revista_adultos["tema"],
            "revista_id": revista_adultos["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar revista de adultos: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()