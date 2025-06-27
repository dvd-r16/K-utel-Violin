import subprocess
import time
from pathlib import Path
import pygame
import threading

# --- RUTAS ---
BASE_PATH = Path(__file__).resolve().parent.parent
CAMARA_SCRIPT = BASE_PATH / "Camara" / "imx500_pose_estimation_higherhrnet_demo3.py"
METRONOMO_SCRIPT = BASE_PATH / "Metronomo" / "Metronomo.py"
RESULT_GUI_PATH = BASE_PATH / "Results" / "build" / "Result3.py"

# --- FLAGS ---
FLAG_EVALUACION = BASE_PATH / "evaluaciones_completadas_3.flag"
FLAG_PERSONA = BASE_PATH / "persona_detectada_3.flag"
FLAG_PASO1 = BASE_PATH / "paso1_completado.flag"
FLAG_PASO2 = BASE_PATH / "paso2_completado.flag"
FLAG_PASO3 = BASE_PATH / "paso3_completado.flag"
FLAG_HABILITAR_PASO1 = BASE_PATH / "habilitar_paso1.flag"
FLAG_HABILITAR_PASO2 = BASE_PATH / "habilitar_paso2.flag"
FLAG_HABILITAR_PASO3 = BASE_PATH / "habilitar_paso3.flag"

# --- AUDIOS ---
AUDIO_CAMARA = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/0.Camara.wav"
AUDIO_INTRO = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/3.Intro.wav"
AUDIO_ADVER1 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/3.Adver.wav"
AUDIO_GOOD1 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/3.Good.wav"
AUDIO_INTRO2 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/3.Intro2.wav"
AUDIO_ADVER2 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/3.Adver.2.wav"
AUDIO_GOOD2 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/3.Good2.wav"
AUDIO_INTRO3 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/3.Intro3.wav"
AUDIO_ADVER3 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/3.Adver.3.wav"
AUDIO_INTRO4 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/3.Intro4.wav"

for f in [FLAG_EVALUACION, FLAG_PERSONA, FLAG_PASO1, FLAG_PASO2, FLAG_PASO3,
          FLAG_HABILITAR_PASO1, FLAG_HABILITAR_PASO2, FLAG_HABILITAR_PASO3]:
    if f.exists():
        try:
            f.unlink()
            print(f"[INFO] Flag eliminada: {f.name}")
        except Exception as e:
            print(f"[WARN] No se pudo eliminar {f.name}: {e}")

pygame.mixer.init()

def reproducir_loop(audio_path, detener_evento, intervalo=10):
    sonido = pygame.mixer.Sound(audio_path)
    while not detener_evento.is_set():
        sonido.play()
        time.sleep(intervalo)

def esperar_flag(path):
    while not path.exists():
        time.sleep(0.5)

def reproducir_audio(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def main():
    try:
        print("[INFO] Iniciando cámara...")
        cam = subprocess.Popen(["python3", str(CAMARA_SCRIPT)])

        # Esperar detección de persona
        voz_posicionate = pygame.mixer.Sound(AUDIO_CAMARA)
        def repetir_posicionamiento():
            while not FLAG_PERSONA.exists():
                print("[AUDIO] Posiciónate frente a la cámara")
                voz_posicionate.play()
                time.sleep(5)
        threading.Thread(target=repetir_posicionamiento, daemon=True).start()

        print("[INFO] Esperando detección de persona...")
        esperar_flag(FLAG_PERSONA)

        print("[INFO] Persona detectada. Reproduciendo Intro...")
        reproducir_audio(AUDIO_INTRO)

        # --- Paso 1 ---
        print("[ETAPA 1] Coloca el violín con mentón y mano izq...")
        stop1 = threading.Event()
        threading.Thread(target=reproducir_loop, args=(AUDIO_ADVER1, stop1), daemon=True).start()
        FLAG_HABILITAR_PASO1.write_text("go")
        esperar_flag(FLAG_PASO1)
        stop1.set()
        pygame.mixer.Sound(str(AUDIO_GOOD1)).play()
        time.sleep(1)
        reproducir_audio(AUDIO_INTRO2)

        # --- Paso 2 ---
        print("[ETAPA 2] Agarre correcto con pulgar e índice...")
        stop2 = threading.Event()
        threading.Thread(target=reproducir_loop, args=(AUDIO_ADVER2, stop2), daemon=True).start()
        FLAG_HABILITAR_PASO2.write_text("go")
        esperar_flag(FLAG_PASO2)
        stop2.set()
        pygame.mixer.Sound(str(AUDIO_GOOD2)).play()
        time.sleep(1)
        reproducir_audio(AUDIO_INTRO3)

        # --- Paso 3 ---
        print("[ETAPA 3] Coloca el arco sobre las cuerdas...")
        stop3 = threading.Event()
        threading.Thread(target=reproducir_loop, args=(AUDIO_ADVER3, stop3), daemon=True).start()
        FLAG_HABILITAR_PASO3.write_text("go")
        esperar_flag(FLAG_PASO3)
        stop3.set()
        reproducir_audio(AUDIO_INTRO4)

        FLAG_POS_CODO = BASE_PATH / "guardar_posicion_codo.flag"
        FLAG_POS_CODO.write_text("go")
        print("[FLAG] Se indicó guardar la posición del codo izquierdo.")

        # --- Iniciar metrónomo y evaluación ---
        print("[INFO] Iniciando metrónomo y evaluación...")
        metro = subprocess.Popen(["python3", str(METRONOMO_SCRIPT)])
        esperar_flag(FLAG_EVALUACION)
        print("[INFO] Evaluaciones completadas.")

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
        print(f"[ERROR] Algo salió mal: {e}")

if __name__ == "__main__":
    main()
