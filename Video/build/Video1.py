from pathlib import Path
import tkinter as tk
from tkinter import Canvas
import subprocess
import vlc
import time

# Rutas base
BASE_PATH = Path(__file__).resolve().parent.parent.parent
VIDEO_PATH = BASE_PATH / "Video" / "build" / "assets" / "frame0" / "Video01.mp4"
ANALISIS_PATH = BASE_PATH / "Camara" / "iniciar_analisis.py"

# Variables globales
vlc_player = None
instance = None
video_omitido = False

# Lanzar análisis
def lanzar_analisis_externo():
    try:
        subprocess.Popen(["python3", str(ANALISIS_PATH)])
        print("[INFO] Análisis de postura iniciado.")
    except Exception as e:
        print(f"[ERROR] Al lanzar análisis: {e}")

# Cierre del video + ejecución de análisis
def cerrar_ventana_y_lanzar_analisis():
    print("[INFO] Cerrando GUI e iniciando análisis...")
    lanzar_analisis_externo()
    root.after(1000, root.destroy)  # Espera 1 segundo antes de cerrar


# Omitir manualmente el video
def omitir_intro(event=None):
    global video_omitido, vlc_player
    if video_omitido:
        return
    video_omitido = True
    print("[EVENTO] Intro omitida.")
    if vlc_player:
        vlc_player.stop()
        vlc_player.release()
    canvas.delete("all")
    canvas.create_text(720, 450, text="⏩ Saltando intro...", fill="white", font=("Arial", 36, "bold"))
    root.after(1000, cerrar_ventana_y_lanzar_analisis)

# Cuando finaliza naturalmente el video
def on_video_final(event=None):  # <-- asegúrate de que esto acepte `event`
    print("[EVENTO] Video finalizado.")
    if not video_omitido:
        cerrar_ventana_y_lanzar_analisis()


# Reproducir video con VLC
def reproducir_video():
    global vlc_player, instance
    instance = vlc.Instance()
    media = instance.media_new(str(VIDEO_PATH))
    vlc_player = instance.media_player_new()
    vlc_player.set_media(media)
    vlc_player.set_xwindow(canvas.winfo_id())  # Para Linux (X11)

    # Callback al finalizar
    event_manager = vlc_player.event_manager()
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, on_video_final)

    vlc_player.play()

# Interfaz con Tkinter
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="#32457D")
canvas = Canvas(root, bg="#32457D", height=900, width=1440, bd=0, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Eventos para omitir
root.bind("<space>", omitir_intro)
root.bind("<Return>", omitir_intro)
root.bind("<Button-1>", omitir_intro)
root.bind("<KeyPress-q>", lambda e: root.destroy())  # Solo cerrar sin lanzar análisis

# Iniciar después de 1s
root.after(1000, reproducir_video)
root.mainloop()
