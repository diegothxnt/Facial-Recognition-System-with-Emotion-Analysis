import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os
from modules.face_recognition import FaceRecognitionSystem

class RegistrationWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Registro de Personas")
        self.window.geometry("900x600")
        self.window.configure(bg='#2c3e50')
        
        self.face_system = FaceRecognitionSystem()
        self.capturas = []
        self.cap = None
        self.is_camera_active = False
        
        # Variables para el formulario
        self.nombre_var = tk.StringVar()
        self.apellido_var = tk.StringVar()
        self.email_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Registro de Nueva Persona",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 15))
        
        # Frame de contenido (dividido en izquierda y derecha)
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill='both', expand=True)
        
        # Left frame - Formulario
        left_frame = tk.Frame(content_frame, bg='#34495e', padx=15, pady=15)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Right frame - Cámara
        right_frame = tk.Frame(content_frame, bg='#34495e', padx=15, pady=15)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self.setup_form(left_frame)
        self.setup_camera(right_frame)
        
        # Iniciar cámara automáticamente
        self.iniciar_camara()
    
    def setup_form(self, parent):
        # Configuración de estilos
        label_style = {'font': ('Arial', 11), 'bg': '#34495e', 'fg': 'white', 'anchor': 'w'}
        entry_style = {'font': ('Arial', 11), 'width': 25}
        
        # Campos del formulario
        tk.Label(parent, text="Nombre:", **label_style).grid(row=0, column=0, sticky='w', pady=8)
        tk.Entry(parent, textvariable=self.nombre_var, **entry_style).grid(row=0, column=1, pady=8, padx=(10, 0))
        
        tk.Label(parent, text="Apellido:", **label_style).grid(row=1, column=0, sticky='w', pady=8)
        tk.Entry(parent, textvariable=self.apellido_var, **entry_style).grid(row=1, column=1, pady=8, padx=(10, 0))
        
        tk.Label(parent, text="Email:", **label_style).grid(row=2, column=0, sticky='w', pady=8)
        tk.Entry(parent, textvariable=self.email_var, **entry_style).grid(row=2, column=1, pady=8, padx=(10, 0))
        
        # Espaciador
        tk.Frame(parent, height=20, bg='#34495e').grid(row=3, column=0, columnspan=2)
        
        # Botones
        button_style = {
            'font': ('Arial', 11),
            'width': 18,
            'height': 1,
            'bg': '#3498db',
            'fg': 'white',
            'relief': 'raised',
            'cursor': 'hand2'
        }
        
        btn_capturar = tk.Button(
            parent,
            text="📷 Capturar Rostro",
            command=self.capturar_rostro,
            **button_style
        )
        btn_capturar.grid(row=4, column=0, columnspan=2, pady=8)
        
        btn_registrar = tk.Button(
            parent,
            text="✅ Registrar Persona",
            command=self.registrar_persona,
            **{**button_style, 'bg': '#2ecc71'}
        )
        btn_registrar.grid(row=5, column=0, columnspan=2, pady=8)
        
        btn_limpiar = tk.Button(
            parent,
            text="🔄 Limpiar Formulario",
            command=self.limpiar_formulario,
            **{**button_style, 'bg': '#e74c3c'}
        )
        btn_limpiar.grid(row=6, column=0, columnspan=2, pady=8)
        
        # Indicador de calidad
        self.quality_label = tk.Label(
            parent,
            text="📸 Capturas: 0/3 (Mínimo: 1 captura)",
            font=('Arial', 10),
            bg='#34495e',
            fg='#f39c12'
        )
        self.quality_label.grid(row=7, column=0, columnspan=2, pady=15)
        
        # Lista de capturas
        tk.Label(parent, text="Capturas realizadas:", 
                font=('Arial', 10, 'bold'), bg='#34495e', fg='white').grid(row=8, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.capturas_listbox = tk.Listbox(parent, height=4, font=('Arial', 9))
        self.capturas_listbox.grid(row=9, column=0, columnspan=2, pady=5, sticky='ew')
    
    def setup_camera(self, parent):
        # Título de la cámara
        cam_title = tk.Label(
            parent,
            text="Vista Previa de Cámara",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#34495e'
        )
        cam_title.pack(pady=(0, 10))
        
        # Frame para la vista de cámara
        cam_display_frame = tk.Frame(parent, bg='black', width=400, height=300)
        cam_display_frame.pack(pady=5)
        cam_display_frame.pack_propagate(False)  # Mantener tamaño fijo
        
        # Label para mostrar la cámara
        self.camera_label = tk.Label(cam_display_frame, bg='black')
        self.camera_label.pack(fill='both', expand=True)
        
        # Frame para controles de cámara
        control_frame = tk.Frame(parent, bg='#34495e')
        control_frame.pack(pady=15)
        
        # Botón de activar/desactivar cámara
        self.btn_toggle_cam = tk.Button(
            control_frame,
            text="🔴 Desactivar Cámara",
            command=self.toggle_camara,
            font=('Arial', 10),
            width=15,
            bg='#e74c3c',
            fg='white',
            relief='raised'
        )
        self.btn_toggle_cam.pack(side='left', padx=5)
        
        # Botón cerrar
        btn_cerrar = tk.Button(
            control_frame,
            text="❌ Cerrar",
            command=self.cerrar,
            font=('Arial', 10),
            width=10,
            bg='#95a5a6',
            fg='white',
            relief='raised'
        )
        btn_cerrar.pack(side='left', padx=5)
        
        # Instrucciones
        instructions = tk.Label(
            parent,
            text="💡 Instrucciones:\n1. Active la cámara\n2. Mire directamente\n3. Capture su rostro\n4. Complete el formulario",
            font=('Arial', 9),
            bg='#34495e',
            fg='#ecf0f1',
            justify='left'
        )
        instructions.pack(pady=10)
    
    def iniciar_camara(self):
        """Iniciar la cámara web"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                # Intentar con índice 1 si el 0 falla
                self.cap = cv2.VideoCapture(1)
                if not self.cap.isOpened():
                    messagebox.showerror("Error", "No se pudo acceder a ninguna cámara")
                    return
            
            self.is_camera_active = True
            self.btn_toggle_cam.config(text="🟢 Desactivar Cámara", bg='#e74c3c')
            self.actualizar_vista_previa()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la cámara: {str(e)}")
    
    def toggle_camara(self):
        """Activar/desactivar cámara"""
        if self.is_camera_active:
            # Desactivar cámara
            self.is_camera_active = False
            self.btn_toggle_cam.config(text="📹 Activar Cámara", bg='#2ecc71')
            
            # Mostrar imagen negra
            img = Image.new('RGB', (400, 300), color='black')
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
            
            if self.cap:
                self.cap.release()
                
        else:
            # Activar cámara
            self.iniciar_camara()
    
    def actualizar_vista_previa(self):
        """Actualizar la vista previa de la cámara"""
        if self.is_camera_active and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # Redimensionar para la vista previa
                frame = cv2.resize(frame, (400, 300))
                
                # Detectar rostros
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                rostros = self.face_system.face_cascade.detectMultiScale(gray, 1.1, 5)
                
                # Dibujar cuadros alrededor de rostros
                for (x, y, w, h) in rostros:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Convertir a RGB y mostrar
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)  # CORREGIDO: era imgtkk
            
            # Programar próxima actualización
            if self.is_camera_active:
                self.window.after(15, self.actualizar_vista_previa)
    
    def capturar_rostro(self):
        """Capturar el rostro actual de la cámara"""
        if not self.is_camera_active:
            messagebox.showwarning("Cámara desactivada", "Active la cámara primero")
            return
        
        if len(self.capturas) >= 3:
            messagebox.showinfo("Límite alcanzado", "Máximo 3 capturas. Puede registrar la persona.")
            return
        
        ret, frame = self.cap.read()
        if ret:
            # Verificar que se detecte un rostro
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostros = self.face_system.face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(rostros) > 0:
                self.capturas.append(frame)
                self.actualizar_lista_capturas()
                self.quality_label.config(
                    text=f"✅ Capturas: {len(self.capturas)}/3 - Rostro detectado",
                    fg='#2ecc71'
                )
                messagebox.showinfo("Éxito", f"Rostro capturado correctamente ({len(self.capturas)}/3)")
            else:
                messagebox.showerror("Error", "No se detectó ningún rostro. Acerquese a la cámara.")
        else:
            messagebox.showerror("Error", "No se pudo capturar la imagen")
    
    def actualizar_lista_capturas(self):
        """Actualizar la lista de capturas"""
        self.capturas_listbox.delete(0, tk.END)
        for i in range(len(self.capturas)):
            self.capturas_listbox.insert(tk.END, f"Captura {i+1} - Rostro detectado")
    
    def registrar_persona(self):
        """Registrar la persona con las capturas tomadas"""
        nombre = self.nombre_var.get().strip()
        apellido = self.apellido_var.get().strip()
        email = self.email_var.get().strip()
        
        # Validaciones
        if not nombre or not apellido or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        if len(self.capturas) == 0:
            messagebox.showerror("Error", "Debe capturar al menos un rostro")
            return
        
        if '@' not in email or '.' not in email:
            messagebox.showerror("Error", "Ingrese un email válido")
            return
        
        # Registrar persona
        success, message = self.face_system.registrar_nueva_persona(
            nombre, apellido, email, self.capturas[0]
        )
        
        if success:
            messagebox.showinfo("Éxito", f"Persona registrada:\n{nombre} {apellido}\n{email}")
            self.limpiar_formulario()
        else:
            messagebox.showerror("Error", message)
    
    def limpiar_formulario(self):
        """Limpiar el formulario y reiniciar capturas"""
        self.nombre_var.set("")
        self.apellido_var.set("")
        self.email_var.set("")
        self.capturas = []
        self.actualizar_lista_capturas()
        self.quality_label.config(
            text="📸 Capturas: 0/3 (Mínimo: 1 captura)",
            fg='#f39c12'
        )
    
    def cerrar(self):
        """Cerrar la ventana y liberar recursos"""
        self.is_camera_active = False
        if self.cap is not None:
            self.cap.release()
        self.window.destroy()