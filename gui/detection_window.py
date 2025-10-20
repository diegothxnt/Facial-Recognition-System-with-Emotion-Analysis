import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import time
import numpy as np

from modules.face_recognition_ai import FaceRecognitionAI as FaceRecognitionSystem
from modules.emotion_analysis import EmotionAnalyzer
from modules.database import DatabaseManager

class DetectionWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Detección en Tiempo Real - IA Optimizada")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2c3e50')
        self.window.protocol("WM_DELETE_WINDOW", self.cerrar)
        
        
        self.face_system = FaceRecognitionSystem()
        self.emotion_analyzer = EmotionAnalyzer()
        self.db = DatabaseManager()
        
        self.cap = None
        self.detection_enabled = False
        self.ultima_deteccion = None
        self.current_image = None
        self.frame_count = 0
        self.last_recognition_time = 0
        
        self.setup_ui()
        self.verificar_modelos()
    
    