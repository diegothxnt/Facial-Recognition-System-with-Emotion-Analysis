import cv2
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import sqlite3
import json
from PIL import Image
import os
from modules.database import DatabaseManager

class FaceRecognitionAI:
    def __init__(self):
        self.db = DatabaseManager()
        
        # Cargar modelo MTCNN para detección de rostros
        self.mtcnn = MTCNN(keep_all=True, device='cpu')
        
        # Cargar modelo FaceNet pre-entrenado para embeddings
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        self.cargar_rostros_conocidos()
        print("✅ IA de Reconocimiento Facial INICIALIZADA")
        print(f"👥 Rostros conocidos cargados: {len(self.known_face_encodings)}")
    
    def extraer_embedding_ia(self, imagen):
        """Extraer embedding facial usando FaceNet"""
        try:
            # Convertir OpenCV a PIL
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            imagen_pil = Image.fromarray(imagen_rgb)
            
            # Detectar rostros usando MTCNN
            boxes, _ = self.mtcnn.detect(imagen_pil)
            
            if boxes is not None and len(boxes) > 0:
                # Tomar el primer rostro detectado
                box = boxes[0]
                x1, y1, x2, y2 = box.astype(int)
                
                # Extraer embedding usando FaceNet
                cara = self.mtcnn(imagen_pil)
                
                if cara is not None:
                    embedding = self.resnet(cara.unsqueeze(0))
                    embedding = embedding.detach().numpy().flatten()
                    
                    print(f"✅ Embedding IA extraído: {len(embedding)} dimensiones")
                    return embedding
            
            print("❌ No se detectaron rostros con IA")
            return None
            
        except Exception as e:
            print(f"❌ Error en IA: {e}")
            # Fallback a método tradicional
            return self.extraer_embedding_tradicional(imagen)
    
    def extraer_embedding_tradicional(self, imagen):
        """Método tradicional como fallback"""
        try:
            # Detector OpenCV como respaldo
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            rostros = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            
            if len(rostros) > 0:
                x, y, w, h = rostros[0]
                rostro_recortado = imagen[y:y+h, x:x+w]
                
                # Características simples
                rostro_redim = cv2.resize(rostro_recortado, (100, 100))
                gris = cv2.cvtColor(rostro_redim, cv2.COLOR_BGR2GRAY)
                caracteristicas = gris.flatten().astype(np.float32) / 255.0
                
                print(f"✅ Embedding tradicional: {len(caracteristicas)} dimensiones")
                return caracteristicas
            
            return None
            
        except Exception as e:
            print(f"❌ Error en método tradicional: {e}")
            return None
    
    def comparar_rostros_ia(self, embedding1, embedding2):
        """Comparar embeddings usando distancia coseno"""
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        try:
            # Normalizar embeddings
            emb1_norm = embedding1 / np.linalg.norm(embedding1)
            emb2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # Similitud coseno
            similitud = np.dot(emb1_norm, emb2_norm)
            return float(similitud)
            
        except Exception as e:
            print(f"❌ Error comparando: {e}")
            return 0.0
    
