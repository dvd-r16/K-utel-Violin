import argparse
import sys
import os
import time
import subprocess
import signal
import random
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
MODO_SIMULACION_IMU = False  # Cambia a False cuando uses el IMU real

tick_total = 0
evaluaciones_realizadas = 0
resultados = []
MARGEN_CODO = 20
posicion_codo_inicial = None

last_boxes = None
last_scores = None
last_keypoints = None
WINDOW_SIZE_H_W = (480, 640)

ARDUINO_URL = "http://192.168.4.1"  # Cambia si es necesario

estado_imu = "Desconocido"
estado_imu1 = "Desconocido"
estado_imu2 = "Desconocido"

BASE_PATH = Path(__file__).resolve().parent.parent
USER_SELECTED_PATH = BASE_PATH / "usuario_seleccionado.txt"
USERS_PATH = BASE_PATH / "Login" / "usuarios"
VENV_PYTHON = "/home/dvdr/Documentos/K-utel-Violin/Kutelenv/bin/python"
RESULT_GUI_PATH = BASE_PATH / "Results" / "build" / "Result3.py"
FLAG_PERSONA = BASE_PATH / "persona_detectada_3.flag"
FLAG_PASO1 = BASE_PATH / "paso1_completado.flag"
FLAG_PASO2 = BASE_PATH / "paso2_completado.flag"
FLAG_PASO3 = BASE_PATH / "paso3_completado.flag"
FLAG_EVALUACION = BASE_PATH / "evaluaciones_completadas_3.flag"

FLAG_HABILITAR_PASO1 = BASE_PATH / "habilitar_paso1.flag"
FLAG_HABILITAR_PASO2 = BASE_PATH / "habilitar_paso2.flag"
FLAG_HABILITAR_PASO3 = BASE_PATH / "habilitar_paso3.flag"

FLAG_POS_CODO = BASE_PATH / "guardar_posicion_codo.flag"


# Eliminar flags anteriores al inicio
for flag in [FLAG_PERSONA, FLAG_PASO1, FLAG_PASO2, FLAG_PASO3, FLAG_EVALUACION, FLAG_POS_CODO]:
    if flag.exists():
        try:
            flag.unlink()
            print(f"[INFO] Flag eliminada: {flag.name}")
        except Exception as e:
            print(f"[WARN] No se pudo eliminar {flag.name}: {e}")

#Audios de correcion - Error unico
AUDIO_SUBIR = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.LowViolin.wav" #Altura1 (subir)
AUDIO_BAJAR = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.HighViolin.wav" #Altura2 (bajar)
AUDIO_AGARRE = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.palma2.wav" #Agarre (Imu1)
#AUDIO_MAL_ABAJO = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.MunyAlV.wav" #Ignorar
#AUDIO_MAL_ARRIBA = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.MunyBaV.wav" #Ignorar
AUDIO_ARCO = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.Arco.wav" #Arco (Imu2)
#AUDIO_ARCO_DESLIZ = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.Deslizar.wav"
#AUDIO_ARCO_MUN = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.Muneca.wav"
#Error Doble
AUDIO_E21 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.AgArc.wav" #Agarre y Arco (Imu1+Imu2)
AUDIO_E22 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.AltAg.wav" #Altura y agarre (Camara + Imu1)
AUDIO_E23 = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.AltArc.wav" #Alura y Arco (camara + Imu2)
#Error Total
AUDIO_MAL = "/home/dvdr/Documentos/K-utel-Violin/Maestro/Lyra/Error.Total.wav" #Todos mal

