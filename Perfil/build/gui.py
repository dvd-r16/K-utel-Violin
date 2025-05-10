from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import subprocess
from PIL import Image, ImageTk
import os


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"
BASE_PATH = Path(__file__).resolve().parent.parent.parent

MENU_PATH = BASE_PATH / "Menu" / "build" / "gui.py"
LOGIN_PATH = BASE_PATH / "Login" / "build" / "gui.py"
USERS_PATH = BASE_PATH / "Login" / "usuarios"
USER_SELECTED_PATH = BASE_PATH / "usuario_seleccionado.txt"
ESTADISTICAS_GUI_PATH = BASE_PATH / "Stats" / "build" / "gui.py"
PHOTO_PATH = BASE_PATH / "Camara" / "Photo.py"


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def open_login():
    # Cambiar imagen del botón 1 al presionar
    button_1.config(image=button_image_1_pressed)
    subprocess.Popen(["python", str(LOGIN_PATH)])
    window.after(1000, window.destroy)

def open_menu():
    subprocess.Popen(["python", str(MENU_PATH)])
    window.after(1000, window.destroy)

def open_estadisticas_gui():
    subprocess.Popen(["python", str(ESTADISTICAS_GUI_PATH)])
    window.after(4000, window.destroy)

# ----------------- Cargar datos del usuario -----------------

def cargar_datos_usuario():
    try:
        with open(USER_SELECTED_PATH, 'r') as file:
            user_id = file.read().strip()
        user_file = USERS_PATH / f"user_{user_id}.txt"
        with open(user_file, 'r') as file:
            data = file.readlines()
        datos = {}
        for linea in data:
            if ':' in linea:
                clave, valor = linea.strip().split(":", 1)
                clave = clave.strip().lower()
                # Normaliza claves comunes
                if "nombre" in clave:
                    datos["nombre"] = valor.strip()
                elif "apellido" in clave:
                    datos["apellido"] = valor.strip()
                elif "edad" in clave:
                    datos["edad"] = valor.strip()
                elif "genero" in clave or "género" in clave:
                    datos["genero"] = valor.strip()
                elif "nivel" in clave:
                    datos["nivel"] = valor  # Guardar nivel


                genero_valor = datos.get("genero", "").strip().lower()
        if "femenino" in genero_valor:
            genero = "F"
        elif "masculino" in genero_valor:
            genero = "M"
        else:
            genero = "F/M"

        return (
            datos.get("nombre", "NOMBRE"),
            datos.get("apellido", "APELLIDO"),
            datos.get("edad", "##"),
            datos.get("genero", genero),
            datos.get("nivel", "0")
        )

    except Exception as e:
        print(f"Error al leer datos del usuario: {e}")
        return ("NOMBRE", "APELLIDO", "##", "F/M", "0")

# ------------------ Inicio de ventana -----------------------

window = Tk()
window.overrideredirect(True)
window.geometry("1440x900")
window.configure(bg="#32457D")

canvas = Canvas(
    window,
    bg="#32457D",
    height=900,
    width=1440,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(720.0, 450.0, image=image_image_1)

# Botones
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_image_1_pressed = PhotoImage(file=relative_to_assets("button_1.1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=open_login,
    relief="flat",
    bg="#32457D",
    activebackground="#32457D"
)
button_1.place(x=148.0, y=88.0, width=156.55, height=74.16)

button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=open_estadisticas_gui,
    relief="flat",
    bg="#32457D",
    activebackground="#32457D"
)
button_2.place(x=348.94, y=88.0, width=258.50, height=73.97)

button_active_3 = PhotoImage(file=relative_to_assets("button_3.1.png"))
button_3 = Button(
    image=button_active_3,
    borderwidth=0,
    highlightthickness=0,
    command=open_menu,
    relief="flat",
    bg="#32457D",
    activebackground="#32457D"
)
button_3.place(x=659.96, y=88.0, width=154.83, height=73.97)

# Elementos gráficos
image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
canvas.create_image(1200.0, 125.0, image=image_image_3)

# ------------------ Mostrar datos de usuario ------------------

nombre, apellido, edad, genero, nivel = cargar_datos_usuario()

nivel = nivel.strip()

if nivel == "1":
    image_nivel = PhotoImage(file=relative_to_assets("image_10.1.png"))
elif nivel == "2":
    image_nivel = PhotoImage(file=relative_to_assets("image_10.2.png"))
elif nivel == "3":
    image_nivel = PhotoImage(file=relative_to_assets("image_10.3.png"))
else:
    image_nivel = PhotoImage(file=relative_to_assets("image_10.png"))

canvas.create_image(1021.36, 123.83, image=image_nivel)

canvas.create_text(226.0, 340.0, anchor="nw", text=nombre, fill="#FFFFFF", font=("LondrinaSolid Black", -43))
canvas.create_text(226.0, 502.0, anchor="nw", text=apellido, fill="#FFFFFF", font=("LondrinaSolid Black", -43))
canvas.create_text(250.0, 653.0, anchor="nw", text=edad, fill="#FFFFFF", font=("LondrinaSolid Black", -43))
canvas.create_text(561.0, 653.0, anchor="nw", text=genero, fill="#FFFFFF", font=("LondrinaSolid Black", -43))

# Botón de imagen del usuario
try:
    with open(USER_SELECTED_PATH, "r") as f:
        user_id = f.read().strip()
    user_image_path = USERS_PATH / f"user_{user_id}.jpeg"

    if user_image_path.exists():
        imagen_usuario = Image.open(user_image_path).resize((420, 420))
        imagen_usuario_tk = ImageTk.PhotoImage(imagen_usuario)
    else:
        print(f"⚠️ Imagen no encontrada: {user_image_path}")
        imagen_usuario_tk = PhotoImage(file=relative_to_assets("button_4.png"))

except Exception as e:
    print(f"❌ Error cargando imagen del usuario: {e}")
    imagen_usuario_tk = PhotoImage(file=relative_to_assets("button_4.png"))


def abrir_camara():
    try:
        subprocess.Popen(["python3", str(PHOTO_PATH)])
    except Exception as e:
        print(f"❌ No se pudo abrir Photo.py: {e}")



button_4 = Button(
    image=imagen_usuario_tk,
    borderwidth=0,
    highlightthickness=0,
    command=abrir_camara,
    relief="flat",
    bg="#32457D",
    activebackground="#32457D"
)
button_4.place(x=794.0, y=321.0, width=420.0, height=420.0)

# Tiempo de última modificación del archivo JPEG
try:
    last_mtime = os.path.getmtime(user_image_path)
except:
    last_mtime = 0

def verificar_cambio_imagen():
    global imagen_usuario_tk, last_mtime

    try:
        nuevo_mtime = os.path.getmtime(user_image_path)
        if nuevo_mtime != last_mtime:
            print("🔄 Imagen del usuario modificada, actualizando...")
            last_mtime = nuevo_mtime
            nueva_imagen = Image.open(user_image_path).resize((420, 420))
            imagen_usuario_tk = ImageTk.PhotoImage(nueva_imagen)
            button_4.config(image=imagen_usuario_tk)
    except:
        pass

    window.after(2000, verificar_cambio_imagen)  # Revisa cada 2 segundos

window.resizable(False, False)
verificar_cambio_imagen()
window.mainloop()
