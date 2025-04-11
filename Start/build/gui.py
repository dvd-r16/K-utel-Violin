from pathlib import Path
from tkinter import Tk, Canvas, PhotoImage
import subprocess

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"D:\Desktop\K'UTEL VIOLIN\Start\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def close_splash():
    window.destroy()  # Ahora se cierra un poco después

def launch_main_gui():
    main_gui_path = r"D:\Desktop\K'UTEL VIOLIN\Menu\build\gui.py"
    subprocess.Popen(["python", main_gui_path])
    window.after(2000, close_splash)  # Espera 500 ms antes de cerrar splash

window = Tk()
window.attributes("-fullscreen", True)
window.geometry("1536x864")
window.configure(bg="#FFFFFF")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=864,
    width=1536,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)
canvas.create_rectangle(6.0, 0.0, 1554.0, 864.0, fill="#FFFFFF", outline="")

image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(768.0, 432.0, image=image_image_1)

# Espera 6 segundos y lanza la GUI principal
window.after(6000, launch_main_gui)

window.resizable(False, False)
window.mainloop()
