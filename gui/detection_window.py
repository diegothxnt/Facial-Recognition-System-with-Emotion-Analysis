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



    def verificar_modelos(self):
        """Verificar si hay personas registradas en el sistema"""
        if hasattr(self.face_system, 'known_face_names') and len(self.face_system.known_face_names) == 0:
            messagebox.showwarning(
                "Advertencia", 
                "No hay personas registradas en el sistema.\n\n"
                "Por favor, registre personas primero en la sección 'Registrar Personas'.\n"
                "Mientras tanto, la cámara mostrará 'No registrado' para todos los rostros."
            )
    
    def setup_ui(self):
      
        main_frame = tk.Frame(self.window, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        
        title_label = tk.Label(
            main_frame,
            text="Detección en Tiempo Real - IA Optimizada",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(expand=True, fill='both')
        
       
        camera_frame = tk.Frame(content_frame, bg='#34495e', padx=20, pady=20)
        camera_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        
        info_frame = tk.Frame(content_frame, bg='#34495e', padx=20, pady=20)
        info_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        
        self.setup_camera(camera_frame)
        self.setup_info_panel(info_frame)
    
    def setup_camera(self, parent):
       
        camera_title = tk.Label(
            parent,
            text="Vista de la Cámara - Optimizada",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#34495e'
        )
        camera_title.pack(pady=(0, 10))
        
        self.camera_label = tk.Label(parent, bg='#2c3e50', relief='sunken', bd=2)
        self.camera_label.pack(expand=True, fill='both')
        
       
        control_frame = tk.Frame(parent, bg='#34495e')
        control_frame.pack(pady=10)
        
        button_style = {
            'font': ('Arial', 12),
            'width': 15,
            'height': 2,
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        self.btn_iniciar = tk.Button(
            control_frame,
            text="Iniciar Detección IA",
            command=self.iniciar_deteccion,
            bg='#2ecc71',
            fg='white',
            **button_style
        )
        self.btn_iniciar.pack(side='left', padx=10)
        
        self.btn_detener = tk.Button(
            control_frame,
            text="Detener Detección",
            command=self.detener_deteccion,
            bg='#e74c3c',
            fg='white',
            **button_style,
            state='disabled'
        )
        self.btn_detener.pack(side='left', padx=10)
        
        btn_cerrar = tk.Button(
            control_frame,
            text="Cerrar",
            command=self.cerrar,
            bg='#95a5a6',
            fg='white',
            **button_style
        )
        btn_cerrar.pack(side='left', padx=10)
    
    def setup_info_panel(self, parent):
        
        title_label = tk.Label(
            parent,
            text="Información de Detección - IA",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#34495e'
        )
        title_label.pack(pady=(0, 20))
        
        
        realtime_frame = tk.Frame(parent, bg='#2c3e50', relief='ridge', bd=2)
        realtime_frame.pack(fill='x', pady=(0, 20))
        
        
        self.info_labels = {}
        info_fields = [
            ("Estado:", "estado", "Esperando..."),
            ("Persona:", "persona", "---"),
            ("Emoción:", "emocion", "---"),
            ("Confianza:", "confianza", "---"),
            ("Tiempo:", "tiempo", "---")
        ]
        
        for i, (label_text, key, default_value) in enumerate(info_fields):
            frame = tk.Frame(realtime_frame, bg='#2c3e50')
            frame.pack(fill='x', padx=10, pady=5)
            
            label = tk.Label(
                frame,
                text=label_text,
                font=('Arial', 12, 'bold'),
                fg='#3498db',
                bg='#2c3e50',
                width=10,
                anchor='w'
            )
            label.pack(side='left')
            
            value_label = tk.Label(
                frame,
                text=default_value,
                font=('Arial', 12),
                fg='white',
                bg='#2c3e50',
                anchor='w'
            )
            value_label.pack(side='left', fill='x', expand=True)
            self.info_labels[key] = value_label
        
        
        history_label = tk.Label(
            parent,
            text="Últimas Detecciones:",
            font=('Arial', 14, 'bold'),
            fg='#3498db',
            bg='#34495e',
            anchor='w'
        )
        history_label.pack(anchor='w', pady=(20, 10))
        
        
        tree_frame = tk.Frame(parent, bg='#34495e')
        tree_frame.pack(fill='both', expand=True)
        
        
        columns = ('Hora', 'Persona', 'Emoción', 'Confianza')
        self.history_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        
        column_widths = {'Hora': 120, 'Persona': 150, 'Emoción': 100, 'Confianza': 100}
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=column_widths[col])
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
    
    def iniciar_deteccion(self):
        """Iniciar el proceso de detección con IA"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                
                self.cap = cv2.VideoCapture(1)
                if not self.cap.isOpened():
                    raise Exception("No se pudo acceder a ninguna cámara")
            
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.detection_enabled = True
            self.btn_iniciar.config(state='disabled')
            self.btn_detener.config(state='normal')
            self.info_labels['estado'].config(text="Detectando con IA...", fg='#2ecc71')
            self.frame_count = 0
            self.last_recognition_time = 0
            self.procesar_deteccion()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la cámara: {str(e)}")
    
    def detener_deteccion(self):
        """Detener el proceso de detección"""
        self.detection_enabled = False
        self.btn_iniciar.config(state='normal')
        self.btn_detener.config(state='disabled')
        self.info_labels['estado'].config(text="Detenido", fg='#e74c3c')
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        
        self.camera_label.configure(image='')
