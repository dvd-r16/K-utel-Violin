from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import subprocess
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pandas as pd
import pygame

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"
BASE_PATH = Path(__file__).resolve().parent.parent.parent
LOGIN_GUI_PATH = BASE_PATH / "Login" / "build" / "gui.py"
MENU_GUI_PATH = BASE_PATH / "Menu" / "build" / "gui.py"
PERFIL_GUI_PATH = BASE_PATH / "Perfil" / "build" / "gui.py"
USER_SELECTED_PATH = BASE_PATH / "usuario_seleccionado.txt"
USERS_PATH = BASE_PATH / "Login" / "usuarios"

RADAR_IMAGE_PATH = ASSETS_PATH / "image_4.png"
LINE_CHARTS_PATHS = [ASSETS_PATH / "image_5.png", ASSETS_PATH / "image_6.png", ASSETS_PATH / "image_7.png"]


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

music_path = str(ASSETS_PATH / "musica_fondo.wav")
pygame.mixer.init()

try:
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # -1 significa repetir indefinidamente
    print("[INFO] Música de fondo iniciada.")
except Exception as e:
    print(f"[ERROR] No se pudo reproducir la música: {e}")



def leer_progreso_usuario():
    try:
        with open(USER_SELECTED_PATH, 'r') as f:
            user_id = f.read().strip()
        print(f"[INFO] Usuario seleccionado: {user_id}")
        user_file = USERS_PATH / f"user_{user_id}.txt"

        progreso = []
        with open(user_file, 'r', encoding='utf-8') as f:
            lineas = f.readlines()

        grabar = False
        for linea in lineas:
            if '[Progreso]' in linea:
                grabar = True
                continue
            if grabar and 'Lección' in linea:
                datos = linea.split(':')[1].strip()
                valores = list(map(int, datos.split(',')))
                progreso.append(valores)

        return progreso
    except Exception as e:
        print(f"[ERROR] Al leer el progreso: {e}")
        return []

def generar_grafica_lineas():
    try:
        with open(USER_SELECTED_PATH, 'r') as f:
            user_id = f.read().strip()
        print(f"[INFO] Generando gráfica de líneas para el usuario: {user_id}")
        csv_path = USERS_PATH / f"user_{user_id}.csv"

        df = pd.read_csv(csv_path)
        print(f"[INFO] CSV cargado correctamente:\n{df.head()}\n")

        # Normalizar columna 'leccion'
        df['leccion'] = df['leccion'].str.extract(r'(\d+)').astype(float)

        for leccion in [1, 2, 3]:
            df_leccion = df[df['leccion'] == leccion].sort_values(by='intento', ascending=False).head(10).sort_values(by='intento')
            valores = df_leccion['valor'].tolist()
            print(f"[INFO] Lección {leccion}: {valores}")

            fig, ax = plt.subplots(figsize=(5.29, 1.24))
            fig.patch.set_facecolor('#203262')
            ax.set_facecolor('#203262')

            if valores:
                ax.plot(range(1, len(valores)+1), valores, marker='o', color='#6ce5e8', linewidth=2)

            ax.set_ylim(0, 10)
            ax.set_xlim(0.5, 10.5)
            ax.set_xticks([])
            ax.set_yticks([0, 2, 4, 6, 8, 10])
            ax.tick_params(colors='white')

            for spine in ax.spines.values():
                spine.set_color('#203262')

            fig.savefig(LINE_CHARTS_PATHS[leccion - 1], dpi=100, bbox_inches='tight', transparent=False)
            plt.close(fig)

    except Exception as e:
        print(f"[ERROR] Al generar gráficas de líneas: {e}")


def generar_grafica_radar():
    progreso = leer_progreso_usuario()
    if not progreso:
        return

    etiquetas = ["Brazo Izq", "Hombro", "Cuello", "Brazo der", "Arco", "Violin"]
    num_vars = len(etiquetas)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#203262')
    ax.set_facecolor('#203262')
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_thetagrids(np.degrees(angles[:-1]), etiquetas, color='white')
    ax.set_rlabel_position(0)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], color='white', size=8)
    ax.tick_params(colors='white')
    ax.yaxis.grid(False)  # Oculta las líneas radiales (círculos)

    # Hexágonos punteados
    for r in [2, 4, 6, 8, 10]:
        ax.plot(angles, [r]*len(angles), color='gray', linewidth=1.5, linestyle='dotted')

    ax.spines['polar'].set_visible(False)

    colores = ['#5ce1e6', '#97d498', '#ffbd59', '#ff871d']
    etiquetas_leyenda = ["Lección 1", "Lección 2", "Lección 3", "Lección 4"]

    for idx, leccion in enumerate(progreso):
        datos = leccion + leccion[:1]
        ax.plot(angles, datos, label=etiquetas_leyenda[idx], linewidth=2.5, linestyle='solid', color=colores[idx % len(colores)])
        ax.fill(angles, datos, alpha=0.1, color=colores[idx % len(colores)])

    # Leyenda personalizada
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, fontsize=8, frameon=True)
    legend.get_frame().set_facecolor('#203262')
    legend.get_frame().set_edgecolor('#203262')
    for text in legend.get_texts():
        text.set_color("white")

    # Guardar y redimensionar
    fig.savefig(RADAR_IMAGE_PATH, dpi=100, bbox_inches='tight', transparent=False)
    plt.close(fig)

    img = Image.open(RADAR_IMAGE_PATH)
    img = img.resize((529, 560))
    img.save(RADAR_IMAGE_PATH)

