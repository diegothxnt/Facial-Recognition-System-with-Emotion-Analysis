import tkinter as tk
from tkinter import ttk, messagebox
from gui.registration_window import RegistrationWindow
from gui.detection_window import DetectionWindow
from gui.reports_window import ReportsWindow
from gui.simple_delete_window import SimpleDeleteWindow  # NUEVO IMPORT

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reconocimiento Facial con Análisis de Emociones")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Sistema de Reconocimiento Facial",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 30))
        
        # Subtítulo
        subtitle_label = tk.Label(
            main_frame,
            text="Análisis de Emociones en Tiempo Real",
            font=('Arial', 16),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Botones de navegación
        button_style = {
            'font': ('Arial', 14),
            'width': 25,
            'height': 2,
            'bg': '#3498db',
            'fg': 'white',
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        btn_registro = tk.Button(
            main_frame,
            text="📝 Registro de Personas",
            command=self.abrir_registro,
            **button_style
        )
        btn_registro.pack(pady=15)
        
        btn_deteccion = tk.Button(
            main_frame,
            text="👁️ Detección en Tiempo Real",
            command=self.abrir_deteccion,
            **button_style
        )
        btn_deteccion.pack(pady=15)
        
        # NUEVO BOTÓN PARA ELIMINAR USUARIOS
        btn_eliminar = tk.Button(
            main_frame,
            text="🗑️ Eliminar Usuarios",
            command=self.abrir_eliminar,
            bg='#e74c3c',  # Rojo para indicar peligro
            fg='white',
            font=('Arial', 14),
            width=25,
            height=2,
            relief='flat',
            cursor='hand2'
        )
        btn_eliminar.pack(pady=15)
        
        btn_reportes = tk.Button(
            main_frame,
            text="📊 Reportes y Estadísticas",
            command=self.abrir_reportes,
            **button_style
        )
        btn_reportes.pack(pady=15)
        
        btn_salir = tk.Button(
            main_frame,
            text="🚪 Salir",
            command=self.root.quit,
            **{**button_style, 'bg': '#95a5a6'}
        )
        btn_salir.pack(pady=15)
    
    def abrir_registro(self):
        RegistrationWindow(self.root)
    
    def abrir_deteccion(self):
        DetectionWindow(self.root)
    
    def abrir_reportes(self):
        ReportsWindow(self.root)
    
    def abrir_eliminar(self):
        """Abrir ventana simple para eliminar usuarios"""
        SimpleDeleteWindow(self.root)