# Sistema de Reconocimiento Facial con Análisis de Emociones

## Descripción del Proyecto
Sistema completo de reconocimiento facial y análisis de emociones en tiempo real desarrollado en Python. Permite registrar personas, reconocerlas en tiempo real y analizar sus emociones mediante IA.

## Características Principales

### Módulo de Registro
- Captura de rostros mediante cámara web
- Extracción y almacenamiento de embeddings faciales
- Registro de información personal (nombre, apellido, email)
- Validación de duplicados
- Vista previa de cámara en tiempo real

###Módulo de Reconocimiento
- Identificación de personas en tiempo real
- Clasificación de 7 emociones básicas:
  - 😊 Felicidad
  - 😢 Tristeza  
  - 😠 Enojo
  - 😲 Sorpresa
  - 😐 Neutral
  - 😨 Miedo
  - 🤢 Disgusto
- Mostrar nivel de confianza de cada predicción

###Módulo de Base de Datos
- Almacenamiento de registros de personas
- Histórico de detecciones emocionales
- Consultas y reportes avanzados
- Gestión completa de usuarios

###Interfaz Gráfica
- **Pantalla de Registro**: Formulario completo con vista de cámara
- **Pantalla de Detección**: Video en tiempo real con overlay de información
- **Pantalla de Reportes**: Gráficos y estadísticas
- **Gestión de Usuarios**: Eliminación y administración de registros

##Instalación y Configuración

###Requisitos del Sistema
- Python 3.6 o superior
- Cámara web
- 4GB RAM mínimo
- Windows 10/11 o Linux

###Instalación de Dependencias
```bash
pip install -r requirements.txt

###Ejecucion 
python main.py


Elaborado por Diego Rojas.
Materia: Inteligencia Artificial.
