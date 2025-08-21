#!/usr/bin/env python3
"""
Sistema de Backup e Restore para EBD Manager
Permite backup e restore via linha de comando ou programático
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
import argparse
import zipfile
import shutil

# Configurações
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

class EBDBackupManager:
    def __init__(self, mongo_url=MONGO_URL, db_name=DB_NAME):
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.client = None
        self.db = None
    
    async def connect(self):
        """Conectar ao MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        
        # Testar conexão
        try:
            await self.client.admin.command('ping')
            print(f"✅ Conectado ao MongoDB: {self.mongo_url}")
            return True
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    async def close(self):
        """Fechar conexão"""
        if self.client:
            self.client.close()
    
    async def generate_backup(self, include_sessions=False):
        """
        Gerar backup completo dos dados
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Coleções para backup
        collections = ['users', 'turmas', 'students', 'attendance', 'revistas']
        if include_sessions:
            collections.append('sessions')
        
        print(f"🔄 Gerando backup - {timestamp}")
        print(f"📊 Coleções: {', '.join(collections)}")
        
        backup_data = {}
        total_records = 0
        
        for collection_name in collections:
            try:
                documents = await self.db[collection_name].find({}).to_list(None)
                
                # Converter ObjectId para string
                clean_documents = []
                for doc in documents:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    clean_documents.append(doc)
                
                backup_data[collection_name] = clean_documents
                total_records += len(clean_documents)
                print(f"   ✅ {collection_name}: {len(clean_documents)} registros")
                
            except Exception as e:
                print(f"   ⚠️ Erro em {collection_name}: {e}")
                backup_data[collection_name] = []
        
        # Metadados
        metadata = {
            "backup_timestamp": timestamp,
            "backup_date": datetime.now().isoformat(),
            "system_version": "EBD Manager v1.0",
            "mongo_url": self.mongo_url.replace(self.mongo_url.split('@')[-1].split('/')[0], '***') if '@' in self.mongo_url else self.mongo_url,
            "database_name": self.db_name,
            "total_collections": len(collections),
            "total_records": total_records,
            "collections": list(backup_data.keys())
        }
        
        complete_backup = {
            "metadata": metadata,
            "data": backup_data
        }
        
        print(f"✅ Backup gerado: {total_records} registros totais")
        return complete_backup, timestamp
    
    async def save_backup_to_file(self, backup_data, filename=None, compress=True):
        """
        Salvar backup em arquivo
        """
        if not filename:
            timestamp = backup_data['metadata']['backup_timestamp']
            filename = f"ebd_backup_{timestamp}"
        
        # Criar diretório de backups
        backup_dir = Path("/app/backups")
        backup_dir.mkdir(exist_ok=True)
        
        if compress:
            # Salvar como ZIP
            zip_path = backup_dir / f"{filename}.zip"
            json_content = json.dumps(backup_data, indent=2, ensure_ascii=False, default=str)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr(f"{filename}.json", json_content)
            
            file_path = zip_path
            print(f"📦 Backup comprimido salvo: {zip_path}")
        else:
            # Salvar como JSON
            json_path = backup_dir / f"{filename}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
            
            file_path = json_path
            print(f"📄 Backup salvo: {json_path}")
        
        # Mostrar informações do arquivo
        file_size = file_path.stat().st_size
        print(f"   📏 Tamanho: {file_size / (1024*1024):.2f} MB")
        
        return str(file_path)
    
    async def restore_from_file(self, file_path, force=False):
        """
        Restaurar dados de arquivo de backup
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        
        print(f"🔄 Restaurando backup de: {file_path}")
        
        # Ler arquivo
        try:
            if file_path.suffix == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zipf:
                    json_files = [f for f in zipf.namelist() if f.endswith('.json')]
                    if not json_files:
                        print("❌ Nenhum arquivo JSON encontrado no ZIP")
                        return False
                    
                    with zipf.open(json_files[0]) as f:
                        backup_data = json.load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                    
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            return False
        
        # Validar estrutura
        if 'data' not in backup_data:
            print("❌ Formato de backup inválido (falta 'data')")
            return False
        
        # Mostrar informações do backup
        metadata = backup_data.get('metadata', {})
        if metadata:
            print(f"   📅 Data do backup: {metadata.get('backup_date', 'N/A')}")
            print(f"   📊 Total de registros: {metadata.get('total_records', 'N/A')}")
            print(f"   📁 Coleções: {', '.join(metadata.get('collections', []))}")
        
        # Confirmação de segurança
        if not force:
            print("\n⚠️  ATENÇÃO: Este processo irá SUBSTITUIR todos os dados existentes!")
            print("📋 Coleções que serão afetadas:")
            for collection in backup_data['data'].keys():
                count = len(backup_data['data'][collection])
                print(f"   - {collection}: {count} registros")
            
            confirm = input("\n🔴 Tem certeza que deseja continuar? (digite 'CONFIRMAR'): ")
            if confirm != 'CONFIRMAR':
                print("❌ Operação cancelada pelo usuário")
                return False
        
        # Executar restore
        return await self.restore_backup_data(backup_data['data'])
    
    async def restore_backup_data(self, restore_data):
        """
        Restaurar dados no MongoDB
        """
        print("🔄 Iniciando restore...")
        
        restore_summary = {}
        collections = ['users', 'turmas', 'students', 'attendance', 'revistas', 'sessions']
        
        for collection_name in collections:
            if collection_name in restore_data:
                try:
                    # Limpar coleção
                    await self.db[collection_name].delete_many({})
                    
                    # Inserir dados
                    documents = restore_data[collection_name]
                    if documents:
                        # Limpar _id para evitar conflitos
                        clean_documents = []
                        for doc in documents:
                            if '_id' in doc and isinstance(doc['_id'], str):
                                del doc['_id']
                            clean_documents.append(doc)
                        
                        result = await self.db[collection_name].insert_many(clean_documents)
                        restore_summary[collection_name] = len(result.inserted_ids)
                        print(f"   ✅ {collection_name}: {len(result.inserted_ids)} registros")
                    else:
                        restore_summary[collection_name] = 0
                        print(f"   ⚠️ {collection_name}: vazio")
                        
                except Exception as e:
                    print(f"   ❌ {collection_name}: erro - {e}")
                    restore_summary[collection_name] = 0
        
        total_restored = sum(restore_summary.values())
        print(f"✅ Restore concluído: {total_restored} registros restaurados")
        
        return True
    
    async def list_backups(self):
        """
        Listar backups disponíveis
        """
        backup_dir = Path("/app/backups")
        if not backup_dir.exists():
            print("📁 Nenhum diretório de backup encontrado")
            return []
        
        backups = []
        for file_path in backup_dir.iterdir():
            if file_path.suffix in ['.json', '.zip']:
                stat = file_path.stat()
                backups.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size_mb': stat.st_size / (1024*1024),
                    'created': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
        
        if backups:
            print(f"📋 Backups disponíveis ({len(backups)}):")
            for backup in sorted(backups, key=lambda x: x['created'], reverse=True):
                print(f"   📄 {backup['filename']}")
                print(f"       📅 {backup['created']} | 📏 {backup['size_mb']:.2f} MB")
                print()
        else:
            print("📁 Nenhum backup encontrado")
        
        return backups

