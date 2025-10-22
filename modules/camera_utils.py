import cv2
import numpy as np

def inicializar_camara(indice_camara=0):
    """Inicializar la cámara web"""
    cap = cv2.VideoCapture(indice_camara)
    if not cap.isOpened():
        raise Exception("No se pudo inicializar la cámara")
    return cap

def capturar_rostros(cap, num_capturas=3):
    """Capturar múltiples rostros de la cámara"""
    capturas = []
    print("Capturando rostros... Mire directamente a la cámara.")
    
    for i in range(num_capturas):
        input(f"Presione Enter para capturar la imagen {i+1}/{num_capturas}...")
        ret, frame = cap.read()
        if ret:
            capturas.append(frame)
            print(f"Captura {i+1} completada")
        else:
            print("Error en la captura")
    
    return capturas

def preprocesar_imagen(imagen, tamaño=(224, 224)):
    """Preprocesar imagen para el modelo"""
    imagen = cv2.resize(imagen, tamaño)
    imagen = imagen.astype('float32') / 255.0
    return imagen

def dibujar_cuadrado_rostro(imagen, coordenadas, color=(0, 255, 0), grosor=2):
    """Dibujar un cuadrado alrededor del rostro"""
    top, right, bottom, left = coordenadas
    cv2.rectangle(imagen, (left, top), (right, bottom), color, grosor)
    return imagen

def añadir_texto_imagen(imagen, texto, posicion, color=(0, 255, 0), tamaño=0.7):
    """Añadir texto a una imagen"""
    cv2.putText(imagen, texto, posicion, cv2.FONT_HERSHEY_SIMPLEX, tamaño, color, 2)
    return imagen