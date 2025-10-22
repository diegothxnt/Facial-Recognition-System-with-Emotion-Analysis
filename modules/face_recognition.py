import cv2
import numpy as np
import sqlite3
import json
from modules.database import DatabaseManager

class FaceRecognitionSystem:
    def __init__(self):
        self.db = DatabaseManager()
        # Usar el clasificador de rostros de OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.cargar_rostros_conocidos()
    
    def extraer_caracteristicas(self, imagen_rostro):
        """Extraer características básicas del rostro usando OpenCV"""
        try:
            # Redimensionar a tamaño fijo
            rostro_redim = cv2.resize(imagen_rostro, (100, 100))
            # Convertir a escala de grises
            gris = cv2.cvtColor(rostro_redim, cv2.COLOR_BGR2GRAY)
            # Aplanar y normalizar
            caracteristicas = gris.flatten().astype(np.float32) / 255.0
            return caracteristicas
        except Exception as e:
            print(f"Error en extraer_caracteristicas: {e}")
            return None
    
    def extraer_embedding(self, imagen):
        """Extraer embedding facial usando OpenCV"""
        try:
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            # Detectar rostros
            rostros = self.face_cascade.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(rostros) > 0:
                x, y, w, h = rostros[0]
                rostro_recortado = imagen[y:y+h, x:x+w]
                return self.extraer_caracteristicas(rostro_recortado)
            return None
        except Exception as e:
            print(f"Error al extraer embedding: {e}")
            return None
    
    def comparar_rostros(self, embedding1, embedding2):
        """Comparar dos embeddings usando distancia euclidiana"""
        if embedding1 is None or embedding2 is None:
            return 0.0
        try:
            distancia = np.linalg.norm(embedding1 - embedding2)
            # Convertir distancia a similitud (0-1)
            similitud = 1.0 / (1.0 + distancia)
            return similitud
        except Exception as e:
            print(f"Error en comparar_rostros: {e}")
            return 0.0
    
    def cargar_rostros_conocidos(self):
        """Cargar todos los rostros conocidos de la base de datos"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.nombre, p.apellido, e.embedding 
            FROM personas p 
            JOIN embeddings e ON p.id = e.persona_id
        ''')
        
        resultados = cursor.fetchall()
        conn.close()
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        for resultado in resultados:
            persona_id, nombre, apellido, embedding_json = resultado
            try:
                embedding = np.array(json.loads(embedding_json))
                self.known_face_encodings.append(embedding)
                self.known_face_names.append(f"{nombre} {apellido}")
                self.known_face_ids.append(persona_id)
            except Exception as e:
                print(f"Error cargando rostro para {nombre}: {e}")
    
    def reconocer_rostro(self, imagen):
        """Reconocer un rostro en una imagen"""
        try:
            embedding = self.extraer_embedding(imagen)
            if embedding is None:
                return None, "No se detectó rostro", 0.0
            
            # Si no hay rostros conocidos
            if not self.known_face_encodings:
                return None, "No hay personas registradas", 0.0
            
            # Comparar con rostros conocidos
            mejores_similitudes = []
            for known_embedding in self.known_face_encodings:
                similitud = self.comparar_rostros(embedding, known_embedding)
                mejores_similitudes.append(similitud)
            
            if mejores_similitudes:
                mejor_indice = np.argmax(mejores_similitudes)
                mejor_similitud = mejores_similitudes[mejor_indice]
                
                if mejor_similitud > 0.6:  # Umbral de similitud
                    return (
                        self.known_face_ids[mejor_indice],
                        self.known_face_names[mejor_indice],
                        mejor_similitud
                    )
            
            return None, "Persona no registrada", 0.0
            
        except Exception as e:
            print(f"Error en reconocimiento: {e}")
            return None, "Error en reconocimiento", 0.0
    
    def registrar_nueva_persona(self, nombre, apellido, email, imagen):
        """Registrar una nueva persona"""
        try:
            embedding = self.extraer_embedding(imagen)
            if embedding is None:
                return False, "No se pudo extraer embedding facial - no se detectó rostro"
            
            # Verificar duplicados
            persona_existente = self.db.obtener_persona_por_email(email)
            if persona_existente:
                return False, "El email ya está registrado"
            
            # Registrar en base de datos
            success, mensaje = self.db.registrar_persona(nombre, apellido, email, embedding)
            
            if success:
                # Actualizar lista de rostros conocidos
                self.cargar_rostros_conocidos()
            
            return success, mensaje
            
        except Exception as e:
            return False, f"Error al registrar: {str(e)}"