from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import subprocess

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"

BASE_PATH = Path(__file__).resolve().parent.parent.parent
seleccion_path = BASE_PATH / "usuario_seleccionado.txt"
usuarios_path = BASE_PATH / "Login" / "usuarios"

LOGIN_GUI_PATH = BASE_PATH / "Login" / "build" / "gui.py"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()
window.attributes("-fullscreen", True)

def salir_fullscreen(event=None):
    window.destroy()

window.bind("<Escape>", salir_fullscreen)
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
canvas.create_rectangle(6.0, 0.0, 720.0, 450.0, fill="#32457D", outline="")

# Imagen fija
image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(720.0, 450.0, image=image_image_1)

# Botones con estados activos
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_active_1 = PhotoImage(file=relative_to_assets("button_1.1.png"))
button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_active_2 = PhotoImage(file=relative_to_assets("button_2.1.png"))
button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
button_active_3 = PhotoImage(file=relative_to_assets("button_3.1.png"))

active_button = None

def open_login_gui():
    subprocess.Popen(["python", str(LOGIN_GUI_PATH)])
    window.after(1000, window.destroy)  # Cierra esta ventana 1 segundo después

def activate_button(button):
    global active_button
    if active_button == button:
        if button == 1:
            button_1.config(image=button_image_1)
        elif button == 2:
            button_2.config(image=button_image_2)
        elif button == 3:
            button_3.config(image=button_image_3)
        active_button = None
        return
    button_1.config(image=button_image_1)
    button_2.config(image=button_image_2)
    button_3.config(image=button_image_3)
    if button == 1:
        button_1.config(image=button_active_1)
        open_login_gui()
    elif button == 2:
        button_2.config(image=button_active_2)
    elif button == 3:
        button_3.config(image=button_active_3)
    active_button = button

button_1 = Button(image=button_image_1, borderwidth=0, highlightthickness=0, bg="#32457D", activebackground="#32457D", command=lambda: activate_button(1), relief="flat")
button_1.place(x=118.0, y=45.0, width=182.0, height=81.0)

button_2 = Button(image=button_image_2, borderwidth=0, highlightthickness=0, bg="#32457D", activebackground="#32457D", command=lambda: activate_button(2), relief="flat")
button_2.place(x=345.0, y=45.0, width=300.0, height=81.0)

button_3 = Button(image=button_image_3, borderwidth=0, highlightthickness=0, bg="#32457D", activebackground="#32457D", command=lambda: activate_button(3), relief="flat")
button_3.place(x=690.0, y=45.0, width=180.0, height=81.0)

# Botones normales
button_image_4 = PhotoImage(file=relative_to_assets("button_4.png"))
button_4 = Button(image=button_image_4, borderwidth=0, highlightthickness=0, bg="#32457D", activebackground="#32457D", command=lambda: print("button_4 clicked"), relief="flat")
button_4.place(x=54.0, y=188.0, width=259.0, height=259.0)

button_image_5 = PhotoImage(file=relative_to_assets("button_5.png"))
button_image_5_1 = PhotoImage(file=relative_to_assets("button_5.1.png"))
button_5 = Button(image=button_image_5, borderwidth=0, highlightthickness=0, bg="#32457D", activebackground="#32457D", command=lambda: print("button_5 clicked"), relief="flat")
button_5.place(x=340.0, y=188.0, width=259.0, height=259.0)

button_image_6 = PhotoImage(file=relative_to_assets("button_6.png"))
button_image_6_1 = PhotoImage(file=relative_to_assets("button_6.1.png"))
button_6 = Button(image=button_image_6, borderwidth=0, highlightthickness=0, bg="#32457D", activebackground="#32457D", command=lambda: print("button_6 clicked"), relief="flat")
button_6.place(x=54.0, y=472.0, width=259.0, height=259.0)

