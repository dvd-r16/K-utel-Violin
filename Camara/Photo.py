import time
import tkinter as tk
from PIL import Image, ImageTk
import datetime
from picamera2 import Picamera2
from libcamera import Transform
import os
from pathlib import Path

# Inicializar la cámara
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(transform=Transform(hflip=True))
picam2.configure(preview_config)
picam2.start()

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Captura de Imagen - Raspberry Pi")
ventana.geometry("500x500")
ventana.configure(bg="#203262")

# Crear canvas para superponer imagen y botón
canvas = tk.Canvas(ventana, width=480, height=480, highlightthickness=0, bg="#203262")
canvas.pack(pady=10)

# Imagen de video (inicializada como vacía)
imagen_id = canvas.create_image(0, 0, anchor=tk.NW)

# Función para actualizar el video con recorte cuadrado
def actualizar_video():
    frame = picam2.capture_array()
    h, w, _ = frame.shape
    size = min(h, w)
    start_x = (w - size) // 2
    start_y = (h - size) // 2
    frame_cuadrado = frame[start_y:start_y+size, start_x:start_x+size]

    imagen = Image.fromarray(frame_cuadrado)
    imagen = imagen.resize((480, 480))  # Mostrar en tamaño cuadrado
    imagen_tk = ImageTk.PhotoImage(imagen)

    canvas.imgtk = imagen_tk
    canvas.itemconfig(imagen_id, image=imagen_tk)
    ventana.after(30, actualizar_video)

# Función para capturar imagen y guardarla como cuadrado
def capturar():
    imagen = picam2.capture_array()
    h, w, _ = imagen.shape
    size = min(h, w)
    start_x = (w - size) // 2
    start_y = (h - size) // 2
    imagen_cuadrada = imagen[start_y:start_y+size, start_x:start_x+size]
    imagen_pil = Image.fromarray(imagen_cuadrada).resize((420, 420)).convert("RGB")


    # Leer usuario seleccionado
    base_path = Path(__file__).resolve().parent.parent  # Ir a K-utel-Violin/
    path_usuario = base_path / "usuario_seleccionado.txt"
    path_destino = base_path / "Login" / "usuarios"

    try:
        with open(path_usuario, "r") as f:
            numero_usuario = f.read().strip()
    except FileNotFoundError:
        print("⚠️ No se encontró usuario_seleccionado.txt")
        return

    # Construir ruta destino como user_X.jpeg
    nombre_archivo = f"user_{numero_usuario}.jpeg"
    ruta_completa = path_destino / nombre_archivo

    # Guardar imagen
    imagen_pil.save(ruta_completa)
    print(f"📸 Imagen guardada como: {ruta_completa}")

# Crear botón y colocarlo encima del canvas
boton_captura = tk.Button(ventana, text="📷 Capturar", command=capturar,
                          bg="#4CAF50", fg="white", font=("Arial", 12))

# Superponer botón en esquina inferior derecha del canvas
canvas.create_window(460, 460, window=boton_captura, anchor=tk.SE)

# Iniciar la actualización del video
actualizar_video()
ventana.mainloop()
