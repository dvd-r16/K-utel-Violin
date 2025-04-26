from pathlib import Path
from tkinter import Tk, Canvas
from moviepy import VideoFileClip
import subprocess

# Ruta al script que quieres lanzar después
BASE_PATH = Path(__file__).resolve().parent.parent.parent  # Subir hasta K-utel-Violin
CAMARA_SCRIPT_PATH = BASE_PATH / "Camara" / "imx500_pose_estimation_higherhrnet_demo2.py"
# Ruta del video
VIDEO_PATH = BASE_PATH / "Video" / "build" / "assets" / "frame0" / "video2.mp4"

# Función para reproducir video con audio
def reproducir_video():
    video = VideoFileClip(VIDEO_PATH)

    # Función que se llamará cuando termine el video
    def cuando_termina(el_clips):
        print("[INFO] Video terminado. Abriendo detección de pose...")
        subprocess.Popen(["python", str(CAMARA_SCRIPT_PATH)])
        window.destroy()

    # Asociar el final del video a la función cuando_termina
    video.preview()
    cuando_termina(video)

# Crear ventana principal (fullscreen)
window = Tk()
window.attributes("-fullscreen", True)
window.geometry("1440x900")
window.configure(bg="#32457D")

canvas = Canvas(window, bg="#32457D", height=900, width=1440, bd=0, highlightthickness=0, relief="ridge")
canvas.pack(fill="both", expand=True)

# Iniciar el video después de 3 segundos
window.after(3000, reproducir_video)

window.resizable(False, False)
window.mainloop()
