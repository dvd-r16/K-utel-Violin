import argparse
import sys
import os
import time
import subprocess
import signal
import socket
import requests
import numpy as np
from libcamera import Transform
from picamera2 import CompletedRequest, MappedArray, Picamera2
from picamera2.devices.imx500 import IMX500, NetworkIntrinsics
from picamera2.devices.imx500.postprocess import COCODrawer
from pathlib import Path
import picamera2.devices.imx500.postprocess as pp
print(pp.__file__)
import pyaudio
import numpy as np
import pygame
from PIL import Image, ImageTk
from tkinter import PhotoImage 

from picamera2.devices.imx500.postprocess_highernet import postprocess_higherhrnet
import threading

SCRIPT_DIR = Path(__file__).resolve().parent
# Ruta base
ASSETS_PATH = SCRIPT_DIR


tick_count = 0
evaluar_tick = False
mostrar_color_resultado = False
color_resultado = (0, 0, 0, 0)
last_m_array = None  # Referencia al último frame para pintar
mostrar_tick_azul = False
cerrar_programa = False
temporizador_activo = False

tick_total = 0
evaluaciones_realizadas = 0
resultados = []


last_boxes = None
last_scores = None
last_keypoints = None
WINDOW_SIZE_H_W = (480, 640)

ARDUINO_URL = "http://192.168.4.1"  # Cambia si es necesario

estado_imu = "Desconocido"

BASE_PATH = Path(__file__).resolve().parent.parent
USER_SELECTED_PATH = BASE_PATH / "usuario_seleccionado.txt"
USERS_PATH = BASE_PATH / "Login" / "usuarios"


pygame.mixer.init()
sound_correct = pygame.mixer.Sound(str(SCRIPT_DIR / "Correct.wav"))
sound_incorrect = pygame.mixer.Sound(str(SCRIPT_DIR / "Incorrect.wav"))

def cargar_imagen(path, size=(50, 50)):
    return np.array(Image.open(ASSETS_PATH / path).resize(size).convert("RGBA"))

# Imágenes para los cuadros
imagen_idle = cargar_imagen("Idle.png")
imagen_correcto = cargar_imagen("Correct.png")
imagen_incorrecto = cargar_imagen("Incorrect.png")
imagen_tick_on = cargar_imagen("Tick_on.png")
imagen_tick_off = cargar_imagen("Tick_off.png")

def pegar_imagen_en_array(m_array, imagen_np, x, y):
    h, w = imagen_np.shape[:2]
    m_array[y:y+h, x:x+w] = imagen_np

def obtener_estado_imu():
    global estado_imu
    try:
        res = requests.get(f"{ARDUINO_URL}/estado", timeout=0.5)
        texto = res.text.strip()
        estado_imu = texto
        print("[IMU]", estado_imu)  # <-- Aquí
    except:
        estado_imu = "Error de conexión"

    if "correcta" in estado_imu.lower():
        print("[DECISIÓN] Cuadro 1 = VERDE")
    elif "incorrecta" in estado_imu.lower():
        print("[DECISIÓN] Cuadro 1 = ROJO")
    else:
        print("[DECISIÓN] Cuadro 1 = GRIS/Blanco")



def ai_output_tensor_parse(metadata: dict):
    
    global last_boxes, last_scores, last_keypoints
    np_outputs = imx500.get_outputs(metadata=metadata, add_batch=True)
    if np_outputs is not None:
        keypoints, scores, boxes = postprocess_higherhrnet(outputs=np_outputs,
                                                           img_size=WINDOW_SIZE_H_W,
                                                           img_w_pad=(0, 0),
                                                           img_h_pad=(0, 0),
                                                           detection_threshold=args.detection_threshold,
                                                           network_postprocess=True)

        if scores is not None and len(scores) > 0:
            last_keypoints = np.reshape(np.stack(keypoints, axis=0), (len(scores), 17, 3))
            last_boxes = [np.array(b) for b in boxes]
            last_scores = np.array(scores)
    return last_boxes, last_scores, last_keypoints

