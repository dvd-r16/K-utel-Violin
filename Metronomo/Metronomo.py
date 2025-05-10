import pygame
import time
import os
import signal
import sys

# Ruta absoluta del sonido
BASE_PATH = os.path.dirname(__file__)
SOUND_PATH = os.path.join(BASE_PATH, "tick.wav")

pygame.mixer.init()
tick = pygame.mixer.Sound(SOUND_PATH)

bpm = 120
interval = 90 / bpm

running = True

def handle_exit(signum, frame):
    global running
    print("[INFO] Señal de salida recibida, cerrando metronomo...")
    running = False

# Registrar señales
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

while running:
    tick.play()
    time.sleep(interval)

print("[INFO] Metronomo finalizado.")
sys.exit(0)
