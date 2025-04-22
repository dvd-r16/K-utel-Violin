import pygame
import time
import os

# Ruta absoluta del sonido
BASE_PATH = os.path.dirname(__file__)
SOUND_PATH = os.path.join(BASE_PATH, "tick.wav")

pygame.mixer.init()
tick = pygame.mixer.Sound(SOUND_PATH)

bpm = 120
interval = 90 / bpm

while True:
    tick.play()
    time.sleep(interval)