def borrar_color_resultado():
    global mostrar_color_resultado, last_m_array
    mostrar_color_resultado = False
    temporizador_activo = False
    if last_m_array is not None:
        last_m_array[10:60, 70:120] = (255, 255, 255, 255)  # Limpiar resultado (cuadro 2)


def ai_output_tensor_draw(request: CompletedRequest, boxes, scores, keypoints, stream='main'):
    
    with MappedArray(request, stream) as m:
        # Cuadro 1 – IMU (arriba izquierda)
        if "posicion correcta" in estado_imu.lower():
            m.array[10:60, 10:60] = (0, 255, 0, 255)  # Verde
        elif "posicion incorrecta (horizontal)" in estado_imu.lower():
            m.array[10:60, 10:60] = (255, 0, 0, 255)  # Rojo
        else:
            m.array[10:60, 10:60] = (255, 255, 255, 255)  # Blanco si no hay info aún
        if boxes is not None and len(boxes) > 0:
            drawer.annotate_image(m.array, boxes, scores,
                                  np.zeros(scores.shape), keypoints, args.detection_threshold,
                                  args.detection_threshold, request.get_metadata(), picam2, stream)
            global last_m_array, evaluar_tick, color_resultado, mostrar_color_resultado
            global evaluaciones_realizadas, resultados

            last_m_array = m.array  # Guardamos referencia al frame actual

            for person in keypoints:
                shoulder = person[6]
                elbow = person[8]
                wrist = person[10]

                if (shoulder[2] > args.detection_threshold and
                    elbow[2] > args.detection_threshold and
                    wrist[2] > args.detection_threshold):

                    # Evaluar si la muñeca está a la misma altura (coordenada Y) que el hombro
                    altura_hombro = shoulder[1]
                    altura_muneca = wrist[1]
                    diferencia = altura_hombro - altura_muneca  # positivo si muñeca está más arriba
                    if evaluar_tick:
                        evaluar_tick = False
                        postura_correcta = -args.margen_altura <= diferencia <= args.margen_altura
                        imu_correcto = "correcta" in estado_imu.lower()

                        if postura_correcta and imu_correcto:
                            puntuacion = 1
                        elif postura_correcta or imu_correcto:
                            puntuacion = 0.5
                        else:
                            puntuacion = 0

                        color_resultado = (0, 255, 0, 255) if puntuacion >= 0.5 else (255, 0, 0, 255)
                        mostrar_color_resultado = True
                        resultados.append(puntuacion)
                        evaluaciones_realizadas += 1

                        if puntuacion == 1:
                            sound_correct.play()
                        else:
                            sound_incorrect.play()

                        if puntuacion == 1:
                            estado_eval = "✔️ EXCELENTE"
                        elif puntuacion == 0.5:
                            estado_eval = "➖ ACEPTABLE"
                        else:
                            estado_eval = "❌ INCORRECTO"
                        print(f"[EVAL] {estado_eval} | Evaluación #{evaluaciones_realizadas}/20")
                        if evaluaciones_realizadas >= 20:
                            registrar_resultado(leccion_idx=1, aciertos=resultados.count(True))  # Lección 2
                            distribuir_puntos_en_txt(leccion_idx=1, aciertos=resultados.count(True))
                            print("[FIN] Se completaron 20 evaluaciones. Esperando instrucciones del proceso padre...")
                            global cerrar_programa
                            cerrar_programa = True
                            # Señal para el padre
                            with open("evaluaciones_completadas.flag", "w") as f:
                                f.write("done")
                    global temporizador_activo
                    if mostrar_color_resultado:
                        imagen_a_usar = imagen_correcto if color_resultado == (0, 255, 0, 255) else imagen_incorrecto
                        if not temporizador_activo:
                            temporizador_activo = True
                            threading.Timer(1.5, borrar_color_resultado).start()
                    else:
                        imagen_a_usar = imagen_idle

                    pegar_imagen_en_array(m.array, imagen_a_usar, x=70, y=10)




                    # Cuadro 3 – indicador visual de tick azul (parte inferior derecha)
                    imagen_tick = imagen_tick_on if mostrar_tick_azul else imagen_tick_off
                    pegar_imagen_en_array(m.array, imagen_tick, x=70, y=70)
       

