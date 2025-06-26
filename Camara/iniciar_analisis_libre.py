import subprocess
import time
from pathlib import Path
import pygame
import threading
import os
import psutil

# Rutas base
BASE_PATH = Path(__file__).resolve().parent.parent
CAMARA_SCRIPT = BASE_PATH / "Camara" / "imx500_pose_estimation_higherhrnet_libre.py"
METRONOMO_SCRIPT = BASE_PATH / "Metronomo" / "Metronomo.py"
MENU_PATH = BASE_PATH / "Menu" / "build" / "gui.py"
FLAG_PERSONA = BASE_PATH / "persona_detectada_4.flag"
INTRO_AUDIO = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/4.Intro.wav"
AUDIO_POSICIONATE = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/0.Camara.wav"


# Eliminar flag anterior si existe
if FLAG_PERSONA.exists():
    try:
        FLAG_PERSONA.unlink()
        print("[INFO] Flag de persona previa eliminada.")
    except Exception as e:
        print(f"[WARN] No se pudo eliminar la flag previa: {e}")

def ventana_preview_activa():
    result = subprocess.run(["wmctrl", "-l"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return b"QtGlPreview" in result.stdout

def cerrar_proceso_imx500():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if "imx500_pose_estimation_higherhrnet_libre.py" in ' '.join(proc.info['cmdline']):
                print(f"[INFO] Cerrando proceso IMX500 con PID {proc.info['pid']}")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    print("[WARN] Proceso IMX500 no respondió. Forzando cierre.")
                    proc.kill()
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


def main():
    try:
        print("[INFO] Iniciando cámara en modo libre...")
        cam = subprocess.Popen(["python3", str(CAMARA_SCRIPT)])

        pygame.mixer.init()
        voz_posicionate = pygame.mixer.Sound(AUDIO_POSICIONATE)

        def repetir_posicionamiento():
            while not FLAG_PERSONA.exists():
                print("[AUDIO] Posiciónate frente a la cámara")
                voz_posicionate.play()
                time.sleep(5)

        threading.Thread(target=repetir_posicionamiento, daemon=True).start()

        print("[INFO] Esperando detección de persona...")
        while not FLAG_PERSONA.exists():
            time.sleep(0.5)

        print("[INFO] Persona detectada. Reproduciendo introducción...")
        pygame.mixer.music.load(INTRO_AUDIO)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        print("[INFO] Iniciando metrónomo...")
        metro = subprocess.Popen(
            ["python3", str(METRONOMO_SCRIPT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print("[INFO] Esperando a que la cámara finalice (Alt+F4)...")
        while ventana_preview_activa():
            if metro.poll() is not None:
                print("[WARN] El metrónomo se cerró inesperadamente.")
                break  # o relanzarlo si quieres
            time.sleep(1)

        print("[INFO] Cierre manual detectado. Cerrando metrónomo...")
        if metro and metro.poll() is None:
            metro.terminate()
            try:
                metro.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("[WARN] El metrónomo no respondió. Forzando cierre.")
                metro.kill()
        print("[INFO] Cierre de Imx500.py")
        cerrar_proceso_imx500()

        print("[INFO] Regresando al menú principal...")
        subprocess.Popen(["python3", str(MENU_PATH)])

    except Exception as e:
        print(f"[ERROR] Algo salió mal en el modo libre: {e}")

if __name__ == "__main__":
    main()
