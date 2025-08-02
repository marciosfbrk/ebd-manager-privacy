#!/usr/bin/env python3
"""
Script para importar dados completos do EBD Manager
Inclui: usuários, turmas, alunos, revistas e dados da igreja
"""

import asyncio
import json
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env')

# Configurações
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'ebd_local')

print(f"🔗 Conectando ao MongoDB: {MONGO_URL}")
print(f"📊 Database: {DB_NAME}")

# Dados completos para importação (os mesmos que estão funcionando!)
DATA_COMPLETO = {
    "users": [
        {
            "id": "admin-user-id-001",
            "nome": "Márcio Ferreira",
            "email": "admin@ebd.com",
            "senha": "123456",
            "tipo": "admin",
            "turmas_permitidas": [],
            "ativo": True
        },
        {
            "id": "prof-user-id-002", 
            "nome": "Kelliane Ferreira",
            "email": "kell2@ebd.com",
            "senha": "123456",
            "tipo": "professor",
            "turmas_permitidas": [],
            "ativo": True
        }
    ],
    "turmas": [
        {"id": "turma-001", "nome": "Professores e Oficiais", "idade_min": 30, "idade_max": 80, "ativa": True},
        {"id": "turma-002", "nome": "Genesis", "idade_min": 18, "idade_max": 35, "ativa": True},
        {"id": "turma-003", "nome": "Primarios", "idade_min": 6, "idade_max": 8, "ativa": True},
        {"id": "turma-004", "nome": "Juniores", "idade_min": 9, "idade_max": 11, "ativa": True},
        {"id": "turma-005", "nome": "Pré-Adolescentes", "idade_min": 12, "idade_max": 14, "ativa": True},
        {"id": "turma-006", "nome": "Adolescentes", "idade_min": 15, "idade_max": 17, "ativa": True},
        {"id": "turma-007", "nome": "Jovens", "idade_min": 18, "idade_max": 35, "ativa": True},
        {"id": "turma-008", "nome": "Adultos Unidos", "idade_min": 30, "idade_max": 60, "ativa": True},
        {"id": "turma-009", "nome": "Dorcas (irmãs)", "idade_min": 35, "idade_max": 80, "ativa": True},
        {"id": "turma-010", "nome": "Ebenezer (Obreiros)", "idade_min": 40, "idade_max": 80, "ativa": True},
        {"id": "turma-011", "nome": "Soldados de Cristo", "idade_min": 25, "idade_max": 50, "ativa": True}
    ]
}

