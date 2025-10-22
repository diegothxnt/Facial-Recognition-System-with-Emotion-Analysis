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
    def cargar_rostros_conocidos(self):
        """Cargar rostros conocidos de la base de datos"""
        try:
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
                    print(f"✅ Cargado: {nombre} {apellido}")
                except Exception as e:
                    print(f"❌ Error cargando {nombre}: {e}")
            
        except Exception as e:
            print(f"❌ Error cargando rostros: {e}")
    
    def reconocer_rostro(self, imagen):
        """Reconocer rostro usando IA"""
        try:
            print("🧠 IA Reconociendo rostro...")
            embedding = self.extraer_embedding_ia(imagen)
            
            if embedding is None:
                return None, "No se detectó rostro", 0.0
            
            if not self.known_face_encodings:
                return None, "No hay personas registradas", 0.0
            
            # Comparar con rostros conocidos
            mejores_similitudes = []
            for i, known_embedding in enumerate(self.known_face_encodings):
                similitud = self.comparar_rostros_ia(embedding, known_embedding)
                mejores_similitudes.append(similitud)
                print(f"  📊 {self.known_face_names[i]}: {similitud:.3f}")
            
            if mejores_similitudes:
                mejor_indice = np.argmax(mejores_similitudes)
                mejor_similitud = mejores_similitudes[mejor_indice]
                
                print(f"🎯 Mejor coincidencia: {self.known_face_names[mejor_indice]} ({mejor_similitud:.3f})")
                
                if mejor_similitud > 0.6:  # Umbral para IA
                    return (
                        self.known_face_ids[mejor_indice],
                        self.known_face_names[mejor_indice],
                        mejor_similitud
                    )
                elif mejor_similitud > 0.4:
                    return (
                        self.known_face_ids[mejor_indice],
                        f"Posiblemente {self.known_face_names[mejor_indice]}",
                        mejor_similitud
                    )
            
            return None, "Persona no registrada", 0.0
            
        except Exception as e:
            print(f"❌ Error en IA: {e}")
            return None, "Error en reconocimiento", 0.0
    
    def registrar_nueva_persona(self, nombre, apellido, email, imagen):
        """Registrar nueva persona usando IA"""
        try:
            print(f"📝 IA Registrando: {nombre} {apellido}")
            embedding = self.extraer_embedding_ia(imagen)
            
            if embedding is None:
                return False, "No se pudo detectar un rostro con IA. Asegúrese de:\n• Buena iluminación\n• Rostro frontal y claro\n• Sin obstrucciones"
            
            # Verificar duplicados
            persona_existente = self.db.obtener_persona_por_email(email)
            if persona_existente:
                return False, "El email ya está registrado"
            
            # Registrar en base de datos
            success, mensaje = self.db.registrar_persona(nombre, apellido, email, embedding)
            
            if success:
                self.cargar_rostros_conocidos()
                print(f"✅ {nombre} {apellido} registrado con IA")
            
            return success, mensaje
            
        except Exception as e:
            error_msg = f"Error en IA al registrar: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def dibujar_detecciones(self, imagen):
        """Dibujar detecciones en la imagen"""
        try:
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            imagen_pil = Image.fromarray(imagen_rgb)
            
            # Detectar rostros
            boxes, probs = self.mtcnn.detect(imagen_pil)
            
            if boxes is not None:
                for box, prob in zip(boxes, probs):
                    if prob > 0.9:  # Confianza alta
                        x1, y1, x2, y2 = box.astype(int)
                        
                        # Dibujar rectángulo
                        cv2.rectangle(imagen, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Reconocer persona
                        persona_id, nombre, confianza = self.reconocer_rostro(imagen)
                        
                        if persona_id is not None:
                            texto = f"{nombre} ({confianza:.1%})"
                            color = (0, 255, 0)
                        else:
                            texto = "Desconocido"
                            color = (0, 0, 255)
                        
                        cv2.putText(imagen, texto, (x1, y1-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            return imagen
            
        except Exception as e:
            print(f"❌ Error dibujando detecciones: {e}")
            return imagen
