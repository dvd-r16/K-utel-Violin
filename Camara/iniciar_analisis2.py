import subprocess
import time
from pathlib import Path
import pygame
import threading

# Rutas base
BASE_PATH = Path(__file__).resolve().parent.parent
CAMARA_SCRIPT = BASE_PATH / "Camara" / "imx500_pose_estimation_higherhrnet_demo2.py"
METRONOMO_SCRIPT = BASE_PATH / "Metronomo" / "Metronomo.py"
RESULT_GUI_PATH = BASE_PATH / "Results" / "build" / "Result2.py"
FLAG_PATH = BASE_PATH / "evaluaciones_completadas_2.flag"
FLAG_PERSONA = BASE_PATH / "persona_detectada_2.flag"
INTRO_AUDIO = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/2.Intro.wav"
AUDIO_POSICIONATE = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/0.Camara.wav"

# Eliminar flag anterior si existe
if FLAG_PATH.exists():
    try:
        FLAG_PATH.unlink()
        print("[INFO] Flag anterior eliminada.")
    except Exception as e:
        print(f"[WARN] No se pudo eliminar la flag previa: {e}")

def reproducir_intro():
    try:
        print("[INFO] Reproduciendo introducción...")
        pygame.mixer.init()
        pygame.mixer.music.load(INTRO_AUDIO)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        print("[INFO] Introducción finalizada.")
    except Exception as e:
        print(f"[ERROR] No se pudo reproducir intro: {e}")

def main():
    try:
        if FLAG_PATH.exists():
            FLAG_PATH.unlink()
            print("[INFO] Flag de evaluación previa eliminada.")

        if FLAG_PERSONA.exists():
            FLAG_PERSONA.unlink()
            print("[INFO] Flag de persona previa eliminada.")

        print("[INFO] Iniciando cámara...")
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
        metro = subprocess.Popen(["python3", str(METRONOMO_SCRIPT)])

        print("[INFO] Esperando evaluaciones...")
        while not FLAG_PATH.exists():
            time.sleep(1)

        print("[INFO] Evaluaciones completadas detectadas.")

        # Intentar detener procesos si siguen vivos
        for proc, name in [(cam, "cámara"), (metro, "metrónomo")]:
            if proc and proc.poll() is None:
                print(f"[INFO] Deteniendo {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"[WARN] {name} no respondió. Forzando cierre.")
                    proc.kill()

        print("[INFO] Abriendo GUI de resultados...")
        subprocess.call(["python3", str(RESULT_GUI_PATH)])
        print("[INFO] GUI cerrada. Análisis completo.")

    except Exception as e:
        print(f"[ERROR] Algo salió mal en el análisis: {e}")

if __name__ == "__main__":
    main()
