import subprocess
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import os

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"
BASE_PATH = OUTPUT_PATH.parent.parent  # K-utel-Violin

REGISTER_PATH = BASE_PATH / "Register" / "build" / "gui.py"
MENU_PATH = BASE_PATH / "Menu" / "build" / "gui.py"
USERS_PATH = BASE_PATH / "Login" / "usuarios"  # Carpeta donde se guarda info de usuarios

# Asegura que la carpeta de usuarios exista
USERS_PATH.mkdir(parents=True, exist_ok=True)

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def ejecutar_script(path):
    subprocess.Popen(["python", str(path)])

def verificar_usuario(usuario_id):
    return (USERS_PATH / f"user_{usuario_id}.txt").exists()

def manejar_click(usuario_id, boton, imagen_original, imagen_registrado):
    seleccion_path = BASE_PATH / "usuario_seleccionado.txt"

    if seleccion_path.exists():
        seleccion_path.unlink()

    with open(seleccion_path, "w") as f:
        f.write(str(usuario_id))

    # Leer e imprimir los datos del usuario seleccionado
    user_file = USERS_PATH / f"user_{usuario_id}.txt"
    if user_file.exists():
        print(f"\n[INFO] Usuario seleccionado: {usuario_id}")
        with open(user_file, "r", encoding="utf-8") as f_user:
            contenido = f_user.read()
            print("[DATOS DEL USUARIO]:")
            print(contenido)
    else:
        print(f"[INFO] Usuario {usuario_id} no tiene datos registrados aún.")

    # Cerrar ventana actual luego de ejecutar el script
    window.after(2000, window.destroy)  # Espera 2 segundos y cierra
    if verificar_usuario(usuario_id):
        boton.config(image=imagen_registrado)
        ejecutar_script(MENU_PATH)
    else:
        boton.config(image=imagen_original)
        ejecutar_script(REGISTER_PATH)

window = Tk()
window.attributes("-fullscreen", True)
window.configure(bg="#32457D")

canvas = Canvas(window, bg="#32457D", height=900, width=1440, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(720.0, 450.0, image=image_image_1)

botones = []
imagenes_originales = []
imagenes_registrado = []

# Posiciones de botones
posiciones = [17.0, 301.0, 587.0, 873.0, 1160.0]

for i in range(5):
    img_orig = PhotoImage(file=relative_to_assets(f"button_{i+1}.png"))
    img_reg = PhotoImage(file=relative_to_assets(f"button_{i+1}.1.png"))

    imagen_actual = img_reg if verificar_usuario(i+1) else img_orig

    btn = Button(
        image=imagen_actual,
        borderwidth=0,
        highlightthickness=0,
        bg="#32457D",
        activebackground="#32457D",
        relief="flat"
    )
    btn.place(x=posiciones[i], y=335.0, width=265.0, height=264.0)

    # Ahora que btn ya está definido, podemos asignar el comando
    btn.config(command=lambda i=i, b=btn, o=img_orig, r=img_reg: manejar_click(i+1, b, o, r))

    botones.append(btn)
    imagenes_originales.append(img_orig)
    imagenes_registrado.append(img_reg)

window.resizable(False, False)
window.mainloop()