def activar_cuadro_tick():
    global mostrar_tick_azul
    mostrar_tick_azul = True
    def desactivar_tick():
        global mostrar_tick_azul
        time.sleep(0.2)
        mostrar_tick_azul = False
    threading.Thread(target=desactivar_tick, daemon=True).start()



def picamera2_pre_callback(request: CompletedRequest):
    boxes, scores, keypoints = ai_output_tensor_parse(request.get_metadata())
    ai_output_tensor_draw(request, boxes, scores, keypoints)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, help="Path of the model",
                        default="/usr/share/imx500-models/imx500_network_higherhrnet_coco.rpk")
    parser.add_argument("--fps", type=int, help="Frames per second")
    parser.add_argument("--detection-threshold", type=float, default=0.2,
                        help="Post-process detection threshold")
    parser.add_argument("--labels", type=str,
                        help="Path to the labels file")
    parser.add_argument("--print-intrinsics", action="store_true",
                        help="Print JSON network_intrinsics then exit")
    parser.add_argument("--margen-altura", type=int, default=20,
                    help="Margen permitido en diferencia de altura entre hombro y muñeca")

    return parser.parse_args()


def get_drawer():
    categories = intrinsics.labels
    categories = [c for c in categories if c and c != "-"]
    return COCODrawer(categories, imx500, needs_rescale_coords=False)


CHUNK = 1024
RATE = 44100
THRESHOLD = 500  # Ajustar según el volumen del tick