async def main():
    parser = argparse.ArgumentParser(description="EBD Manager - Sistema de Backup e Restore")
    parser.add_argument('action', choices=['backup', 'restore', 'list'], help='Ação a executar')
    parser.add_argument('--file', '-f', help='Arquivo para restore ou nome para backup')
    parser.add_argument('--compress', '-c', action='store_true', help='Comprimir backup (ZIP)')
    parser.add_argument('--force', action='store_true', help='Forçar restore sem confirmação')
    parser.add_argument('--sessions', '-s', action='store_true', help='Incluir sessões no backup')
    
    args = parser.parse_args()
    
    print("🚀 EBD MANAGER - SISTEMA DE BACKUP")
    print("=" * 50)
    
    manager = EBDBackupManager()
    
    if not await manager.connect():
        sys.exit(1)
    
    try:
        if args.action == 'backup':
            backup_data, timestamp = await manager.generate_backup(include_sessions=args.sessions)
            filename = args.file or f"ebd_backup_{timestamp}"
            
            file_path = await manager.save_backup_to_file(
                backup_data, 
                filename, 
                compress=args.compress
            )
            
            print(f"\n🎉 Backup criado com sucesso!")
            print(f"📄 Arquivo: {file_path}")
            
        elif args.action == 'restore':
            if not args.file:
                print("❌ Especifique o arquivo com --file")
                sys.exit(1)
            
            success = await manager.restore_from_file(args.file, force=args.force)
            if success:
                print(f"\n🎉 Restore concluído com sucesso!")
            else:
                print(f"\n❌ Falha no restore")
                sys.exit(1)
                
        elif args.action == 'list':
            await manager.list_backups()
    
    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(main())