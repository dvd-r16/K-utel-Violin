from pathlib import Path
from tkinter import Tk, Canvas
from moviepy import VideoFileClip
import subprocess

# Variables globales
proceso_camara = None

# Ruta base
BASE_PATH = Path(__file__).resolve().parent.parent.parent
CAMARA_SCRIPT_PATH = BASE_PATH / "Camara" / "imx500_pose_estimation_higherhrnet_demo3.py"
VIDEO_PATH = BASE_PATH / "Video" / "build" / "assets" / "frame0" / "video3.mp4"

def reproducir_video():
    video = VideoFileClip(str(VIDEO_PATH))  # Convertir ruta a string por seguridad

    def cuando_termina(el_clip):
        global proceso_camara
        print("[INFO] Video terminado. Abriendo detección de pose...")
        proceso_camara = subprocess.Popen(["python3", str(CAMARA_SCRIPT_PATH)])
        # ¡Ya no cerramos window aquí! Solo lanzamos la cámara

    video.preview()
    cuando_termina(video)

def cerrar_todo():
    global proceso_camara
    print("[INFO] Cerrando ventana principal...")
    if proceso_camara is not None:
        try:
            proceso_camara.terminate()
            proceso_camara.wait(timeout=5)
            print("[INFO] Proceso de cámara detenido correctamente.")
        except Exception as e:
            print(f"[ERROR] No se pudo detener la cámara: {e}")
    window.destroy()

# Crear ventana principal (fullscreen)
window = Tk()
window.attributes("-fullscreen", True)
window.geometry("1440x900")
window.configure(bg="#32457D")  # Fondo azul

canvas = Canvas(window, bg="#32457D", height=900, width=1440, bd=0, highlightthickness=0, relief="ridge")
canvas.pack(fill="both", expand=True)

# Vincular la acción de cerrar la ventana
window.protocol("WM_DELETE_WINDOW", cerrar_todo)

# Iniciar el video después de 3 segundos
window.after(3000, reproducir_video)

window.resizable(False, False)
window.mainloop()
