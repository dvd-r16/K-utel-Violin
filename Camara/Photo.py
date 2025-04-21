import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import datetime

class CamaraApp:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Captura de Foto - Raspberry Pi")

        # Abrimos la cámara
        self.cap = cv2.VideoCapture(0)

        # Crear etiqueta donde se verá la imagen en vivo
        self.etiqueta_video = Label(ventana)
        self.etiqueta_video.pack()

        # Botón para capturar imagen
        self.boton_captura = Button(ventana, text="Capturar", command=self.capturar_imagen, bg="#4CAF50", fg="white", font=("Arial", 14))
        self.boton_captura.pack(pady=10)

        # Empezamos a actualizar la imagen
        self.actualizar_video()

        # Cerrar correctamente
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)

    def actualizar_video(self):
        ret, frame = self.cap.read()
        if ret:
            # Convertimos el frame a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = Image.fromarray(frame)
            imagen_tk = ImageTk.PhotoImage(image=imagen)

            self.etiqueta_video.imgtk = imagen_tk
            self.etiqueta_video.configure(image=imagen_tk)

        self.ventana.after(10, self.actualizar_video)

    def capturar_imagen(self):
        ret, frame = self.cap.read()
        if ret:
            nombre_archivo = datetime.datetime.now().strftime("captura_%Y%m%d_%H%M%S.jpg")
            cv2.imwrite(nombre_archivo, frame)
            print(f"📷 Imagen guardada como {nombre_archivo}")

    def cerrar(self):
        self.cap.release()
        self.ventana.destroy()

# Ejecutar la app
if __name__ == "__main__":
    ventana = tk.Tk()
    app = CamaraApp(ventana)
    ventana.mainloop()
