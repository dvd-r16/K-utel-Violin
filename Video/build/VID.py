from moviepy import VideoFileClip

# Cargar el video
video = VideoFileClip(r"D:\Desktop\K-utel-Violin\Video\build\assets\frame0\video2.mp4")

# Reproducir el video con audio sincronizado
video.preview()