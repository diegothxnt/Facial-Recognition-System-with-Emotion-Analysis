import tkinter as tk
from gui.main_window import MainWindow
from modules.face_recognition_ai import FaceRecognitionAI as FaceRecognitionSystem
import sqlite3
import os

def initialize_database():
    """Inicializar la base de datos"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Tabla de personas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Tabla de embeddings faciales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id INTEGER,
            embedding BLOB NOT NULL,
            FOREIGN KEY (persona_id) REFERENCES personas (id)
        )
    ''')
    
    # Tabla de detecciones emocionales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detecciones_emociones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id INTEGER,
            emocion TEXT NOT NULL,
            confianza REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (persona_id) REFERENCES personas (id)
        )
    ''')
  

   
