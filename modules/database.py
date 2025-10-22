import sqlite3
import numpy as np
import json
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path='data/database.db'):
        self.db_path = db_path
        
        # Asegurarse de que el directorio data existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Inicializar la base de datos
        self.init_database()
        print(f"📍 Base de datos: {os.path.abspath(self.db_path)}")
    
    def init_database(self):
        """Inicializar la base de datos con las tablas necesarias"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de personas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de embeddings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_id INTEGER NOT NULL,
                    embedding TEXT NOT NULL,
                    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
                )
            ''')
            
            # Tabla de detecciones_emociones (corregida para coincidir con tu código)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detecciones_emociones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_id INTEGER NOT NULL,
                    emocion TEXT NOT NULL,
                    confianza REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Base de datos inicializada correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando base de datos: {e}")
    
    def registrar_persona(self, nombre, apellido, email, embedding):
        """Registrar una nueva persona en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar si el email ya existe
            cursor.execute("SELECT id FROM personas WHERE email = ?", (email,))
            if cursor.fetchone():
                return False, "El email ya está registrado"
            
            # Insertar persona
            cursor.execute(
                "INSERT INTO personas (nombre, apellido, email) VALUES (?, ?, ?)",
                (nombre, apellido, email)
            )
            persona_id = cursor.lastrowid
            
            # Guardar embedding
            embedding_blob = json.dumps(embedding.tolist() if hasattr(embedding, 'tolist') else embedding)
            cursor.execute(
                "INSERT INTO embeddings (persona_id, embedding) VALUES (?, ?)",
                (persona_id, embedding_blob)
            )
            
            conn.commit()
            return True, "Persona registrada exitosamente"
            
        except Exception as e:
            conn.rollback()
            return False, f"Error al registrar: {str(e)}"
        finally:
            conn.close()
    
    def obtener_persona_por_email(self, email):
        """Obtener información de una persona por email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.nombre, p.apellido, p.email, e.embedding 
            FROM personas p 
            LEFT JOIN embeddings e ON p.id = e.persona_id 
            WHERE p.email = ?
        ''', (email,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'nombre': result[1],
                'apellido': result[2],
                'email': result[3],
                'embedding': json.loads(result[4]) if result[4] else None
            }
        return None
    
    def obtener_todas_personas(self):
        """Obtener todas las personas registradas - VERSIÓN CORREGIDA"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='personas'")
            if not cursor.fetchone():
                print("❌ La tabla 'personas' no existe")
                return []
            
            cursor.execute('''
                SELECT id, nombre, apellido, email, fecha_registro 
                FROM personas 
                ORDER BY fecha_registro DESC
            ''')
            
            personas = cursor.fetchall()
            conn.close()
            
            print(f"✅ Se encontraron {len(personas)} personas en la base de datos")
            for persona in personas:
                print(f"   - {persona[1]} {persona[2]} (ID: {persona[0]})")
                
            return personas
        except Exception as e:
            print(f"❌ Error al obtener personas: {e}")
            return []
    
    def eliminar_persona(self, persona_id):
        """Eliminar una persona y sus datos relacionados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Primero obtener información de la persona para el mensaje
            cursor.execute("SELECT nombre, apellido FROM personas WHERE id = ?", (persona_id,))
            persona_info = cursor.fetchone()
            
            if not persona_info:
                return False, "La persona no existe"
            
            # Eliminar de la tabla detecciones_emociones primero
            try:
                cursor.execute('DELETE FROM detecciones_emociones WHERE persona_id = ?', (persona_id,))
            except:
                pass  # La tabla puede no existir
            
            # Eliminar de la tabla embeddings
            cursor.execute('DELETE FROM embeddings WHERE persona_id = ?', (persona_id,))
            
            # Eliminar de la tabla personas
            cursor.execute('DELETE FROM personas WHERE id = ?', (persona_id,))
            
            conn.commit()
            conn.close()
            
            nombre_completo = f"{persona_info[0]} {persona_info[1]}"
            return True, f"Persona '{nombre_completo}' eliminada correctamente"
            
        except Exception as e:
            return False, f"Error al eliminar persona: {str(e)}"
    
    def guardar_deteccion_emocion(self, persona_id, emocion, confianza):
        """Guardar detección emocional en el historial"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO detecciones_emociones (persona_id, emocion, confianza) VALUES (?, ?, ?)",
                (persona_id, emocion, confianza)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error guardando detección: {e}")
            return False
    
    def obtener_historial_emociones(self, persona_id=None):
        """Obtener historial de detecciones emocionales"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if persona_id:
                cursor.execute('''
                    SELECT de.emocion, de.confianza, de.timestamp, p.nombre, p.apellido
                    FROM detecciones_emociones de
                    JOIN personas p ON de.persona_id = p.id
                    WHERE de.persona_id = ?
                    ORDER BY de.timestamp DESC
                ''', (persona_id,))
            else:
                cursor.execute('''
                    SELECT de.emocion, de.confianza, de.timestamp, p.nombre, p.apellido
                    FROM detecciones_emociones de
                    JOIN personas p ON de.persona_id = p.id
                    ORDER BY de.timestamp DESC
                ''')
            
            resultados = cursor.fetchall()
            conn.close()
            
            return [{
                'emocion': r[0],
                'confianza': r[1],
                'timestamp': r[2],
                'nombre': r[3],
                'apellido': r[4]
            } for r in resultados]
        except Exception as e:
            print(f"❌ Error obteniendo historial: {e}")
            return []
    
    def diagnosticar_bd(self):
        """Función de diagnóstico para ver el estado de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ver tablas existentes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = cursor.fetchall()
            
            info = {
                'ruta': os.path.abspath(self.db_path),
                'tablas': [tabla[0] for tabla in tablas],
                'conteos': {}
            }
            
            # Contar registros en cada tabla
            for tabla in info['tablas']:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                info['conteos'][tabla] = cursor.fetchone()[0]
            
            conn.close()
            return info
            
        except Exception as e:
            return {'error': str(e)}