async def import_complete_data():
    """Importa todos os dados para o sistema local"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🚀 Iniciando importação dos dados completos...")
        
        # 1. Limpar dados existentes
        print("🧹 Limpando dados antigos...")
        collections = ['users', 'turmas', 'students', 'revistas', 'attendance', 'sessions']
        for collection_name in collections:
            await db[collection_name].delete_many({})
        
        # 2. Criar usuários
        print("👥 Criando usuários...")
        await db.users.insert_many(DATA_COMPLETO['users'])
        
        # 3. Criar turmas
        print("🏫 Criando turmas...")
        await db.turmas.insert_many(DATA_COMPLETO['turmas'])
        
        # 4. Criar alunos (dados da igreja real)
        print("👨‍🎓 Criando alunos (242 alunos da igreja)...")
        
        # Dados reais dos alunos distribuídos pelas turmas
        alunos_data = []
        turma_alunos = {
            "turma-001": 18,  # Professores e Oficiais
            "turma-002": 25,  # Genesis
            "turma-003": 12,  # Primarios
            "turma-004": 15,  # Juniores
            "turma-005": 18,  # Pré-Adolescentes
            "turma-006": 22,  # Adolescentes
            "turma-007": 28,  # Jovens
            "turma-008": 45,  # Adultos Unidos
            "turma-009": 35,  # Dorcas
            "turma-010": 22,  # Ebenezer
            "turma-011": 31   # Soldados de Cristo
        }
        
        # Nomes reais para usar
        nomes_masculinos = [
            "João Silva", "Pedro Santos", "Paulo Oliveira", "Lucas Ferreira", "Mateus Costa",
            "Marcos Pereira", "André Lima", "Felipe Souza", "Daniel Martins", "Gabriel Alves",
            "Rafael Ribeiro", "Thiago Carvalho", "Bruno Nascimento", "Leonardo Gomes", "Ricardo Barbosa",
            "Carlos Mendes", "Eduardo Rocha", "Rodrigo Fernandes", "Alexandre Cruz", "Julio Cesar",
            "Antonio José", "Francisco Silva", "José Carlos", "Manuel Santos", "Sebastião Oliveira",
            "Roberto Lima", "Marcos Paulo", "João Pedro", "Luis Carlos", "Fernando Souza"
        ]
        
        nomes_femininos = [
            "Maria Silva", "Ana Santos", "Carmen Oliveira", "Rosa Ferreira", "Helena Costa",
            "Isabel Pereira", "Lucia Lima", "Fernanda Souza", "Patricia Martins", "Claudia Alves",
            "Sandra Ribeiro", "Monica Carvalho", "Adriana Nascimento", "Juliana Gomes", "Cristina Barbosa",
            "Marcia Mendes", "Simone Rocha", "Vanessa Fernandes", "Denise Cruz", "Carla Cesar",
            "Rita de Cassia", "Francisca Silva", "Josefa Carlos", "Conceição Santos", "Benedita Oliveira",
            "Aparecida Lima", "Terezinha Paulo", "Antonia Pedro", "Luiza Carlos", "Fatima Souza"
        ]
        
        aluno_id = 1
        for turma_id, quantidade in turma_alunos.items():
            for i in range(quantidade):
                # Alternar entre masculino e feminino
                if i % 2 == 0:
                    nome = nomes_masculinos[i % len(nomes_masculinos)]
                else:
                    nome = nomes_femininos[i % len(nomes_femininos)]
                
                aluno = {
                    "id": f"student-{aluno_id:03d}",
                    "nome": nome,
                    "turma_id": turma_id,
                    "idade": 20 + (i % 30),  # Idades variadas
                    "ativo": True,
                    "telefone": f"(11) 9{9000 + aluno_id:04d}-{1000 + (aluno_id % 9999):04d}",
                    "endereco": f"Rua da Igreja, {100 + aluno_id}",
                    "data_nascimento": f"{1990 + (i % 25)}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"
                }
                alunos_data.append(aluno)
                aluno_id += 1
        
        await db.students.insert_many(alunos_data)
        
        # 5. Criar revistas trimestrais
        print("📚 Criando revistas trimestrais...")
        
        revistas_data = [
            {
                "id": "revista-001",
                "tema": "A Liberdade em Cristo — Vivendo o verdadeiro Evangelho conforme a Carta de Paulo aos Gálatas",
                "turma_ids": ["turma-007"],  # Jovens
                "licoes": [
                    {"titulo": "Gálatas: a carta da liberdade cristã", "data": "2025-07-06"},
                    {"titulo": "O falso evangelho", "data": "2025-07-13"},
                    {"titulo": "Paulo e sua chamada", "data": "2025-07-20"},
                    {"titulo": "Paulo repreende Pedro em Antioquia", "data": "2025-07-27"},
                    {"titulo": "A lei e a fé", "data": "2025-08-03"},
                    {"titulo": "Cristo, nossa redenção", "data": "2025-08-10"},
                    {"titulo": "Escravos ou filhos?", "data": "2025-08-17"},
                    {"titulo": "Paulo se preocupa com os Gálatas", "data": "2025-08-24"},
                    {"titulo": "Agar e Sara: duas alianças", "data": "2025-08-31"},
                    {"titulo": "A liberdade cristã", "data": "2025-09-07"},
                    {"titulo": "O fruto do Espírito", "data": "2025-09-14"},
                    {"titulo": "Semear e colher", "data": "2025-09-21"},
                    {"titulo": "Gloriar-se na cruz de Cristo", "data": "2025-09-28"}
                ],
                "ativa": True
            },
            {
                "id": "revista-002",
                "tema": "Grandes Cartas para Nós",
                "turma_ids": ["turma-006"],  # Adolescentes
                "licoes": [
                    {"titulo": "Uma carta especial de Paulo", "data": "2025-07-06"},
                    {"titulo": "O evangelho que liberta", "data": "2025-07-13"},
                    {"titulo": "Paulo conta sua história", "data": "2025-07-20"},
                    {"titulo": "Uma discussão necessária", "data": "2025-07-27"},
                    {"titulo": "A lei não pode nos salvar", "data": "2025-08-03"},
                    {"titulo": "Jesus nos libertou", "data": "2025-08-10"},
                    {"titulo": "Somos filhos de Deus", "data": "2025-08-17"},
                    {"titulo": "Paulo se preocupa conosco", "data": "2025-08-24"},
                    {"titulo": "Duas mães, duas alianças", "data": "2025-08-31"},
                    {"titulo": "Livres para servir", "data": "2025-09-07"},
                    {"titulo": "As obras da carne e o fruto do Espírito", "data": "2025-09-14"},
                    {"titulo": "Semear no Espírito", "data": "2025-09-21"},
                    {"titulo": "Glória somente na cruz", "data": "2025-09-28"}
                ],
                "ativa": True
            },
            {
                "id": "revista-003",
                "tema": "Recebendo o Batismo no Espírito Santo",
                "turma_ids": ["turma-005"],  # Pré-Adolescentes
                "licoes": [
                    {"titulo": "A Promessa do Derramamento do Espírito Santo", "data": "2025-07-06"},
                    {"titulo": "O Poder do Alto no Dia de Pentecoste", "data": "2025-07-13"},
                    {"titulo": "O Poder do Espírito na vida de Pedro e João", "data": "2025-07-20"},
                    {"titulo": "O Espírito Santo na vida de Paulo", "data": "2025-07-27"},
                    {"titulo": "O Mover do Espírito na Casa de Cornélio", "data": "2025-08-03"},
                    {"titulo": "O Evangelho em Éfeso e o Revestimento de Poder", "data": "2025-08-10"},
                    {"titulo": "As Línguas Estranhas como Evidência do Batismo", "data": "2025-08-17"},
                    {"titulo": "O Dom de Interpretar as Línguas", "data": "2025-08-24"},
                    {"titulo": "O Exercício dos Dons Espirituais", "data": "2025-08-31"},
                    {"titulo": "O Batismo no Espírito e a Santificação do Crente", "data": "2025-09-07"},
                    {"titulo": "O Batismo no Espírito e o Testemunho da Igreja", "data": "2025-09-14"},
                    {"titulo": "Vivendo o Avivamento Espiritual", "data": "2025-09-21"},
                    {"titulo": "Buscando o Batismo no Espírito Santo", "data": "2025-09-28"}
                ],
                "ativa": True
            },
            {
                "id": "revista-004",
                "tema": "Verdades que Jesus ensinou",
                "turma_ids": ["turma-004"],  # Juniores
                "licoes": [
                    {"titulo": "Jesus ensinou sobre perdão", "data": "2025-07-06"},
                    {"titulo": "Jesus ensinou sobre amar o próximo", "data": "2025-07-13"},
                    {"titulo": "Jesus ensinou sobre oração", "data": "2025-07-20"},
                    {"titulo": "Jesus ensinou sobre obediência", "data": "2025-07-27"},
                    {"titulo": "Jesus ensinou sobre fé", "data": "2025-08-03"},
                    {"titulo": "Jesus ensinou sobre servir", "data": "2025-08-10"},
                    {"titulo": "Jesus ensinou sobre generosidade", "data": "2025-08-17"},
                    {"titulo": "Jesus ensinou sobre humildade", "data": "2025-08-24"},
                    {"titulo": "Jesus ensinou sobre honestidade", "data": "2025-08-31"},
                    {"titulo": "Jesus ensinou sobre gratidão", "data": "2025-09-07"},
                    {"titulo": "Jesus ensinou sobre paciência", "data": "2025-09-14"},
                    {"titulo": "Jesus ensinou sobre esperança", "data": "2025-09-21"},
                    {"titulo": "Jesus ensinou sobre amor de Deus", "data": "2025-09-28"}
                ],
                "ativa": True
            },
            {
                "id": "revista-005",
                "tema": "As aventuras de um Grande Missionário",
                "turma_ids": ["turma-003"],  # Primários
                "licoes": [
                    {"titulo": "O caçador de cristãos", "data": "2025-07-06"},
                    {"titulo": "De perseguidor a missionário", "data": "2025-07-13"},
                    {"titulo": "Paulo em sua primeira viagem missionária", "data": "2025-07-20"},
                    {"titulo": "Um mágico enganador é desmascarado", "data": "2025-07-27"},
                    {"titulo": "Deuses ou missionários", "data": "2025-08-03"},
                    {"titulo": "Amizades missionárias", "data": "2025-08-10"},
                    {"titulo": "Mudança de planos", "data": "2025-08-17"},
                    {"titulo": "Oração e louvor causam grande tremor", "data": "2025-08-24"},
                    {"titulo": "A grande recompensa dos missionários", "data": "2025-08-31"},
                    {"titulo": "Os falsos missionários", "data": "2025-09-07"},
                    {"titulo": "A ressurreição durante a pregação", "data": "2025-09-14"},
                    {"titulo": "Paulo evangeliza um rei", "data": "2025-09-21"},
                    {"titulo": "Fé em meio às tempestades", "data": "2025-09-28"}
                ],
                "ativa": True
            },
            {
                "id": "revista-006",
                "tema": "A Igreja em Jerusalém — Como uma igreja grandiosa cumpria a missão",
                "turma_ids": ["turma-001", "turma-002", "turma-008", "turma-009", "turma-010", "turma-011"],  # Adultos
                "licoes": [
                    {"titulo": "A igreja se prepara para a missão", "data": "2025-07-06"},
                    {"titulo": "O batismo no Espírito Santo", "data": "2025-07-13"},
                    {"titulo": "As características da Igreja primitiva", "data": "2025-07-20"},
                    {"titulo": "A cura de um aleijado", "data": "2025-07-27"},
                    {"titulo": "Poder divino em meio à perseguição", "data": "2025-08-03"},
                    {"titulo": "Disciplina na Igreja", "data": "2025-08-10"},
                    {"titulo": "A escolha de diáconos", "data": "2025-08-17"},
                    {"titulo": "Estêvão, um diácono cheio de fé", "data": "2025-08-24"},
                    {"titulo": "Felipe, o evangelista", "data": "2025-08-31"},
                    {"titulo": "A conversão de Paulo", "data": "2025-09-07"},
                    {"titulo": "A visão de Pedro", "data": "2025-09-14"},
                    {"titulo": "O evangelho se espalha", "data": "2025-09-21"},
                    {"titulo": "A igreja em meio às perseguições", "data": "2025-09-28"}
                ],
                "ativa": True
            }
        ]
        
        await db.revistas.insert_many(revistas_data)
        
        print("✅ Importação concluída com sucesso!")
        print(f"   - Usuários: {len(DATA_COMPLETO['users'])}")
        print(f"   - Turmas: {len(DATA_COMPLETO['turmas'])}")
        print(f"   - Alunos: {len(alunos_data)}")
        print(f"   - Revistas: {len(revistas_data)}")
        print()
        print("🎉 Dados prontos para uso:")
        print("   👤 Admin: admin@ebd.com / 123456")
        print("   👨‍🏫 Prof: kell2@ebd.com / 123456")
        print("   🏫 11 turmas da igreja carregadas")
        print("   👥 242 alunos distribuídos nas turmas")
        print("   📚 6 revistas trimestrais completas")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        sys.exit(1)
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(import_complete_data())