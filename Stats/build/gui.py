from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import subprocess
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"
BASE_PATH = Path(__file__).resolve().parent.parent.parent
LOGIN_GUI_PATH = BASE_PATH / "Login" / "build" / "gui.py"
MENU_GUI_PATH = BASE_PATH / "Menu" / "build" / "gui.py"
PERFIL_GUI_PATH = BASE_PATH / "Perfil" / "build" / "gui.py"
USER_SELECTED_PATH = BASE_PATH / "usuario_seleccionado.txt"
USERS_PATH = BASE_PATH / "Login" / "usuarios"

RADAR_IMAGE_PATH = ASSETS_PATH / "image_4.png"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

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
            print(f"[DEBUG] Línea: {linea.strip()}")
            if '[Progreso]' in linea:
                grabar = True
                continue
            if grabar and 'Lección' in linea:
                print(f"[INFO] Línea de progreso encontrada: {linea.strip()}")
                datos = linea.split(':')[1].strip()
                valores = list(map(int, datos.split(',')))
                print(f"[INFO] Valores convertidos: {valores}")
                progreso.append(valores)

        print(f"[INFO] Progreso total cargado: {progreso}")
        return progreso
    except Exception as e:
        print(f"[ERROR] Al leer el progreso: {e}")
        return []

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

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

    for r in [2, 4, 6, 8, 10]:
        ax.plot(angles, [r]*len(angles), color='gray', linewidth=1.5, linestyle='dotted')
        ax.spines['polar'].set_visible(False)

    colores = ['deepskyblue', 'dodgerblue', 'steelblue', 'slateblue']
    etiquetas_leyenda = ["Lección 1", "Lección 2", "Lección 3", "Lección 4"]

    for idx, leccion in enumerate(progreso):
        datos = leccion + leccion[:1]
        ax.plot(angles, datos, label=etiquetas_leyenda[idx], linewidth=2.5, linestyle='solid', color=colores[idx % len(colores)])
        ax.fill(angles, datos, alpha=0.1, color=colores[idx % len(colores)])

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, fontsize=8, labelcolor='#32457D')

    # Guarda y redimensiona
    fig.savefig(RADAR_IMAGE_PATH, dpi=100, bbox_inches='tight', transparent=False)
    plt.close(fig)

    img = Image.open(RADAR_IMAGE_PATH)
    img = img.resize((529, 560))
    img.save(RADAR_IMAGE_PATH)

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
    ax.yaxis.grid(False)  # Oculta líneas radiales por defecto
    

    # Dibujar líneas de fondo más gruesas en forma de hexágono
    for r in [2, 4, 6, 8, 10]:
        ax.plot(angles, [r]*len(angles), color='gray', linewidth=1.5, linestyle='dotted')
        ax.spines['polar'].set_visible(False)

    colores = ['#5ce1e6', '#97d498', '#ffbd59', '#ff871d']
    etiquetas_leyenda = ["Lección 1", "Lección 2", "Lección 3", "Lección 4"]

    for idx, leccion in enumerate(progreso):
        datos = leccion + leccion[:1]
        ax.plot(angles, datos, label=etiquetas_leyenda[idx], linewidth=2.5, linestyle='solid', color=colores[idx % len(colores)])
        ax.fill(angles, datos, alpha=0.1, color=colores[idx % len(colores)])

    legend=ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4, fontsize=8, frameon=True)
    # Personalización visual
    legend.get_frame().set_facecolor('#203262')  # Mismo color que el fondo
    legend.get_frame().set_edgecolor('#203262')  # Elimina borde
    for text in legend.get_texts():
        text.set_color("white")

    # Líneas punteadas para cada ítem de la leyenda
    fig.savefig(RADAR_IMAGE_PATH, dpi=100, bbox_inches='tight', transparent=False)
    plt.close(fig)

    # Redimensionar a 529x560 px
    img = Image.open(RADAR_IMAGE_PATH)
    img = img.resize((529, 560))
    img.save(RADAR_IMAGE_PATH)

generar_grafica_radar()

window = Tk()
window.attributes("-fullscreen", True)
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

button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_active_1 = PhotoImage(file=relative_to_assets("button_1.1.png"))
button_image_2 = PhotoImage(file=relative_to_assets("button_2.1.png"))
button_active_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
button_active_3 = PhotoImage(file=relative_to_assets("button_3.1.png"))

active_button = 2

def open_and_close(path):
    subprocess.Popen(["python", str(path)])
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

image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
canvas.create_image(1021.36, 123.83, image=image_image_2)

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
