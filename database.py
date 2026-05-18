import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='atletas.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com a tabela de atletas"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS atletas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                idade INTEGER NOT NULL,
                modalidade TEXT NOT NULL,
                genero TEXT NOT NULL,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def adicionar_atleta(self, nome, idade, modalidade, genero):
        """Adiciona um novo atleta ao banco de dados"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO atletas (nome, idade, modalidade, genero)
                VALUES (?, ?, ?, ?)
            ''', (nome, int(idade), modalidade, genero))
            
            conn.commit()
            conn.close()
            return True, "Atleta cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao cadastrar atleta: {str(e)}"
    
    def obter_todos_atletas(self):
        """Obtém todos os atletas cadastrados"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, nome, idade, modalidade, genero, data_cadastro FROM atletas ORDER BY id DESC')
            atletas = cursor.fetchall()
            
            conn.close()
            return atletas
        except Exception as e:
            print(f"Erro ao obter atletas: {str(e)}")
            return []
    
    def atualizar_atleta(self, id_atleta, nome, idade, modalidade, genero):
        """Atualiza informações de um atleta"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE atletas 
                SET nome = ?, idade = ?, modalidade = ?, genero = ?
                WHERE id = ?
            ''', (nome, int(idade), modalidade, genero, id_atleta))
            
            conn.commit()
            conn.close()
            return True, "Atleta atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar atleta: {str(e)}"
    
    def deletar_atleta(self, id_atleta):
        """Deleta um atleta do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM atletas WHERE id = ?', (id_atleta,))
            
            conn.commit()
            conn.close()
            return True, "Atleta deletado com sucesso!"
        except Exception as e:
            return False, f"Erro ao deletar atleta: {str(e)}"
    
    def buscar_atleta(self, termo_busca):
        """Busca atletas por nome ou modalidade"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nome, idade, modalidade, genero, data_cadastro 
                FROM atletas 
                WHERE nome LIKE ? OR modalidade LIKE ?
                ORDER BY nome
            ''', (f'%{termo_busca}%', f'%{termo_busca}%'))
            
            atletas = cursor.fetchall()
            conn.close()
            return atletas
        except Exception as e:
            print(f"Erro ao buscar atleta: {str(e)}")
            return []
    
    def obter_estatisticas(self):
        """Obtém estatísticas dos atletas"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Total de atletas
            cursor.execute('SELECT COUNT(*) FROM atletas')
            total = cursor.fetchone()[0]
            
            # Atletas por modalidade
            cursor.execute('''
                SELECT modalidade, COUNT(*) as total 
                FROM atletas 
                GROUP BY modalidade 
                ORDER BY total DESC
            ''')
            por_modalidade = cursor.fetchall()
            
            # Atletas por gênero
            cursor.execute('''
                SELECT genero, COUNT(*) as total 
                FROM atletas 
                GROUP BY genero
            ''')
            por_genero = cursor.fetchall()
            
            # Idade média
            cursor.execute('SELECT AVG(idade) FROM atletas')
            idade_media = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total': total,
                'por_modalidade': por_modalidade,
                'por_genero': por_genero,
                'idade_media': round(idade_media, 1) if idade_media else 0
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            return None
