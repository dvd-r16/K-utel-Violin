import argparse
import sys
import os
import time
import subprocess
import signal
import subprocess
import socket
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

from picamera2.devices.imx500.postprocess_highernet import postprocess_higherhrnet
import threading

SCRIPT_DIR = Path(__file__).resolve().parent


tick_count = 0
evaluar_tick = False
mostrar_color_resultado = False
color_resultado = (0, 0, 0, 0)
last_m_array = None  # Referencia al último frame para pintar
mostrar_tick_azul = False
cerrar_programa = False

tick_total = 0
evaluaciones_realizadas = 0
resultados = []


last_boxes = None
last_scores = None
last_keypoints = None
WINDOW_SIZE_H_W = (480, 640)

pygame.mixer.init()
sound_correct = pygame.mixer.Sound(str(SCRIPT_DIR / "Correct.wav"))
sound_incorrect = pygame.mixer.Sound(str(SCRIPT_DIR / "Incorrect.wav"))



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
    if last_m_array is not None:
        last_m_array[10:60, 70:120] = (255, 255, 255, 255)  # Limpiar resultado (cuadro 2)


def ai_output_tensor_draw(request: CompletedRequest, boxes, scores, keypoints, stream='main'):
    
    with MappedArray(request, stream) as m:
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
                        bueno = -args.margen_altura <= diferencia <= args.margen_altura
                        color_resultado = (0, 255, 0, 255) if bueno else (255, 0, 0, 255)
                        mostrar_color_resultado = True
                        resultados.append(bueno)
                        evaluaciones_realizadas += 1

                        if bueno:
                            sound_correct.play()
                        else:
                            sound_incorrect.play()

                        print(f"[EVAL] {'✔️ BUENO' if bueno else '❌ MALO'} | Evaluación #{evaluaciones_realizadas}/20")

                        if evaluaciones_realizadas >= 20:
                            print("[FIN] Se completaron 20 evaluaciones. Esperando instrucciones del proceso padre...")
                            global cerrar_programa
                            cerrar_programa = True
                            # Señal para el padre
                            with open("evaluaciones_completadas.flag", "w") as f:
                                f.write("done")




                    # Cuadro 3 – indicador visual de tick azul (parte inferior derecha)
                    if mostrar_tick_azul:
                        m.array[70:120, 70:120] = (0, 0, 255, 255)  # Azul
                    else:
                        m.array[70:120, 70:120] = (255, 255, 255, 255)  # Blanco


        if mostrar_color_resultado:
            m.array[10:60, 70:120] = color_resultado
            threading.Timer(1.5, borrar_color_resultado).start()        

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



