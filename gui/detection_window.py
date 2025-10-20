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

    def procesar_deteccion(self):
        """Procesar frame por frame para detección con IA - OPTIMIZADO"""
        if not self.detection_enabled or self.cap is None:
            return
        
        try:
            ret, frame = self.cap.read()
            if ret:
                self.frame_count += 1
                current_time = time.time()
                
                
                frame_small = cv2.resize(frame, (320, 240))
                frame_display = frame.copy()
                
                
                gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))
                
                nombre = "Desconocido"
                confianza = 0.0
                emocion = "---"
                confianza_emocion = 0.0
                persona_id = None
                
                
                should_recognize = (self.frame_count % 10 == 0 or 
                                  current_time - self.last_recognition_time > 0.5)
                
                if should_recognize and len(faces) > 0:
                    self.last_recognition_time = current_time
                    
                    persona_id, nombre, confianza = self.face_system.reconocer_rostro(frame)
                    print(f"🎭 Reconocimiento IA: {nombre} ({confianza:.2f})")
                
                
                for (x, y, w, h) in faces:
                    
                    scale_x = frame.shape[1] / frame_small.shape[1]
                    scale_y = frame.shape[0] / frame_small.shape[0]
                    x_orig = int(x * scale_x)
                    y_orig = int(y * scale_y)
                    w_orig = int(w * scale_x)
                    h_orig = int(h * scale_y)
                    
                    
                    try:
                        face_roi = frame[y_orig:y_orig+h_orig, x_orig:x_orig+w_orig]
                        if face_roi.size > 0:
                            emocion, confianza_emocion = self.emotion_analyzer.predecir_emocion(face_roi)
                            print(f"😊 Emoción detectada: {emocion} ({confianza_emocion:.2f})")
                    except Exception as e:
                        print(f"❌ Error en análisis de emociones: {e}")
                        emocion, confianza_emocion = "Error", 0.0
                    
                    
                    if nombre != "Desconocido" and confianza > 0.6:
                        color = (0, 255, 0)  
                        texto = f"{nombre} ({confianza:.1%})"
                        if emocion != "---":
                            texto += f" | {emocion}"
                    else:
                        color = (0, 0, 255)  
                        texto = "No registrado"
                        if emocion != "---":
                            texto += f" | {emocion}"
                    
                   
                    cv2.rectangle(frame_display, (x_orig, y_orig), 
                                (x_orig+w_orig, y_orig+h_orig), color, 2)
                    cv2.putText(frame_display, texto, (x_orig, y_orig-10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
               
                self.actualizar_interfaz(nombre, emocion, max(confianza, confianza_emocion), persona_id)
                
                
                frame_display = cv2.resize(frame_display, (640, 480))
                rgb_frame = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                
                self.current_image = imgtk
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
            
        except Exception as e:
            print(f"Error en procesamiento IA: {e}")
            
        
        
        if self.detection_enabled:
            self.window.after(15, self.procesar_deteccion)
    
    def actualizar_interfaz(self, nombre, emocion, confianza, persona_id):
        """Actualizar la interfaz con la información de detección"""
        tiempo_actual = time.strftime("%H:%M:%S")
        
        
        self.info_labels['persona'].config(text=nombre)
        self.info_labels['emocion'].config(text=emocion)
        
        if confianza > 0:
            self.info_labels['confianza'].config(text=f"{confianza:.1%}")
        else:
            self.info_labels['confianza'].config(text="---")
            
        self.info_labels['tiempo'].config(text=tiempo_actual)
        
        
        if persona_id is not None and nombre != "Desconocido" and confianza > 0.7:
            try:
                self.db.guardar_deteccion_emocion(persona_id, emocion, confianza)
                
                
                self.history_tree.insert(
                    '', 0,
                    values=(tiempo_actual, nombre, emocion, f"{confianza:.1%}")
                )
                
                
                if len(self.history_tree.get_children()) > 50:
                    self.history_tree.delete(self.history_tree.get_children()[-1])
                    
            except Exception as e:
                print(f"Error al guardar en BD: {e}")
    
    def cerrar(self):
        """Cerrar la ventana y liberar recursos"""
        self.detener_deteccion()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = DetectionWindow(root)
    root.mainloop() 
