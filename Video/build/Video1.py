from pathlib import Path
import tkinter as tk
from tkinter import Canvas
import subprocess
import threading
import vlc
import sys
import os


# Rutas base
BASE_PATH = Path(__file__).resolve().parent.parent.parent
CAMARA_SCRIPT_PATH = BASE_PATH / "Camara" / "imx500_pose_estimation_higherhrnet_demo.py"
VIDEO_PATH = BASE_PATH / "Video" / "build" / "assets" / "frame0" / "Video01.mp4"
RESULT_GUI_PATH = BASE_PATH / "Results" / "build" / "Result.py"
METRONOMO_PATH = BASE_PATH / "Metronomo" / "Metronomo.py"
FLAG_PATH = BASE_PATH / "evaluaciones_completadas.flag"

# Variables globales
proceso_camara = None
metronomo_proceso = None
gui_lanzado = False
video_omitido = False
vlc_player = None
instance = None

def iniciar_metronomo():
    global metronomo_proceso
    try:
        metronomo_proceso = subprocess.Popen(["python3", str(METRONOMO_PATH)])
        print("[INFO] Metrónomo iniciado.")
    except Exception as e:
        print(f"[ERROR] No se pudo iniciar el metrónomo: {e}")

def detener_metronomo():
    global metronomo_proceso
    if metronomo_proceso:
        try:
            metronomo_proceso.terminate()
            metronomo_proceso.wait(timeout=5)
            print("[INFO] Metrónomo detenido.")
        except Exception as e:
            print(f"[ERROR] No se pudo detener el metrónomo: {e}")

def cerrar_todo():
    global proceso_camara, gui_lanzado, vlc_player

    print("[INFO] Cerrando todo...")

    # Detener metrónomo
    detener_metronomo()

    # Detener cámara
    if proceso_camara and proceso_camara.poll() is None:
        try:
            proceso_camara.terminate()
            proceso_camara.wait(timeout=5)
            print("[INFO] Cámara detenida.")
        except Exception as e:
            print(f"[ERROR] No se pudo detener la cámara: {e}")

    # Detener y liberar VLC
    if vlc_player:
        try:
            if vlc_player.is_playing():
                vlc_player.stop()
            vlc_player.release()
            print("[INFO] VLC detenido y liberado.")
        except Exception as e:
            print(f"[ERROR] No se pudo cerrar VLC: {e}")

    # Abrir resultados
    if not gui_lanzado:
        gui_lanzado = True
        print("[INFO] Abriendo GUI de resultados...")
        subprocess.Popen(["python3", str(RESULT_GUI_PATH)])

    # Forzar cierre total
    try:
        root.quit()
        root.destroy()
        print("[INFO] Tkinter cerrado correctamente.")
    except Exception as e:
        print(f"[ERROR] Al cerrar Tkinter: {e}")
    

    os._exit(0)  # 💥 Fuerza la terminación de todo el proceso, útil si algo queda colgado


def verificar_finalizacion():
    if FLAG_PATH.exists():
        print("[INFO] Evaluaciones completadas detectadas.")
        cerrar_todo()
    else:
        root.after(1000, verificar_finalizacion)

def lanzar_camara_y_gui():
    global proceso_camara
    proceso_camara = subprocess.Popen(["python3", str(CAMARA_SCRIPT_PATH)])
    iniciar_metronomo()
    verificar_finalizacion()

def omitir_intro(event=None):
    global video_omitido, vlc_player
    if video_omitido:
        return
    video_omitido = True
    print("[EVENTO] Intro omitida.")
    if vlc_player:
        vlc_player.stop()
        vlc_player.release()
        print("[INFO] VLC detenido y recursos liberados.")
    canvas.delete("all")  # Limpia la pantalla
    canvas.create_text(720, 450, text="⏩ Saltando intro...", fill="white", font=("Arial", 36, "bold"))
    root.after(1000, lanzar_camara_y_gui)

def reproducir_video():
    global vlc_player, instance
    instance = vlc.Instance()
    media = instance.media_new(str(VIDEO_PATH))
    vlc_player = instance.media_player_new()
    vlc_player.set_media(media)
    vlc_player.set_xwindow(canvas.winfo_id())  # ✅ para Linux (X11)
    vlc_player.play()

    def esperar_final():
        while not vlc_player.is_playing():
            pass
        while vlc_player.is_playing():
            if video_omitido:
                return
        if not video_omitido:
            if vlc_player:
                vlc_player.stop()
                vlc_player.release()
                print("[INFO] VLC detenido al finalizar video.")
            canvas.delete("all")
            lanzar_camara_y_gui()

    threading.Thread(target=esperar_final, daemon=True).start()

# Crear ventana Tkinter fullscreen
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="#32457D")
canvas = Canvas(root, bg="#32457D", height=900, width=1440, bd=0, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Eventos
root.bind("<space>", omitir_intro)
root.bind("<Return>", omitir_intro)
root.bind("<Button-1>", omitir_intro)
root.bind("<KeyPress-q>", lambda e: cerrar_todo())
root.protocol("WM_DELETE_WINDOW", cerrar_todo)

# Eliminar flag si quedó de ejecuciones pasadas
if FLAG_PATH.exists():
    FLAG_PATH.unlink()

# Iniciar reproducción después de 1 segundo (para que la GUI se prepare)
root.after(1000, reproducir_video)
root.mainloop()