button_image_7 = PhotoImage(file=relative_to_assets("button_7.png"))
button_image_7_1 = PhotoImage(file=relative_to_assets("button_7.1.png"))
button_7 = Button(image=button_image_7, borderwidth=0, highlightthickness=0, bg="#32457D", activebackground="#32457D", command=lambda: print("button_7 clicked"), relief="flat")
button_7.place(x=340.0, y=472.0, width=259.0, height=259.0)

original_buttons_state = {
    5: button_image_5,
    6: button_image_6,
    7: button_image_7
}

image_image_10 = PhotoImage(file=relative_to_assets("image_10.png"))
image_image_10_1 = PhotoImage(file=relative_to_assets("image_10.1.png"))
image_image_10_2 = PhotoImage(file=relative_to_assets("image_10.2.png"))
image_image_10_3 = PhotoImage(file=relative_to_assets("image_10.3.png"))
image_10 = canvas.create_image(1064.0, 85.0, image=image_image_10)

image_image_11 = PhotoImage(file=relative_to_assets("image_11.png"))
canvas.create_image(1264.0, 85.0, image=image_image_11)

# Grupo B y G
image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(768.0, 432.0, image=image_image_2, state='hidden')

image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(935.0, 305.0, image=image_image_3, state='hidden')
image_image_4 = PhotoImage(file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(1355.0, 200.0, image=image_image_4, state='hidden')
image_image_5 = PhotoImage(file=relative_to_assets("image_5.png"))
image_5 = canvas.create_image(1395.0, 406.0, image=image_image_5, state='hidden')
image_image_6 = PhotoImage(file=relative_to_assets("image_6.png"))
image_6 = canvas.create_image(872.0, 379.0, image=image_image_6, state='hidden')
image_image_7 = PhotoImage(file=relative_to_assets("image_7.png"))
image_7 = canvas.create_image(1311.0, 378.0, image=image_image_7, state='hidden')
image_image_8 = PhotoImage(file=relative_to_assets("image_8.png"))
image_8 = canvas.create_image(963.0, 415.0, image=image_image_8, state='hidden')


image_image_9 = PhotoImage(file=relative_to_assets("image_9.png"))
image_9 = canvas.create_image(768.0, 432.0, image=image_image_9, state='hidden')



image_image_15 = PhotoImage(file=relative_to_assets("image_15.png"))
image_15 = canvas.create_image(768.0, 432.0, image=image_image_15, state='hidden')

image_image_16 = PhotoImage(file=relative_to_assets("image_16.png"))
image_16 = canvas.create_image(735.77, 428.77, image=image_image_16, state='hidden')
image_image_17 = PhotoImage(file=relative_to_assets("image_17.png"))
image_17 = canvas.create_image(706.70, 535.70, image=image_image_17, state='hidden')
image_image_18 = PhotoImage(file=relative_to_assets("image_18.png"))
image_18 = canvas.create_image(1150.74, 279.74, image=image_image_18, state='hidden')
image_image_20 = PhotoImage(file=relative_to_assets("image_20.png"))
image_20 = canvas.create_image(780.0, 262.0, image=image_image_20, state='hidden')
image_image_21 = PhotoImage(file=relative_to_assets("image_21.png"))
image_21 = canvas.create_image(1141.0, 179.0, image=image_image_21, state='hidden')
image_image_22 = PhotoImage(file=relative_to_assets("image_22.png"))
image_22 = canvas.create_image(1273.0, 317.0, image=image_image_22, state='hidden')

image_image_19 = PhotoImage(file=relative_to_assets("image_19.png"))
image_19 = canvas.create_image(777.0, 436.0, image=image_image_19, state='hidden')



b_extra_images = {1: [image_3, image_7], 2: [image_5, image_8], 3: [image_4, image_6]}
g_extra_images = {1: [image_18, image_22], 2: [image_17, image_20], 3: [image_16, image_21]}

current_b_state = 0
current_g_state = 0
b_visible = False
g_visible = False

def toggle_b(event=None):
    global b_visible
    b_visible = not b_visible
    canvas.itemconfigure(image_2, state='normal' if b_visible else 'hidden')
    canvas.itemconfigure(image_9, state='normal' if b_visible else 'hidden')
    if not b_visible:
        for imgs in b_extra_images.values():
            for img in imgs:
                canvas.itemconfigure(img, state='hidden')

def toggle_g(event=None):
    global g_visible
    g_visible = not g_visible
    canvas.itemconfigure(image_15, state='normal' if g_visible else 'hidden')
    canvas.itemconfigure(image_19, state='normal' if g_visible else 'hidden')
    if not g_visible:
        for imgs in g_extra_images.values():
            for img in imgs:
                canvas.itemconfigure(img, state='hidden')

def set_state_zero(event=None):
    global current_b_state, current_g_state
    canvas.itemconfig(image_10, image=image_image_10)
    button_5.config(image=original_buttons_state[5])
    button_6.config(image=original_buttons_state[6])
    button_7.config(image=original_buttons_state[7])
    for imgs in b_extra_images.values():
        for img in imgs:
            canvas.itemconfigure(img, state='hidden')
    for imgs in g_extra_images.values():
        for img in imgs:
            canvas.itemconfigure(img, state='hidden')
    current_b_state = 0
    current_g_state = 0

def set_state_one(event=None):
    global current_b_state, current_g_state
    canvas.itemconfig(image_10, image=image_image_10_1)
    button_5.config(image=button_image_5_1)
    if b_visible:
        for img in b_extra_images[1]:
            canvas.itemconfigure(img, state='normal')
    if g_visible:
        for img in g_extra_images[1]:
            canvas.itemconfigure(img, state='normal')
    current_b_state = max(current_b_state, 1)
    current_g_state = max(current_g_state, 1)

def set_state_two(event=None):
    global current_b_state, current_g_state
    canvas.itemconfig(image_10, image=image_image_10_2)
    button_6.config(image=button_image_6_1)
    if b_visible and current_b_state >= 1:
        for img in b_extra_images[2]:
            canvas.itemconfigure(img, state='normal')
    if g_visible and current_g_state >= 1:
        for img in g_extra_images[2]:
            canvas.itemconfigure(img, state='normal')
    current_b_state = max(current_b_state, 2)
    current_g_state = max(current_g_state, 2)

def set_state_three(event=None):
    global current_b_state, current_g_state
    canvas.itemconfig(image_10, image=image_image_10_3)
    button_7.config(image=button_image_7_1)
    if b_visible and current_b_state >= 2:
        for img in b_extra_images[3]:
            canvas.itemconfigure(img, state='normal')
    if g_visible and current_g_state >= 2:
        for img in g_extra_images[3]:
            canvas.itemconfigure(img, state='normal')
    current_b_state = max(current_b_state, 3)
    current_g_state = max(current_g_state, 3)

window.bind("0", set_state_zero)
window.bind("1", set_state_one)
window.bind("2", set_state_two)
window.bind("3", set_state_three)

try:
    if seleccion_path.exists():
        with open(seleccion_path, "r", encoding="utf-8") as f:
            user_id = f.read().strip()
            print(f"[INFO] Usuario seleccionado: {user_id}")

        user_file = usuarios_path / f"user_{user_id}.txt"

        if user_file.exists():
            print(f"[INFO] Información de user_{user_id}.txt:")
            genero = ""
            with open(user_file, "r", encoding="utf-8") as f_user:
                for line in f_user:
                    print(line.strip())
                    if "Género:" in line:
                        genero = line.split(":")[1].strip().lower()

            # Activar grupo según género
            if genero == "masculino":
                print("[INFO] Activando grupo B (masculino)")
                toggle_b()
            elif genero == "femenino":
                print("[INFO] Activando grupo G (femenino)")
                toggle_g()
            else:
                print("[WARN] Género no reconocido:", genero)
        else:
            print(f"[ERROR] El archivo del usuario no existe: {user_file}")
    else:
        print(f"[ERROR] El archivo 'usuario_seleccionado.txt' no fue encontrado.")
except Exception as e:
    print(f"[ERROR] Al leer la información del usuario: {e}")

window.resizable(False, False)
window.mainloop()