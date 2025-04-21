from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, StringVar
import subprocess
import re
import pandas as pd
from datetime import datetime

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"
MENU_GUI_PATH = OUTPUT_PATH.parent.parent / "Menu" / "build" / "gui.py"
BASE_PATH = Path(__file__).resolve().parent.parent.parent
USERS_PATH = BASE_PATH / "Login" / "usuarios"
USER_SELECTED_PATH = BASE_PATH / "usuario_seleccionado.txt"

USERS_PATH.mkdir(parents=True, exist_ok=True)

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()
window.attributes("-fullscreen", True)
window.geometry("1440x900")
window.configure(bg="#32457D")

canvas = Canvas(window, bg="#32457D", height=900, width=1440, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)
image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(720.0, 450.0, image=image_image_1)

# Estados
genero = StringVar(value="")  # "" | "Masculino" | "Femenino"

# Imagenes
button_1_active = PhotoImage(file=relative_to_assets("button_1.png"))
button_1_inactive = PhotoImage(file=relative_to_assets("button_1.1.png"))
button_2_off = PhotoImage(file=relative_to_assets("button_2.png"))
button_2_on = PhotoImage(file=relative_to_assets("button_2.1.png"))
button_3_off = PhotoImage(file=relative_to_assets("button_3.png"))
button_3_on = PhotoImage(file=relative_to_assets("button_3.1.png"))

# Entradas con validación
def validar_todo(*args):
    nombre = entry_1.get()
    apellido = entry_2.get()
    edad = entry_3.get()

    if re.fullmatch(r"[A-Za-záéíóúÁÉÍÓÚüÜñÑ\s]+", nombre) and \
       re.fullmatch(r"[A-Za-záéíóúÁÉÍÓÚüÜñÑ\s]+", apellido) and \
       edad.isdigit() and (1 <= int(edad) <= 90) and genero.get() in ("Masculino", "Femenino"):
        button_1.config(state="normal", image=button_1_active)
    else:
        button_1.config(state="disabled", image=button_1_inactive)

# Entradas
entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
canvas.create_image(723.5, 353.5, image=entry_image_1)
entry_1 = Entry(bd=0, bg="#203262", fg="white", font=("Arial", 18), highlightthickness=0)
entry_1.place(x=369.5, y=309.0, width=708.0, height=87.0)
entry_1.bind("<KeyRelease>", validar_todo)

entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
canvas.create_image(719.5, 504.5, image=entry_image_2)
entry_2 = Entry(bd=0, bg="#203262", fg="white", font=("Arial", 18), highlightthickness=0)
entry_2.place(x=365.5, y=460.0, width=708.0, height=87.0)
entry_2.bind("<KeyRelease>", validar_todo)

entry_image_3 = PhotoImage(file=relative_to_assets("entry_3.png"))
canvas.create_image(943.0, 673.0, image=entry_image_3)
entry_3 = Entry(bd=0, bg="#203262", fg="white", font=("Arial", 18), highlightthickness=0)
entry_3.place(x=813.0, y=628.0, width=260.0, height=88.0)
entry_3.bind("<KeyRelease>", validar_todo)

# Botones de género
def seleccionar_genero(valor):
    genero.set(valor)
    if valor == "Masculino":
        button_2.config(image=button_2_on)
        button_3.config(image=button_3_off)
    elif valor == "Femenino":
        button_2.config(image=button_2_off)
        button_3.config(image=button_3_on)
    validar_todo()

button_2 = Button(image=button_2_off, borderwidth=0, highlightthickness=0, bg="#32457D", activebackground="#32457D",
                  command=lambda: seleccionar_genero("Masculino"), relief="flat")
button_2.place(x=499.0, y=633.0, width=154.0, height=154.0)

button_3 = Button(image=button_3_off, borderwidth=0, highlightthickness=0, bg="#32457D", activebackground="#32457D",
                  command=lambda: seleccionar_genero("Femenino"), relief="flat")
button_3.place(x=325.0, y=633.0, width=154.0, height=154.0)

# Guardar datos
def guardar_datos():
    nombre = entry_1.get().strip()
    apellido = entry_2.get().strip()
    edad = entry_3.get().strip()
    genero_valor = genero.get()

    # Leer ID seleccionado
    if not USER_SELECTED_PATH.exists():
        print("[ERROR] No se encontró el archivo usuario_seleccionado.txt")
        return

    with open(USER_SELECTED_PATH, "r", encoding="utf-8") as f:
        id_usuario = f.read().strip()

    # Verificar si es válido
    if not id_usuario.isdigit() or not (1 <= int(id_usuario) <= 5):
        print(f"[ERROR] ID de usuario inválido: {id_usuario}")
        return

    # Construir rutas de archivos
    ruta_txt = USERS_PATH / f"user_{id_usuario}.txt"
    ruta_csv = USERS_PATH / f"user_{id_usuario}.csv"

    # Verificar si ya existe
    if ruta_txt.exists():
        print(f"[INFO] El usuario user_{id_usuario}.txt ya existe.")
        return

    # Escribir archivo .txt con datos personales y progreso
    contenido = (
        f"Nombre: {nombre}\n"
        f"Apellido: {apellido}\n"
        f"Edad: {edad}\n"
        f"Género: {genero_valor}\n"
        f"Nivel: 0\n"
        f"[Progreso]\n"
        f"Lección 1: 0,0,0,0,0,0\n"
        f"Lección 2: 0,0,0,0,0,0\n"
        f"Lección 3: 0,0,0,0,0,0\n"
        f"Lección 4: 0,0,0,0,0,0"
    )

    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(contenido)

    # Crear archivo CSV vacío
    df = pd.DataFrame(columns=["leccion", "intento", "valor", "fecha"])
    df.to_csv(ruta_csv, index=False)

    # Lanzar GUI del menú y cerrar ventana actual
    subprocess.Popen(["python", str(MENU_GUI_PATH)])
    window.after(2000, window.destroy)


button_1 = Button(image=button_1_inactive, borderwidth=0, highlightthickness=0, bg="#32457D",
                  activebackground="#32457D", command=guardar_datos, relief="flat", state="disabled")
button_1.place(x=863.0, y=773.0, width=258.5, height=74)

window.resizable(False, False)
window.mainloop()
