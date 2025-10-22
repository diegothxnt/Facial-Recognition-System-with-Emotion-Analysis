import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from modules.database import DatabaseManager

class SimpleDeleteWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Eliminar Usuarios - Base de Datos")
        self.window.geometry("900x600")
        self.window.configure(bg='#2c3e50')
        
        self.db = DatabaseManager()
        
        self.setup_ui()
        self.cargar_usuarios()
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Gestión de Usuarios - Eliminar Registros",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de información
        info_frame = tk.Frame(main_frame, bg='#34495e', padx=10, pady=10)
        info_frame.pack(fill='x', pady=(0, 15))
        
        info_label = tk.Label(
            info_frame,
            text="Seleccione un usuario de la lista y haga clic en 'Eliminar' para borrarlo permanentemente",
            font=('Arial', 10),
            fg='#ecf0f1',
            bg='#34495e',
            wraplength=700
        )
        info_label.pack()
        
        # Frame para la tabla
        table_frame = tk.Frame(main_frame, bg='#34495e')
        table_frame.pack(expand=True, fill='both', pady=(0, 15))
        
        # Treeview para usuarios
        columns = ('ID', 'Nombre', 'Apellido', 'Email', 'Fecha Registro')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        # Configurar columnas
        column_widths = {
            'ID': 60, 
            'Nombre': 120, 
            'Apellido': 120, 
            'Email': 200, 
            'Fecha Registro': 150
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col], anchor='center')
        
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Frame de botones
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill='x')
        
        # Botón Eliminar
        btn_eliminar = tk.Button(
            button_frame,
            text="🗑️ ELIMINAR USUARIO SELECCIONADO",
            command=self.eliminar_usuario,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=25,
            height=2,
            relief='flat',
            cursor='hand2'
        )
        btn_eliminar.pack(side='left', padx=10)
        
        # Botón Actualizar
        btn_actualizar = tk.Button(
            button_frame,
            text="🔄 ACTUALIZAR LISTA",
            command=self.cargar_usuarios,
            bg='#3498db',
            fg='white',
            font=('Arial', 11),
            width=15,
            height=2,
            relief='flat',
            cursor='hand2'
        )
        btn_actualizar.pack(side='left', padx=10)
        
        # Botón Cerrar
        btn_cerrar = tk.Button(
            button_frame,
            text="CERRAR",
            command=self.window.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11),
            width=10,
            height=2,
            relief='flat',
            cursor='hand2'
        )
        btn_cerrar.pack(side='right', padx=10)
        
        # Etiqueta de estado
        self.status_label = tk.Label(
            main_frame,
            text="Cargando usuarios...",
            font=('Arial', 10),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        self.status_label.pack(pady=5)
    
    def cargar_usuarios(self):
        """Cargar lista de usuarios - CON DIAGNÓSTICO"""
        try:
            self.status_label.config(text="Buscando usuarios...")
            
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener diagnóstico primero
            diagnostico = self.db.diagnosticar_bd()
            print("🔍 Diagnóstico de BD:", diagnostico)
            
            # Obtener usuarios
            usuarios = self.db.obtener_todas_personas()
            
            if not usuarios:
                self.status_label.config(text="❌ No se encontraron usuarios")
                
                # Mostrar diagnóstico completo
                info = f"""
📊 DIAGNÓSTICO DE BASE DE DATOS:

Ruta: {diagnostico.get('ruta', 'N/A')}
Tablas: {', '.join(diagnostico.get('tablas', []))}
Conteos: {diagnostico.get('conteos', {})}

Posibles soluciones:
1. Verifica que hayas registrado personas
2. La base de datos podría estar en otra ubicación
3. Las tablas podrían tener nombres diferentes
                """
                messagebox.showinfo("Diagnóstico", info)
                return
            
            # Llenar treeview
            for usuario in usuarios:
                valores = [str(val) if val is not None else "" for val in usuario]
                self.tree.insert('', 'end', values=valores)
            
            self.status_label.config(text=f"✅ {len(usuarios)} usuarios cargados")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.status_label.config(text=f"❌ {error_msg}")
    
    def eliminar_usuario(self):
        """Eliminar usuario seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario de la lista para eliminar.")
            return
        
        item = seleccion[0]
        valores = self.tree.item(item, 'values')
        
        if not valores or len(valores) < 3:
            messagebox.showerror("Error", "No se pudieron obtener los datos del usuario seleccionado.")
            return
        
        usuario_id = valores[0]
        nombre = valores[1]
        apellido = valores[2]
        email = valores[3] if len(valores) > 3 else "N/A"
        
        nombre_completo = f"{nombre} {apellido}"
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "CONFIRMAR ELIMINACIÓN",
            f"¿Está seguro de que desea ELIMINAR permanentemente al usuario?\n\n"
            f"👤 Nombre: {nombre_completo}\n"
            f"📧 Email: {email}\n"
            f"🔢 ID: {usuario_id}\n\n"
            f"⚠️  ADVERTENCIA: Esta acción NO se puede deshacer.\n"
            f"Se eliminarán todos los datos del usuario incluyendo:\n"
            f"• Información personal\n• Embeddings faciales\n• Historial de detecciones"
        )
        
        if respuesta:
            try:
                success, mensaje = self.db.eliminar_persona(usuario_id)
                
                if success:
                    messagebox.showinfo("✅ Éxito", f"Usuario eliminado correctamente:\n{nombre_completo}")
                    self.cargar_usuarios()  # Recargar lista
                else:
                    messagebox.showerror("❌ Error", f"No se pudo eliminar el usuario:\n{mensaje}")
                    
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al eliminar usuario:\n{str(e)}")