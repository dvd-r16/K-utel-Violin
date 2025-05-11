import pygame
import time
import os
import socket
import signal
import sys

# Ruta absoluta del sonido
BASE_PATH = os.path.dirname(__file__)
SOUND_PATH = os.path.join(BASE_PATH, "tick.wav")

# Crear socket TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Manejo de señales (SIGTERM o Ctrl+C)
def salir_gracioso(signum, frame):
    print("\n[INFO] Señal de terminación recibida. Cerrando metrónomo...")
    try:
        client_socket.close()
    except:
        pass
    pygame.quit()
    sys.exit(0)

signal.signal(signal.SIGTERM, salir_gracioso)
signal.signal(signal.SIGINT, salir_gracioso)

# Intentar conexión hasta que el receptor esté listo
while True:
    try:
        client_socket.connect(('localhost', 9999))
        break
    except ConnectionRefusedError:
        print("[WAIT] Esperando a que el receptor esté listo...")
        time.sleep(1)

pygame.mixer.init()
tick = pygame.mixer.Sound(SOUND_PATH)

bpm = 120
interval = 90 / bpm  # Tiempo entre ticks

try:
    print("[INFO] Metronomo iniciado.")
    while True:
        try:
            tick.play()
            client_socket.sendall(b"tick\n")
            time.sleep(interval)
        except BrokenPipeError:
            print("[ERROR] El receptor cerró la conexión. Terminando metrónomo...")
            break
except KeyboardInterrupt:
    salir_gracioso(None, None)
finally:
    try:
        client_socket.close()
    except:
        pass
    pygame.quit()
    print("[INFO] Metrónomo cerrado limpiamente.")