pygame.mixer.init()
sound_correct = pygame.mixer.Sound(str(SCRIPT_DIR / "Correct.wav"))
sound_incorrect = pygame.mixer.Sound(str(SCRIPT_DIR / "Incorrect.wav"))
#Voces de correccion
sound_subir = pygame.mixer.Sound(AUDIO_SUBIR)
sound_bajar = pygame.mixer.Sound(AUDIO_BAJAR)
sound_agarre_mal = pygame.mixer.Sound(AUDIO_AGARRE)
sound_arco = pygame.mixer.Sound(AUDIO_ARCO)
#Error Doble
sound_agarre_arco = pygame.mixer.Sound(AUDIO_E21)
sound_altura_agarre = pygame.mixer.Sound(AUDIO_E22)
sound_altura_arco = pygame.mixer.Sound(AUDIO_E23)
#Error Triple - Completo
sound_todo_mal = pygame.mixer.Sound(AUDIO_MAL)

def cargar_imagen(path, size=(50, 50)):
    return np.array(Image.open(ASSETS_PATH / path).resize(size).convert("RGBA"))

# Imágenes para los cuadros
imagen_idle = cargar_imagen("Idle.png")              # Postura (altura)
imagen_correcto = cargar_imagen("Correct.png")
imagen_incorrecto = cargar_imagen("Incorrect.png")

imagen_idle2 = cargar_imagen("Idle2.png")            # IMU1
imagen_correcto2 = cargar_imagen("Correct2.png")
imagen_incorrecto2 = cargar_imagen("Incorrect2.png")

imagen_idle3 = cargar_imagen("Idle3.png")            # IMU2
imagen_correcto3 = cargar_imagen("Correct3.png")
imagen_incorrecto3 = cargar_imagen("Incorrect3.png")

imagen_tick_on = cargar_imagen("Tick_on.png") #Pulsos
imagen_tick_off = cargar_imagen("Tick_off.png")

def pegar_imagen_en_array(m_array, imagen_np, x, y):
    h, w = imagen_np.shape[:2]
    m_array[y:y+h, x:x+w] = imagen_np

