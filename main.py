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
  
   