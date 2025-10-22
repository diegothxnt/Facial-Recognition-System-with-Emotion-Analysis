import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from datetime import datetime, timedelta
from modules.database import DatabaseManager
import json

class ReportsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Reportes y Estadísticas")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2c3e50')
        
        self.db = DatabaseManager()
        
        self.setup_ui()
        self.cargar_datos()
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Reportes y Estadísticas",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both')
        
        # Pestaña de estadísticas generales
        stats_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.notebook.add(stats_frame, text="Estadísticas Generales")
        
        # Pestaña de historial completo
        history_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.notebook.add(history_frame, text="Historial Completo")
        
        # Pestaña de análisis por persona
        person_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.notebook.add(person_frame, text="Análisis por Persona")
        
        self.setup_stats_tab(stats_frame)
        self.setup_history_tab(history_frame)
        self.setup_person_tab(person_frame)
    
    def setup_stats_tab(self, parent):
        # Frame para controles
        control_frame = tk.Frame(parent, bg='#2c3e50')
        control_frame.pack(fill='x', pady=10)
        
        # Selector de rango de fechas
        tk.Label(control_frame, text="Rango:", font=('Arial', 10), 
                bg='#2c3e50', fg='white').pack(side='left', padx=5)
        
        self.rango_var = tk.StringVar(value="7dias")
        rangos = [("Últimos 7 días", "7dias"), 
                 ("Último mes", "30dias"), 
                 ("Últimos 3 meses", "90dias"),
                 ("Todo el historial", "todo")]
        
        for text, value in rangos:
            tk.Radiobutton(control_frame, text=text, variable=self.rango_var,
                          value=value, command=self.actualizar_graficos,
                          bg='#2c3e50', fg='white', selectcolor='#34495e').pack(side='left', padx=5)
        
        # Frame para gráficos
        charts_frame = tk.Frame(parent, bg='#2c3e50')
        charts_frame.pack(expand=True, fill='both', pady=10)
        
        # Gráfico de distribución de emociones
        self.fig_emociones = plt.Figure(figsize=(8, 6))
        self.ax_emociones = self.fig_emociones.add_subplot(111)
        self.canvas_emociones = FigureCanvasTkAgg(self.fig_emociones, charts_frame)
        self.canvas_emociones.get_tk_widget().pack(side='left', fill='both', expand=True, padx=5)
        
        # Gráfico de actividad temporal
        self.fig_actividad = plt.Figure(figsize=(8, 6))
        self.ax_actividad = self.fig_actividad.add_subplot(111)
        self.canvas_actividad = FigureCanvasTkAgg(self.fig_actividad, charts_frame)
        self.canvas_actividad.get_tk_widget().pack(side='right', fill='both', expand=True, padx=5)
    
    def setup_history_tab(self, parent):
        # Frame para controles de historial
        control_frame = tk.Frame(parent, bg='#2c3e50')
        control_frame.pack(fill='x', pady=10)
        
        # Filtros
        tk.Label(control_frame, text="Filtrar por:", font=('Arial', 10),
                bg='#2c3e50', fg='white').pack(side='left', padx=5)
        
        self.filtro_persona_var = tk.StringVar(value="Todas")
        self.filtro_emocion_var = tk.StringVar(value="Todas")
        
        # Dropdown para personas
        personas = ["Todas"] + self.obtener_lista_personas()
        persona_dropdown = ttk.Combobox(control_frame, textvariable=self.filtro_persona_var,
                                       values=personas, state="readonly", width=15)
        persona_dropdown.pack(side='left', padx=5)
        
        # Dropdown para emociones
        emociones = ["Todas", "Felicidad", "Tristeza", "Enojo", "Sorpresa", "Neutral", "Miedo", "Disgusto"]
        emocion_dropdown = ttk.Combobox(control_frame, textvariable=self.filtro_emocion_var,
                                       values=emociones, state="readonly", width=15)
        emocion_dropdown.pack(side='left', padx=5)
        
        # Botón aplicar filtros
        btn_aplicar = tk.Button(control_frame, text="Aplicar Filtros",
                               command=self.aplicar_filtros,
                               bg='#3498db', fg='white', font=('Arial', 10))
        btn_aplicar.pack(side='left', padx=5)
        
        # Botón exportar
        btn_exportar = tk.Button(control_frame, text="Exportar CSV",
                                command=self.exportar_csv,
                                bg='#2ecc71', fg='white', font=('Arial', 10))
        btn_exportar.pack(side='left', padx=5)
        
        # Treeview para el historial
        columns = ('ID', 'Fecha', 'Hora', 'Persona', 'Emoción', 'Confianza')
        self.history_tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        self.history_tree.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.history_tree, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
    
    def setup_person_tab(self, parent):
        # Frame para selección de persona
        selection_frame = tk.Frame(parent, bg='#2c3e50')
        selection_frame.pack(fill='x', pady=10)
        
        tk.Label(selection_frame, text="Seleccionar persona:", font=('Arial', 12),
                bg='#2c3e50', fg='white').pack(side='left', padx=5)
        
        self.persona_seleccionada_var = tk.StringVar()
        personas = self.obtener_lista_personas()
        if personas:
            self.persona_seleccionada_var.set(personas[0])
        
        persona_dropdown = ttk.Combobox(selection_frame, textvariable=self.persona_seleccionada_var,
                                       values=personas, state="readonly", width=30)
        persona_dropdown.pack(side='left', padx=5)
        persona_dropdown.bind('<<ComboboxSelected>>', self.actualizar_grafico_persona)
        
        # Frame para gráficos de persona
        charts_frame = tk.Frame(parent, bg='#2c3e50')
        charts_frame.pack(expand=True, fill='both', pady=10)
        
        # Gráfico de emociones por persona
        self.fig_persona = plt.Figure(figsize=(10, 8))
        self.ax_persona = self.fig_persona.add_subplot(111)
        self.canvas_persona = FigureCanvasTkAgg(self.fig_persona, charts_frame)
        self.canvas_persona.get_tk_widget().pack(fill='both', expand=True)
    
    def cargar_datos(self):
        """Cargar datos iniciales"""
        self.actualizar_graficos()
        self.cargar_historial_completo()
        if self.obtener_lista_personas():
            self.actualizar_grafico_persona()
    
    def actualizar_graficos(self):
        """Actualizar los gráficos estadísticos"""
        try:
            # Obtener datos según el rango seleccionado
            datos = self.obtener_datos_estadisticos()
            
            # Limpiar gráficos
            self.ax_emociones.clear()
            self.ax_actividad.clear()
            
            # Gráfico de distribución de emociones
            emociones = list(datos['distribucion_emociones'].keys())
            conteos = list(datos['distribucion_emociones'].values())
            
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0', '#ffb3e6']
            self.ax_emociones.pie(conteos, labels=emociones, autopct='%1.1f%%', colors=colors)
            self.ax_emociones.set_title('Distribución de Emociones')
            
            # Gráfico de actividad temporal
            fechas = list(datos['actividad_temporal'].keys())
            conteos_actividad = list(datos['actividad_temporal'].values())
            
            self.ax_actividad.bar(fechas, conteos_actividad, color='#3498db')
            self.ax_actividad.set_title('Actividad de Detección por Día')
            self.ax_actividad.tick_params(axis='x', rotation=45)
            
            # Actualizar canvases
            self.fig_emociones.tight_layout()
            self.fig_actividad.tight_layout()
            self.canvas_emociones.draw()
            self.canvas_actividad.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los gráficos: {str(e)}")
    
    def actualizar_grafico_persona(self, event=None):
        """Actualizar gráfico para la persona seleccionada"""
        try:
            persona = self.persona_seleccionada_var.get()
            if not persona:
                return
            
            datos_persona = self.obtener_datos_persona(persona)
            
            self.ax_persona.clear()
            
            # Gráfico de emociones para la persona
            emociones = list(datos_persona.keys())
            conteos = list(datos_persona.values())
            
            bars = self.ax_persona.bar(emociones, conteos, color='#2ecc71')
            self.ax_persona.set_title(f'Distribución de Emociones - {persona}')
            self.ax_persona.tick_params(axis='x', rotation=45)
            
            # Añadir valores en las barras
            for bar, count in zip(bars, conteos):
                height = bar.get_height()
                self.ax_persona.text(bar.get_x() + bar.get_width()/2., height,
                                    f'{count}', ha='center', va='bottom')
            
            self.fig_persona.tight_layout()
            self.canvas_persona.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el gráfico de persona: {str(e)}")
    
    def obtener_datos_estadisticos(self):
        """Obtener datos estadísticos según el rango seleccionado"""
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # Determinar fecha límite según el rango
        if self.rango_var.get() == "7dias":
            fecha_limite = datetime.now() - timedelta(days=7)
        elif self.rango_var.get() == "30dias":
            fecha_limite = datetime.now() - timedelta(days=30)
        elif self.rango_var.get() == "90dias":
            fecha_limite = datetime.now() - timedelta(days=90)
        else:
            fecha_limite = datetime.min
        
        # Distribución de emociones
        cursor.execute('''
            SELECT emocion, COUNT(*) as count 
            FROM detecciones_emociones 
            WHERE datetime(timestamp) >= datetime(?)
            GROUP BY emocion
        ''', (fecha_limite,))
        
        distribucion_emociones = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Actividad temporal
        cursor.execute('''
            SELECT DATE(timestamp) as fecha, COUNT(*) as count
            FROM detecciones_emociones
            WHERE datetime(timestamp) >= datetime(?)
            GROUP BY DATE(timestamp)
            ORDER BY fecha DESC
            LIMIT 10
        ''', (fecha_limite,))
        
        actividad_temporal = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'distribucion_emociones': distribucion_emociones,
            'actividad_temporal': actividad_temporal
        }
    
    def obtener_datos_persona(self, persona_nombre):
        """Obtener datos de emociones para una persona específica"""
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT de.emocion, COUNT(*) as count
            FROM detecciones_emociones de
            JOIN personas p ON de.persona_id = p.id
            WHERE p.nombre || ' ' || p.apellido = ?
            GROUP BY de.emocion
        ''', (persona_nombre,))
        
        datos = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        return datos
    
    def obtener_lista_personas(self):
        """Obtener lista de todas las personas registradas"""
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT nombre, apellido FROM personas')
        personas = [f"{row[0]} {row[1]}" for row in cursor.fetchall()]
        conn.close()
        
        return personas
    
    def cargar_historial_completo(self):
        """Cargar todo el historial en el treeview"""
        historial = self.db.obtener_historial_emociones()
        
        # Limpiar treeview
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Cargar datos
        for registro in historial:
            fecha_hora = registro['timestamp'].split(' ')
            fecha = fecha_hora[0] if len(fecha_hora) > 0 else ''
            hora = fecha_hora[1] if len(fecha_hora) > 1 else ''
            
            self.history_tree.insert('', 'end', values=(
                registro.get('id', ''),
                fecha,
                hora,
                f"{registro['nombre']} {registro['apellido']}",
                registro['emocion'],
                f"{registro['confianza']:.1%}"
            ))
    
    def aplicar_filtros(self):
        """Aplicar filtros al historial"""
        # Esta función se implementaría para filtrar el treeview
        # según los criterios seleccionados
        messagebox.showinfo("Info", "Funcionalidad de filtros en desarrollo")
    
    def exportar_csv(self):
        """Exportar historial a CSV"""
        try:
            from datetime import datetime
            filename = f"reporte_emociones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            historial = self.db.obtener_historial_emociones()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Fecha,Hora,Persona,Emoción,Confianza\n")
                for registro in historial:
                    fecha_hora = registro['timestamp'].split(' ')
                    fecha = fecha_hora[0] if len(fecha_hora) > 0 else ''
                    hora = fecha_hora[1] if len(fecha_hora) > 1 else ''
                    
                    f.write(f"{fecha},{hora},{registro['nombre']} {registro['apellido']},"
                           f"{registro['emocion']},{registro['confianza']:.4f}\n")
            
            messagebox.showinfo("Éxito", f"Reporte exportado como: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte: {str(e)}")