def obtener_estado_imu():
    global estado_imu, estado_imu1

    # Evaluar el estado del codo con keypoints
    codo_estado = "desconocido"
    if posicion_codo_inicial is not None and last_keypoints is not None:
        for person in last_keypoints:
            left_elbow = person[7]
            if left_elbow[2] > args.detection_threshold:
                x, y = left_elbow[0], left_elbow[1]
                x0, y0 = posicion_codo_inicial
                dentro_margen = abs(x - x0) <= MARGEN_CODO and abs(y - y0) <= MARGEN_CODO
                codo_estado = "good" if dentro_margen else "bad"
                break
    else:
        codo_estado = "desconocido"

    # Construir la URL incluyendo el estado del codo como parámetro
    url = f"{ARDUINO_URL}/estado"
    if codo_estado in ["good", "bad"]:
        url += f"?led2={codo_estado}"

    try:
        res = requests.get(url, timeout=0.5)
        texto = res.text.strip()
        estado_imu = texto  # respuesta completa

        lineas = texto.splitlines()
        if len(lineas) >= 2:
            estado = lineas[1].strip().lower()
            if "bien" in estado:
                estado_imu1 = "bien"
            elif "mal" in estado:
                estado_imu1 = "mal"
            else:
                estado_imu1 = "desconocido"
        else:
            estado_imu1 = "desconocido"
    except:
        estado_imu = "Error de conexión"
        estado_imu1 = "error"

    print(f"[IMU] IMU1 = {estado_imu1.upper()} | Codo = {codo_estado.upper()}")


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
    global estado_imu, estado_imu1, estado_imu2
    global posicion_codo_inicial, estado_codo_anterior, ultimo_envio_codo
    global estado_agarre_anterior, ultimo_envio_agarre
    with MappedArray(request, stream) as m:
        # Cuadro 1 – IMU (arriba izquierda)
        if "bien" in estado_imu1.lower():
            pegar_imagen_en_array(m.array, imagen_correcto2, x=10, y=10)
            nuevo_estado_agarre = "good"
        elif "mal" in estado_imu1.lower():
            pegar_imagen_en_array(m.array, imagen_incorrecto2, x=10, y=10)
            nuevo_estado_agarre = "bad"
        else:
            pegar_imagen_en_array(m.array, imagen_idle2, x=10, y=10)
            nuevo_estado_agarre = None

        
        # Cuadro 2 – IMU2 (abajo izquierda)
        if posicion_codo_inicial is not None and last_keypoints is not None:
            for person in last_keypoints:
                left_elbow = person[7]
                if left_elbow[2] > args.detection_threshold:
                    x, y = left_elbow[0], left_elbow[1]
                    x0, y0 = posicion_codo_inicial
                    dentro_margen = abs(x - x0) <= MARGEN_CODO and abs(y - y0) <= MARGEN_CODO

                    nuevo_estado = "good" if dentro_margen else "bad"
                    imagen = imagen_correcto3 if dentro_margen else imagen_incorrecto3
                    pegar_imagen_en_array(m.array, imagen, x=10, y=70)

                    break
        else:
            pegar_imagen_en_array(m.array, imagen_idle3, x=10, y=70)
            
        if boxes is not None and len(boxes) > 0:
            drawer.annotate_image(m.array, boxes, scores,
                                  np.zeros(scores.shape), keypoints, args.detection_threshold,
                                  args.detection_threshold, request.get_metadata(), picam2, stream)
            global last_m_array, evaluar_tick, color_resultado, mostrar_color_resultado
            global evaluaciones_realizadas, resultados

            last_m_array = m.array  # Guardamos referencia al frame actual

            for person in keypoints:
                if FLAG_POS_CODO.exists() and posicion_codo_inicial is None:
                    left_elbow = person[7]
                    if left_elbow[2] > args.detection_threshold:
                        posicion_codo_inicial = (left_elbow[0], left_elbow[1])
                        print(f"[POS] Codo izquierdo guardado: {posicion_codo_inicial}")
                        try:
                            FLAG_POS_CODO.unlink()
                        except:
                            pass




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
                    # FLAG para detectar persona
                    if not FLAG_PERSONA.exists():
                        with open(FLAG_PERSONA, 'w') as f:
                            f.write('persona')
                        print("[FLAG] Persona detectada → FLAG_PERSONA")

                    # Etapa 1: mano izquierda ≈ hombro
                    if not FLAG_PASO1.exists() and FLAG_HABILITAR_PASO1.exists():
                        if abs(diferencia) <= args.margen_altura:
                            with open(FLAG_PASO1, 'w') as f:
                                f.write('paso1')
                            print("[FLAG] Paso 1 completado → FLAG_PASO1")

                    # Etapa 2: IMU en posición correcta
                    if not FLAG_PASO2.exists() and FLAG_HABILITAR_PASO2.exists():
                        if "correcta" in estado_imu.lower():
                            with open(FLAG_PASO2, 'w') as f:
                                f.write('paso2')
                            print("[FLAG] Paso 2 completado → FLAG_PASO2")


                    # Etapa 3: muñeca izquierda ≈ hombro izquierdo
                    if FLAG_PASO2.exists() and FLAG_HABILITAR_PASO3.exists() and not FLAG_PASO3.exists():
                        left_shoulder = person[5]  # hombro izquierdo
                        left_wrist = person[9]     # muñeca izquierda
                        if (left_shoulder[2] > args.detection_threshold and left_wrist[2] > args.detection_threshold):
                            altura_izquierda = left_shoulder[1]
                            altura_muneca_izquierda = left_wrist[1]
                            diferencia_izquierda = altura_izquierda - altura_muneca_izquierda
                            if abs(diferencia_izquierda) <= args.margen_altura:
                                with open(FLAG_PASO3, 'w') as f:
                                    f.write('paso3')
                                print("[FLAG] Paso 3 completado → FLAG_PASO3")

                    if evaluar_tick:
                        evaluar_tick = False
                        postura_correcta = -args.margen_altura <= diferencia <= args.margen_altura
                        agarre_correcto = "bien" in estado_imu1
                        arco_correcto = False
                        if posicion_codo_inicial is not None and person[7][2] > args.detection_threshold:
                            x, y = person[7][0], person[7][1]
                            x0, y0 = posicion_codo_inicial
                            if abs(x - x0) <= MARGEN_CODO and abs(y - y0) <= MARGEN_CODO:
                                arco_correcto = True

                        # Calcula cuántos de los 3 son correctos
                        aciertos = sum([postura_correcta, agarre_correcto, arco_correcto])

                        # Puntuación proporcional: 0.0, 0.333, 0.666, 1.0
                        puntuacion = round(aciertos / 3, 3)

                        color_resultado = (0, 255, 0, 255) if postura_correcta else (255, 0, 0, 255)
                        mostrar_color_resultado = True
                        resultados.append(puntuacion)
                        evaluaciones_realizadas += 1

                        if puntuacion == 1.0:
                            sound_correct.play()
                        else:
                            # Identificar errores individuales
                            sound_incorrect.play()
                            altura_incorrecta = not postura_correcta
                            agarre_incorrecto = not agarre_correcto
                            arco_incorrecto = not arco_correcto

                            # Triple error
                            if altura_incorrecta and agarre_incorrecto and arco_incorrecto:
                                sound_todo_mal.play()
                            # Dobles combinaciones
                            elif altura_incorrecta and agarre_incorrecto:
                                sound_altura_agarre.play()
                            elif altura_incorrecta and arco_incorrecto:
                                sound_altura_arco.play()
                            elif agarre_incorrecto and arco_incorrecto:
                                sound_agarre_arco.play()  # Puedes sustituir por otro si tienes
                            # Errores individuales
                            elif altura_incorrecta:
                                if diferencia > 0:
                                    sound_bajar.play()  # Muñeca más arriba → bajar
                                else:
                                    sound_subir.play()  # Muñeca más abajo → subir
                            elif agarre_incorrecto:
                                sound_agarre_mal.play()
                            elif arco_incorrecto:
                                sound_arco.play()
                            else:
                                sound_incorrect.play()  # Fallback de seguridad

                        if puntuacion == 1.0:
                            estado_eval = "✔️ EXCELENTE"
                        elif puntuacion >= 0.66:
                            estado_eval = "🟢 BUENO"
                        elif puntuacion >= 0.33:
                            estado_eval = "🟡 ACEPTABLE"
                        else:
                            estado_eval = "❌ INCORRECTO"

                        print(f"[EVAL] {estado_eval} | Evaluación #{evaluaciones_realizadas}/20")
                        if evaluaciones_realizadas >= 20:
                            aciertos = sum(resultados)
                            registrar_resultado(leccion_idx=2, aciertos=aciertos)  # Lección 3
                            distribuir_puntos_en_txt(leccion_idx=2, aciertos=aciertos)
                            print("[FIN] Se completaron 20 evaluaciones. Esperando instrucciones del proceso padre...")
                            global cerrar_programa
                            try:
                                with open(FLAG_EVALUACION, 'w') as f:
                                    f.write("done")
                                print("[INFO] FLAG_EVALUACION escrita correctamente.")
                            except Exception as e:
                                print(f"[ERROR] No se pudo escribir FLAG_EVALUACION: {e}")

                            cerrar_programa = True
                    global temporizador_activo
                    if mostrar_color_resultado:
                        imagen_a_usar = imagen_correcto if color_resultado == (0, 255, 0, 255) else imagen_incorrecto
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
    try:
        subprocess.Popen(["python3", str(RESULT_GUI_PATH)])
        print("[INFO] GUI de resultados abierta correctamente.")
    except Exception as e:
        print(f"[ERROR] Al abrir Result.py: {e}")

    print("[INFO] Programa finalizado correctamente.")
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
    global tick_count, evaluar_tick, tick_total, cerrar_programa, posicion_codo_inicial
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

                    # Guardar posición del codo izquierdo en el primer tick
                    if tick_total == 4 and posicion_codo_inicial is None and last_keypoints is not None:
                        for person in last_keypoints:
                            left_elbow = person[7]
                            if left_elbow[2] > args.detection_threshold:
                                posicion_codo_inicial = (left_elbow[0], left_elbow[1])
                                print(f"[INFO] Posición inicial del codo izquierdo guardada: {posicion_codo_inicial}")
                                break




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
                ultimos = [int(r["intento"]) for r in reader if r["leccion"] == f"Lección {leccion_idx + 1}"]
            if ultimos:
                intento = max(ultimos) + 1
            else:
                intento = 1


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

                # Convertimos aciertos (0 a 20) a radar (0 a 8)
                nuevo_valor = round((aciertos / 20) * 8)

                # Actualizamos cada campo con un valor aleatorio entre el actual y el nuevo, solo si mejora
                for idx in range(len(valores)):
                    if nuevo_valor > valores[idx]:
                        valor_random = random.randint(valores[idx], nuevo_valor)
                        valores[idx] = valor_random
                # Sobrescribimos la línea
                lineas[i] = f"Lección {leccion_idx + 1}: {','.join(map(str, valores))}\n"
                break

        # Actualizamos el nivel si corresponde
        for i, linea in enumerate(lineas):
            if linea.startswith("Nivel:"):
                nivel_actual = int(linea.strip().split(":")[1])
                if nivel_actual == 2 and (aciertos / 20) >= 0.7:
                    nuevo_nivel = 3
                    lineas[i] = f"Nivel: {nuevo_nivel}\n"
                    print(f"[NIVEL] El usuario ha subido al nivel {nuevo_nivel}")
                else:
                    print(f"[NIVEL] No se modificó el nivel. Actual: {nivel_actual}")
                break

        if progreso_encontrado:
            with open(user_file, 'w', encoding='utf-8') as f:
                f.writelines(lineas)
            print(f"[TXT] Progreso actualizado para Lección {leccion_idx + 1}")
        else:
            print("[WARN] No se encontró la lección para actualizar.")
    except Exception as e:
        print(f"[ERROR] Al actualizar progreso en TXT: {e}")

