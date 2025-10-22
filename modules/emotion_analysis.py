import cv2
import numpy as np
from keras.models import load_model
import os

class EmotionAnalyzer:
    def __init__(self):
        self.model = None
        self.emotion_labels = ['Enojo', 'Desagrado', 'Miedo', 'Felicidad', 'Tristeza', 'Sorpresa', 'Neutral']
        self.model_path = "models/emotion_model.h5"
        self.load_model()
    
    def load_model(self):
        """Cargar modelo de emociones"""
        try:
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                print("✅ Modelo de emociones cargado correctamente")
            else:
                print("⚠️  No se encontró modelo de emociones, usando modo simulado")
                self.model = None
        except Exception as e:
            print(f"❌ Error cargando modelo de emociones: {e}")
            self.model = None
    
    def predecir_emocion(self, face_image):
        """Predecir emoción en imagen de rostro - MEJORADO"""
        try:
            if self.model is None:
                # Modo simulado para desarrollo
                return self.predecir_emocion_simulada(face_image)
            
            # Preprocesamiento mejorado
            face_processed = self.preprocesar_rostro(face_image)
            if face_processed is None:
                return "No detectable", 0.0
            
            # Predicción
            predictions = self.model.predict(face_processed)
            emotion_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][emotion_idx])
            
            emotion = self.emotion_labels[emotion_idx]
            
            # Filtrar predicciones de baja confianza
            if confidence < 0.6:
                return "Neutral", confidence
            
            return emotion, confidence
            
        except Exception as e:
            print(f"❌ Error en predicción de emociones: {e}")
            return "Error", 0.0
    
    def preprocesar_rostro(self, face_image):
        """Preprocesamiento mejorado del rostro"""
        try:
            # Convertir a escala de grises si es color
            if len(face_image.shape) == 3:
                face_gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                face_gray = face_image
            
            # Redimensionar a 48x48 (típico para modelos de emociones)
            face_resized = cv2.resize(face_gray, (48, 48))
            
            # Normalizar
            face_normalized = face_resized.astype('float32') / 255.0
            
            # Añadir dimensiones para el modelo (1, 48, 48, 1)
            face_batch = np.expand_dims(np.expand_dims(face_normalized, -1), 0)
            
            return face_batch
            
        except Exception as e:
            print(f"❌ Error en preprocesamiento: {e}")
            return None
    
    def predecir_emocion_simulada(self, face_image):
        """Predicción simulada basada en características de la imagen"""
        try:
            # Análisis simple basado en características visuales
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image
            
            # Calcular brillo promedio (rostros felices suelen estar mejor iluminados)
            brightness = np.mean(gray)
            
            # Detectar sonrisa simple (basado en patrones de intensidad)
            height, width = gray.shape
            mouth_region = gray[int(height*0.6):int(height*0.8), 
                              int(width*0.25):int(width*0.75)]
            
            if mouth_region.size > 0:
                mouth_variance = np.var(mouth_region)
            else:
                mouth_variance = 0
            
            # Lógica simple basada en características
            if mouth_variance > 500 and brightness > 80:
                return "Felicidad", 0.85
            elif brightness < 60:
                return "Tristeza", 0.7
            elif mouth_variance > 400:
                return "Sorpresa", 0.75
            else:
                return "Neutral", 0.6
                
        except Exception as e:
            print(f"❌ Error en emoción simulada: {e}")
            return "Neutral", 0.5
    
    def mejorar_iluminacion(self, image):
        """Mejorar iluminación de la imagen para mejor detección"""
        try:
            # Convertir a LAB
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Aplicar CLAHE a L
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l_enhanced = clahe.apply(l)
            
            # Combinar canales
            lab_enhanced = cv2.merge([l_enhanced, a, b])
            enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
            
            return enhanced
        except:
            return image