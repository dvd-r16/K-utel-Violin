from moviepy import VideoFileClip



# Ruta de tu video
video_path = r"D:\Desktop\K-utel-Violin\Video\build\assets\frame0\video2.mp4"
# Ruta donde guardarás el audio
audio_output_path = r"D:\Desktop\K-utel-Violin\Video\build\assets\frame0\audio2.mp3"

# Cargar el video
video = VideoFileClip(video_path)

# Extraer audio
audio = video.audio

# Guardar audio en un archivo mp3
audio.write_audiofile(audio_output_path)

print("[INFO] ¡Audio extraído correctamente!")