def hilo_simulacion_etapas():
    if not MODO_SIMULACION_IMU:
        return
    print("[SIMULACIÓN] Modo automático activado para IMU (solo paso 2)")
    while not cerrar_programa:
        if not FLAG_PASO2.exists():
            with open(FLAG_PASO2, 'w') as f:
                f.write('paso2')
            print("[SIMULACIÓN] FLAG_PASO2 creado automáticamente")
        time.sleep(0.5)

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
        Thread(target=hilo_simulacion_etapas, daemon=True).start()

        while not cerrar_programa:
            time.sleep(0.5)
        
        # 🔽 Se llegó al final por evaluación completa
        print("[INFO] Evaluaciones completadas detectadas. Iniciando cierre limpio...")

        try:
            picam2.stop()
            time.sleep(0.3)
            picam2.close()
        except Exception as e:
            print(f"[WARN] Error al detener picam2: {e}")

        try:
            imx500.stop_network_task()
        except AttributeError:
            print("[WARN] Error al detener red neuronal: 'IMX500' object has no attribute 'stop_network_task'")
        except Exception as e:
            print(f"[WARN] Error inesperado al detener red neuronal: {e}")

        import gc
        del picam2
        gc.collect()

        print("[INFO] Programa finalizado correctamente.")
        sys.exit(0)


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

        # Abrir Resultados incluso si se cierra con X o interrupción
        try:
            subprocess.Popen([VENV_PYTHON, str(RESULT_GUI_PATH)])
            print("[INFO] GUI de resultados abierta con entorno virtual.")
        except Exception as e:
            print(f"[ERROR] Al abrir Result.py: {e}")