# Generar gráficas
generar_grafica_radar()
generar_grafica_lineas()

# Interfaz Tkinter
window = Tk()
window.overrideredirect(True)
window.geometry("1440x900")
window.configure(bg="#32457D")

canvas = Canvas(window, bg="#32457D", height=900, width=1440, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(720.0, 450.0, image=image_image_1)

button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_active_1 = PhotoImage(file=relative_to_assets("button_1.1.png"))
button_image_2 = PhotoImage(file=relative_to_assets("button_2.1.png"))
button_active_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
button_active_3 = PhotoImage(file=relative_to_assets("button_3.1.png"))

active_button = 2

def open_and_close(path):
    subprocess.Popen(["python", str(path)])
    pygame.mixer.music.stop()
    window.after(2000, window.destroy)

def activate_button(button):
    global active_button
    if active_button == button:
        if button == 1:
            button_1.config(image=button_active_1)
            open_and_close(LOGIN_GUI_PATH)
        elif button == 2:
            button_2.config(image=button_active_2)
            open_and_close(MENU_GUI_PATH)
        elif button == 3:
            button_3.config(image=button_active_3)
            open_and_close(PERFIL_GUI_PATH)
        return

    button_1.config(image=button_image_1)
    button_2.config(image=button_image_2)
    button_3.config(image=button_image_3)

    if button == 1:
        button_1.config(image=button_active_1)
        open_and_close(LOGIN_GUI_PATH)
    elif button == 2:
        button_2.config(image=button_active_2)
        open_and_close(MENU_GUI_PATH)
    elif button == 3:
        button_3.config(image=button_active_3)
        open_and_close(PERFIL_GUI_PATH)

    active_button = button

button_1 = Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: activate_button(1), relief="flat", bg="#32457D", activebackground="#32457D")
button_1.place(x=148.0, y=87.8341, width=156.5533, height=74.1658)

button_2 = Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: activate_button(2), relief="flat", bg="#32457D", activebackground="#32457D")
button_2.place(x=348.9462, y=87.8341, width=258.5037, height=73.9782)

button_3 = Button(image=button_image_3, borderwidth=0, highlightthickness=0, command=lambda: activate_button(3), relief="flat", bg="#32457D", activebackground="#32457D")
button_3.place(x=659.9584, y=87.8341, width=154.8329, height=73.9782)

# Leer nivel del usuario
try:
    with open(USER_SELECTED_PATH, 'r') as f:
        user_id = f.read().strip()

    user_file = USERS_PATH / f"user_{user_id}.txt"
    nivel = "0"  # Por defecto

    if user_file.exists():
        with open(user_file, 'r', encoding='utf-8') as f:
            for line in f:
                if "Nivel:" in line:
                    nivel = line.split(":")[1].strip()
                    break
except Exception as e:
    print(f"[ERROR] Al leer nivel del usuario: {e}")
    nivel = "0"

# Seleccionar imagen según nivel
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

image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
canvas.create_image(1200.0, 125.0, image=image_image_3)

image_image_4 = PhotoImage(file=relative_to_assets("image_4.png"))
canvas.create_image(400.0, 524.0, image=image_image_4)

image_image_5 = PhotoImage(file=relative_to_assets("image_5.png"))
canvas.create_image(1048.0, 309.0, image=image_image_5)

image_image_6 = PhotoImage(file=relative_to_assets("image_6.png"))
canvas.create_image(1048.0, 520.0, image=image_image_6)

image_image_7 = PhotoImage(file=relative_to_assets("image_7.png"))
canvas.create_image(1048.0, 741.0, image=image_image_7)

window.resizable(False, False)
window.mainloop()
