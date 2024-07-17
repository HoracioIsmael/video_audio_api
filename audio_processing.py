# app/services/audio_processing.py
import sys
import os

# Asegúrate de que el directorio donde está `conf.py` está en el PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import conf

from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

import moviepy.editor as mp

# Bloque de prueba
if __name__ == "__main__":
    try:
        # Ejecuta alguna función de prueba para verificar la configuración
        # Por ejemplo, si tienes una función principal llamada main(), puedes llamarla aquí
        # main()  
        
        # Imprime "todo está bien" si no hay problemas
        print("todo está bien")
    except Exception as e:
        # Imprime el error si hay algún problema
        print(f"Se produjo un error: {e}")

def add_audio_to_video(video_path, audio_path):
    try:
        video = mp.VideoFileClip(video_path)
        audio = mp.AudioFileClip(audio_path)
        
        video = video.set_audio(audio)
        output_path = video_path.replace('.mp4', '_with_audio.mp4')
        video.write_videofile(output_path, codec='libx264', audio_codec='aac')

        return output_path
    except Exception as e:
        return {"status": "error", "message": str(e)}


