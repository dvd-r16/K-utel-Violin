from pathlib import Path
from tkinter import Tk, Canvas
from moviepy import VideoFileClip
import threading
import subprocess

# Variables globales
proceso_camara = None
metronomo_proceso = None


def iniciar_metronomo():
    global metronomo_proceso
    metronomo_path = BASE_PATH / "Metronomo" / "Metronomo.py"
    try:
        metronomo_proceso = subprocess.Popen(["python3", str(metronomo_path)])
        print("[INFO] Metronomo iniciado.")
    except Exception as e:
        print(f"[ERROR] No se pudo iniciar el metronomo: {e}")

def detener_metronomo():
    global metronomo_proceso
    if metronomo_proceso is not None:
        try:
            metronomo_proceso.terminate()
            metronomo_proceso.wait(timeout=5)
            print("[INFO] Metronomo detenido correctamente.")
        except Exception as e:
            print(f"[ERROR] No se pudo detener el metronomo: {e}")

# Ruta base
BASE_PATH = Path(__file__).resolve().parent.parent.parent
CAMARA_SCRIPT_PATH = BASE_PATH / "Camara" / "imx500_pose_estimation_higherhrnet_demo.py"
VIDEO_PATH = BASE_PATH / "Video" / "build" / "assets" / "frame0" / "Video01.mp4"
RESULT_GUI_PATH = BASE_PATH / "Results" / "build" / "Result.py"

def reproducir_video():
    video = VideoFileClip(str(VIDEO_PATH))  # Convertir ruta a string por seguridad

    def cuando_termina(el_clip):
        global proceso_camara
        print("[INFO] Video terminado. Abriendo detección de pose...")

        # Lanzar script de cámara
        proceso_camara = subprocess.Popen(["python3", str(CAMARA_SCRIPT_PATH)])
        window.after(1000, verificar_finalizacion)
        
        def esperar_cierre():
            proceso_camara.wait()  # ⏳ Esperar que el script termine
            print("[INFO] Script de cámara finalizó.")
            cerrar_todo()  # 🔚 Aquí cerramos el metronomo y lanzamos gui.py

        # Correr en un hilo para no congelar el GUI
        threading.Thread(target=esperar_cierre, daemon=True).start()

        
    video.preview()
    cuando_termina(video)

    # Arrancar metrónomo unos segundos después
    window.after(5000, iniciar_metronomo)

gui_lanzado = False  # Al inicio del script

def cerrar_todo():
    global proceso_camara, gui_lanzado
    print("[INFO] Cerrando ventana principal...")
    detener_metronomo()

    if proceso_camara is not None and proceso_camara.poll() is None:
        try:
            proceso_camara.terminate()
            proceso_camara.wait(timeout=5)
        except Exception as e:
            print(f"[ERROR] No se pudo detener la cámara: {e}")
    
    if not gui_lanzado:
        gui_lanzado = True
        print("[INFO] Abriendo interfaz de resultados...")
        try:
            subprocess.Popen(["python3", str(RESULT_GUI_PATH)])
        except Exception as e:
            print(f"[ERROR] No se pudo abrir gui.py: {e}")

    window.destroy()
    window.quit()
    flag_path = BASE_PATH / "evaluaciones_completadas.flag"
    if flag_path.exists():
        flag_path.unlink()


# Crear ventana principal (fullscreen)
window = Tk()
window.attributes("-fullscreen", True)
window.geometry("1440x900")
window.configure(bg="#32457D")  # Fondo azul

canvas = Canvas(window, bg="#32457D", height=900, width=1440, bd=0, highlightthickness=0, relief="ridge")
canvas.pack(fill="both", expand=True)

window.bind("<KeyPress-q>", lambda e: cerrar_todo())

def verificar_finalizacion():
    flag_path = BASE_PATH / "evaluaciones_completadas.flag"
    if flag_path.exists():
        print("[INFO] Evaluaciones completadas detectadas por el padre.")
        cerrar_todo()
    else:
        window.after(1000, verificar_finalizacion)  # Revisa de nuevo en 1 segundo

# Vincular la acción de cerrar la ventana
window.protocol("WM_DELETE_WINDOW", cerrar_todo)

# Iniciar el video después de 3 segundos
window.after(3000, reproducir_video)

window.resizable(False, False)
window.mainloop()