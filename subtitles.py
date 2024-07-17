# Ahora importa conf.py  # No necesitas ajustar sys.path ya que conf.py está en el mismo directorio
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ColorClip, vfx
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

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import conf
from moviepy.editor import VideoFileClip, CompositeAudioClip, TextClip, ColorClip, AudioFileClip
import os

def generate_subtitles(audio_path):
    # Función de ejemplo para generar subtítulos desde un archivo de audio
    # En la práctica, esto debería transcribir el audio y generar los tiempos de inicio y fin de cada línea de subtítulo
    return [
        {"start": 0, "end": 5, "text": "Texto de ejemplo 1"},
        {"start": 5, "end": 10, "text": "Texto de ejemplo 2"},
    ]


def style_generator(txt, style):
    
    # Fuentes modernas
    modern_fonts = ['Arial-Bold', 'Helvetica-Bold', 'Verdana-Bold']
    
    # Colores fluorescentes modernos
    modern_colors = ['#39FF14', '#FF00FF', '#00FFFF']
    
    # Colores de fondo modernos
    modern_bg_colors = ['#000000', '#FFFFFF', '#FF1493']
    
    # Colores de borde modernos
    modern_border_colors = ['#FF4500', '#32CD32', '#1E90FF']
    
    font = style.get('font', modern_fonts[0])
    fontsize = style.get('font_size', 24)
    color = style.get('color', modern_colors[0])
    border_color = style.get('border_color', modern_border_colors[0])
    bg_color = style.get('bg_color', 'transparent',modern_bg_colors[0] )
    return TextClip(txt, font=font, fontsize=fontsize, color=color, stroke_color=border_color, bg_color=bg_color)


# Bloque de prueba
if __name__ == "__main__":
    try:
        print("todo está bien")
    except Exception as e:
        print(f"Se produjo un error: {e}")