def audio_monitor():
    global tick_count, evaluar_tick
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("[AUDIO] Iniciando monitoreo de ticks...")

    try:
        while True:
            data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
            peak = np.abs(data).max()
            if peak > THRESHOLD:
                tick_count += 1
                print(f"[TICK] Detectado #{tick_count} con pico: {peak}")
                activar_cuadro_tick()
                if tick_count >= 4:
                    evaluar_tick = True
                    tick_count = 0
            time.sleep(0.05)
    except Exception as e:
        print(f"[ERROR] Monitoreo de audio: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        
def manejar_terminacion(signum, frame):
    print("[SEÑAL] Terminación recibida, limpiando cámara...")
    detener_componentes()
    sys.exit(0)

def detener_componentes():
    try:
        picam2.stop()
    except Exception as e:
        print(f"[WARN] Error al detener picam2: {e}")
    try:
        imx500.stop_network_task()
    except Exception as e:
        print(f"[WARN] Error al detener red neuronal: {e}")

def socket_tick_listener():
    global tick_count, evaluar_tick, tick_total, cerrar_programa
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(1)
    print("[SOCKET] Esperando conexión del metrónomo...")
    conn, _ = server_socket.accept()
    print("[SOCKET] Conectado al metrónomo.")

    try:
        while not cerrar_programa:
            data = conn.recv(1024)
            if not data:
                break
            if b"tick" in data:
                tick_count += 1
                print(f"[TICK] Señal recibida #{tick_count}")
                activar_cuadro_tick()
                if tick_count >= 4:
                    tick_count = 0
                    evaluar_tick = True
                    tick_total += 4
                    print(f"[TICK] Total acumulado: {tick_total}")
    except Exception as e:
        print(f"[ERROR] Socket tick listener: {e}")
    finally:
        conn.close()
        server_socket.close()

def registrar_resultado(leccion_idx, aciertos):
    from datetime import datetime
    import csv

    try:
        with open(USER_SELECTED_PATH, 'r') as f:
            user_id = f.read().strip()
        csv_file = USERS_PATH / f"user_{user_id}.csv"

        valor = round((aciertos / 20) * 10, 2)
        intento = 1
        if csv_file.exists():
            with open(csv_file, 'r') as f:
                reader = list(csv.DictReader(f))
                if reader:
                    ultimos = [int(r["intento"]) for r in reader if r["leccion"] == f"Lección {leccion_idx + 1}"]
                    intento = max(ultimos) + 1

        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if csv_file.stat().st_size == 0:
                writer.writerow(["leccion", "intento", "valor", "fecha"])
            writer.writerow([f"Lección {leccion_idx + 1}", intento, valor, datetime.now().isoformat()])
        print(f"[CSV] Resultado registrado: Lección {leccion_idx + 1}, Valor: {valor}")
    except Exception as e:
        print(f"[ERROR] Al guardar resultado en CSV: {e}")

def distribuir_puntos_en_txt(leccion_idx, aciertos):
    try:
        with open(USER_SELECTED_PATH, 'r') as f:
            user_id = f.read().strip()
        user_file = USERS_PATH / f"user_{user_id}.txt"

        with open(user_file, 'r', encoding='utf-8') as f:
            lineas = f.readlines()

        progreso_encontrado = False
        for i, linea in enumerate(lineas):
            if linea.startswith(f"Lección {leccion_idx + 1}:"):
                progreso_encontrado = True
                partes = linea.strip().split(":")
                valores = list(map(int, partes[1].strip().split(",")))

                nuevo_puntaje = round((aciertos / 20) * 4)
                indices_a_actualizar = [0, 1, 2, 3, 5]  # Brazo izq, hombro, cuello, brazo der, violin

                for idx in indices_a_actualizar:
                    valores[idx] = max(valores[idx], nuevo_puntaje)

                lineas[i] = f"Lección {leccion_idx + 1}: {','.join(map(str, valores))}\n"
                break

        if progreso_encontrado:
            with open(user_file, 'w', encoding='utf-8') as f:
                f.writelines(lineas)
            print(f"[TXT] Progreso actualizado con valor máximo en Lección {leccion_idx + 1}")
        else:
            print("[WARN] No se encontró la lección para actualizar.")
    except Exception as e:
        print(f"[ERROR] Al actualizar progreso en TXT: {e}")


if __name__ == "__main__":
    args = get_args()
    signal.signal(signal.SIGTERM, manejar_terminacion)


    try:
        imx500 = IMX500(args.model)
        intrinsics = imx500.network_intrinsics
        if not intrinsics:
            intrinsics = NetworkIntrinsics()
            intrinsics.task = "pose estimation"
        elif intrinsics.task != "pose estimation":
            print("Network is not a pose estimation task", file=sys.stderr)
            exit()

        for key, value in vars(args).items():
            if key == 'labels' and value is not None:
                with open(value, 'r') as f:
                    intrinsics.labels = f.read().splitlines()
            elif hasattr(intrinsics, key) and value is not None:
                setattr(intrinsics, key, value)

        if intrinsics.inference_rate is None:
            intrinsics.inference_rate = 10
        if intrinsics.labels is None:
            with open("assets/coco_labels.txt", "r") as f:
                intrinsics.labels = f.read().splitlines()
        intrinsics.update_with_defaults()

        if args.print_intrinsics:
            print(intrinsics)
            exit()

        drawer = get_drawer()

        picam2 = Picamera2(imx500.camera_num)
        config = picam2.create_preview_configuration(
            controls={'FrameRate': intrinsics.inference_rate},
            buffer_count=12,
            transform=Transform(hflip=True, vflip=False)
        )

        imx500.show_network_fw_progress_bar()
        picam2.start(config, show_preview=True)
        time.sleep(1.5)
        # Forzar fullscreen de la ventana más reciente (asumimos que es la del preview)
        subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,fullscreen"])
        imx500.set_auto_aspect_ratio()
        picam2.pre_callback = picamera2_pre_callback
        threading.Thread(target=socket_tick_listener, daemon=True).start()

        from threading import Thread

        def hilo_estado_imu():
            while True:
                obtener_estado_imu()
                time.sleep(0.5)

        Thread(target=hilo_estado_imu, daemon=True).start()

        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[INFO] Interrupción recibida, cerrando...")
    finally:
        print("[INFO] Deteniendo cámara...")
        try:
            picam2.stop()
        except Exception as e:
            print(f"[WARN] No se pudo detener picam2: {e}")
        
        try:
            imx500.stop_network_task()
        except Exception as e:
            print(f"[WARN] No se pudo detener red neuronal: {e}")
        
        print("[INFO] Programa finalizado correctamente.")