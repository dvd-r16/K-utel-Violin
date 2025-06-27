#!/usr/bin/python3
from pathlib import Path
from tkinter import Tk, Canvas, PhotoImage
import os
import sys

VENV_PYTHON = "/home/dvdr/Documentos/K-utel-Violin/Kutelenv/bin/python"

if sys.executable != VENV_PYTHON:
    os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def launch_main_gui():
    project_root = Path(__file__).resolve().parent.parent.parent
    main_gui_path = project_root / "Login" / "build" / "gui.py"
    python_path = sys.executable  # Usa el mismo que ejecutó este archivo

    os.execv(python_path, [python_path, str(main_gui_path)])

# Splash
window = Tk()
#window.attributes("-fullscreen", True)
window.overrideredirect(True)
window.geometry("1440x900")
window.configure(bg="#32457D")

canvas = Canvas(
    window,
    bg="#32457D",
    height=864,
    width=1536,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)
canvas.create_rectangle(6.0, 0.0, 1554.0, 864.0, fill="#32457D", outline="")

image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(768.0, 432.0, image=image_image_1)

window.after(6000, launch_main_gui)

window.resizable(False, False)
window.mainloop()