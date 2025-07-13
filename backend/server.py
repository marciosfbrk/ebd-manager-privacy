from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
from enum import Enum
import json

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
    data_nascimento: date
    contato: str
    turma_id: str
    ativo: bool = True
    criado_em: datetime = Field(default_factory=datetime.utcnow)

class StudentCreate(BaseModel):
    nome_completo: str
    data_nascimento: date
    contato: str
    turma_id: str

class StudentUpdate(BaseModel):
    nome_completo: Optional[str] = None
    data_nascimento: Optional[date] = None
    contato: Optional[str] = None
    turma_id: Optional[str] = None

class Turma(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    descricao: Optional[str] = None
    ativa: bool = True
    criada_em: datetime = Field(default_factory=datetime.utcnow)

class TurmaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None

class Attendance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aluno_id: str
    turma_id: str
    data: date
    status: AttendanceStatus
    oferta: Optional[float] = 0.0
    biblias_entregues: Optional[int] = 0
    revistas_entregues: Optional[int] = 0
    criado_em: datetime = Field(default_factory=datetime.utcnow)

class AttendanceCreate(BaseModel):
    aluno_id: str
    turma_id: str
    data: date
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
    data: date
    matriculados: int
    presentes: int
    ausentes: int
    visitantes: int
    pos_chamada: int
    total_ofertas: float
    total_biblias: int
    total_revistas: int

# Helper functions
def is_sunday(date_obj: date) -> bool:
    return date_obj.weekday() == 6  # Sunday is 6

def serialize_date(obj):
    """Convert date objects to string for MongoDB storage"""
    if isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def prepare_for_mongo(data):
    """Prepare data for MongoDB insertion by converting dates to strings"""
    if isinstance(data, dict):
        return {k: serialize_date(v) for k, v in data.items()}
    return data

# Routes - Turmas
@api_router.post("/turmas", response_model=Turma)
async def create_turma(turma: TurmaCreate):
    turma_dict = turma.dict()
    turma_obj = Turma(**turma_dict)
    await db.turmas.insert_one(prepare_for_mongo(turma_obj.dict()))
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
    await db.students.insert_one(prepare_for_mongo(student_obj.dict()))
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
async def transfer_student(student_id: str, nova_turma_id: str):
    # Verificar se o aluno existe
    student = await db.students.find_one({"id": student_id, "ativo": True})
    if not student:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Verificar se a nova turma existe
    turma = await db.turmas.find_one({"id": nova_turma_id, "ativa": True})
    if not turma:
        raise HTTPException(status_code=404, detail="Nova turma não encontrada")
    
    # Atualizar turma do aluno
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"turma_id": nova_turma_id}}
    )
    
    return {"message": "Aluno transferido com sucesso"}

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
        "data": attendance.data.isoformat()
    })
    if existing:
        raise HTTPException(status_code=400, detail="Chamada já existe para este aluno nesta data")
    
    attendance_dict = attendance.dict()
    attendance_obj = Attendance(**attendance_dict)
    await db.attendance.insert_one(prepare_for_mongo(attendance_obj.dict()))
    return attendance_obj

@api_router.get("/attendance", response_model=List[Attendance])
async def get_attendance(turma_id: Optional[str] = None, data: Optional[date] = None):
    filter_dict = {}
    if turma_id:
        filter_dict["turma_id"] = turma_id
    if data:
        filter_dict["data"] = data.isoformat()
    
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
async def get_dashboard_report(data: Optional[date] = None):
    if not data:
        data = datetime.now().date()
    
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
            "data": data.isoformat()
        }).to_list(1000)
        
        # Calcular estatísticas
        presentes = len([a for a in attendance_records if a["status"] == "presente"])
        visitantes = len([a for a in attendance_records if a["status"] == "visitante"])
        pos_chamada = len([a for a in attendance_records if a["status"] == "pos_chamada"])
        ausentes = matriculados - presentes
        
        total_ofertas = sum(a.get("oferta", 0) for a in attendance_records)
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
async def bulk_attendance(turma_id: str, data: date, attendance_list: List[AttendanceCreate]):
    # Verificar se é domingo
    if not is_sunday(data):
        raise HTTPException(status_code=400, detail="Chamada só pode ser feita aos domingos")
    
    # Verificar se a turma existe
    turma = await db.turmas.find_one({"id": turma_id, "ativa": True})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # Remover registros existentes da data
    await db.attendance.delete_many({"turma_id": turma_id, "data": data.isoformat()})
    
    # Inserir novos registros
    attendance_objects = []
    for att_data in attendance_list:
        att_dict = att_data.dict()
        att_dict["data"] = data.isoformat()
        att_dict["turma_id"] = turma_id
        attendance_obj = Attendance(**att_dict)
        attendance_objects.append(prepare_for_mongo(attendance_obj.dict()))
    
    if attendance_objects:
        await db.attendance.insert_many(attendance_objects)
    
    return {"message": f"Chamada salva com sucesso para {len(attendance_objects)} registros"}

# Initialize sample data
@api_router.post("/init-sample-data")
async def init_sample_data():
    # Limpar dados existentes
    await db.turmas.delete_many({})
    await db.students.delete_many({})
    await db.attendance.delete_many({})
    
    # Criar turmas de exemplo
    turmas = [
        {"id": str(uuid.uuid4()), "nome": "Gênesis", "descricao": "Turma dos adultos", "ativa": True, "criada_em": datetime.utcnow()},
        {"id": str(uuid.uuid4()), "nome": "Primários", "descricao": "Turma das crianças", "ativa": True, "criada_em": datetime.utcnow()},
        {"id": str(uuid.uuid4()), "nome": "Juvenil", "descricao": "Turma dos jovens", "ativa": True, "criada_em": datetime.utcnow()}
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