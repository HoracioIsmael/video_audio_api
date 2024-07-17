# app/routes.py
import json
import time
import random
import string
from flask import Flask, request, jsonify, render_template,  send_from_directory, url_for, Blueprint
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
import speech_recognition as sr
import subprocess 
from pydub import AudioSegment
import moviepy.video.fx.all as vfx
import whisper
import srt
from datetime import timedelta
import tempfile
import os

#from .services.video_processing import process_video
from .services.audio_processing import add_audio_to_video
from .services.subtitles import generate_subtitles
from google.cloud import storage
#from .services.subtitles import add_subtitles_to_video

app = Flask(__name__)

# Configurar rutas estáticas
app.config['STATIC_FOLDER'] = 'static'
app.config['VIDEO_FOLDER'] = os.path.join(app.config['STATIC_FOLDER'], 'videos')
app.config['DATA_FOLDER'] = os.path.join(app.config['STATIC_FOLDER'], 'data')

# Asegurarse de que las carpetas existen
os.makedirs(app.config['VIDEO_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

# Inicializar el modelo de Whisper
model = whisper.load_model("base")

def generate_random_filename(length=10):
    characters = string.ascii_letters + string.digits
    random_filename = ''.join(random.choice(characters) for _ in range(length))
    return f"{random_filename}.mp4"

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    # Inicializa el cliente de almacenamiento
    storage_client = storage.Client()

    # Obtén el bucket
    bucket = storage_client.bucket(bucket_name)

    # Crea un nuevo blob y sube el archivo
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    # Haz que el blob sea públicamente accesible
    blob.make_public()

    # Devuelve la URL pública del archivo
    return blob.public_url

def transcribe_audio(audio_path, language="es-ES"):
    try:
        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(audio_path)
        with audio_file as source:
            audio = recognizer.record(source)
        transcription = recognizer.recognize_google(audio, language=language)
        return transcription
    except sr.UnknownValueError as e:
        app.logger.error(f"Google Speech Recognition could not understand audio: {e}")
        raise
    except sr.RequestError as e:
        app.logger.error(f"Could not request results from Google Speech Recognition service; {e}")
        raise
    except Exception as e:
        app.logger.error(f"Error transcribing audio: {e}")
        raise

def create_subtitles(transcription, video, font_size=18, color='white', font='Arial', border_color='black', bg_color='black', position_x=10, position_y=20):
    try:
        # Divide la transcripción en bloques de 5 palabras
        words = transcription.split()
        subtitles = []
        duration = video.duration
        words_per_second = len(words) / duration

        block_size = 5
        for i in range(0, len(words), block_size):
            block = " ".join(words[i:i+block_size])
            start_time = (i / words_per_second) * (block_size / 5)
            end_time = ((i + block_size) / words_per_second) * (block_size / 5)
            text_clip = TextClip(block, fontsize=font_size, color=color, font=font, bg_color=bg_color, stroke_color=border_color)
            text_clip = text_clip.set_position((position_x, position_y)).set_start(start_time).set_duration(end_time - start_time)
            subtitles.append(text_clip)

        subtitle_video = CompositeVideoClip([video] + subtitles)
        return subtitle_video
    except Exception as e:
        app.logger.error(f"Error creating subtitles: {e}")
        raise

def convert_audio_to_wav(audio_path):
    try:
        audio = AudioSegment.from_file(audio_path)
        wav_path = os.path.splitext(audio_path)[0] + ".wav"
        audio.export(wav_path, format="wav")
        return wav_path
    except Exception as e:
        app.logger.error(f"Error converting audio to WAV: {e}")
        raise

def add_audio_to_video(video_path, audio_path, output_path, audio_music_volume=1.0, ia_voice_path=None, ia_voice_volume=1.0):
    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path).volumex(audio_music_volume)

        if ia_voice_path:
            ia_voice = AudioFileClip(ia_voice_path).volumex(ia_voice_volume)
            combined_audio = CompositeAudioClip([audio, ia_voice.set_start(0)])
        else:
            combined_audio = audio

        video = video.set_audio(combined_audio)
        return video
    except Exception as e:
        app.logger.error(f"Error adding audio to video: {e}")
        raise

def add_ia_voice_to_video(video_path, ia_voice_path, output_path, style, position, ia_voice_volume=1.0):
        try:
            video = VideoFileClip(video_path)
            audio = AudioFileClip(ia_voice_path).volumex(ia_voice_volume)
            audio = audio.set_duration(video.duration)
            video = video.set_audio(audio)
            subtitles = generate_subtitles(ia_voice_path)
            subtitle_clips = []
            for subtitle in subtitles:
                txt_clip = TextClip(
                    subtitle["text"],
                    fontsize=style['font_size'],
                    color=style['color'],
                    font=style['font'],
                    stroke_color=style['border_color'],
                    bg_color='#%02x%02x%02x' % style['bg_color']
                ).set_position((position['x'], position['y'])).set_start(subtitle["start"]).set_end(subtitle["end"])
                subtitle_clips.append(txt_clip)
            video_with_subtitles = CompositeVideoClip([video] + subtitle_clips)
            video_with_subtitles.write_videofile(output_path, codec='libx264')
            return output_path
        except Exception as e:
            raise ValueError(f"Error al agregar voz IA al video: {str(e)}")

# Ejemplo de uso
#if __name__ == "__main__":
    # Configura tu bucket
    #bucket_name = "staging.video-editor-api.appspot.com"  # Reemplaza con el nombre de tu bucket
    #source_file_name = r"C:\Users\horac\video_editor_api\static\videos\videop1.mp4"  # Ruta del archivo local
    #destination_blob_name = generate_random_filename()  # Nombre del archivo en GCS

    # Sube el archivo y obtiene la URL pública
    #public_url = upload_to_gcs(bucket_name, source_file_name, destination_blob_name)
    #print(f"El archivo se ha subido exitosamente a {public_url}")

def invert_add_audio(input_file, output_file, audio_file, audio_start_offset=2):
    video = VideoFileClip(input_file)
    
    # Verifica la resolución del video y redimensiona si es necesario
    if video.size != (1080, 1920):
        video = video.resize((1080, 1920))
    
    # Cambia la velocidad del video basado en su duración
    if video.duration > 55:
        video = video.fx(vfx.speedx, 1.3)
    
    inverted_video = video.fx(vfx.mirror_x)
    original_audio = inverted_video.audio.volumex(0)
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration
    audio_start_time = audio_start_offset

    # Verifica que la duración del audio no exceda la duración del video menos el offset
    if (audio_start_time + audio_duration) > inverted_video.duration:
        raise ValueError("La duración del audio excede la duración del video cuando se aplica el offset.")
    
    audio = audio.set_start(audio_start_time)
    combined_audio = CompositeAudioClip([original_audio, audio])
    final_audio_video = inverted_video.set_audio(combined_audio)
    final_audio_video.write_videofile(output_file, codec='libx264')

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')    
    
    def get_next_filename(directory, prefix='output_video_with_audio_', extension='.mp4'):
        existing_files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(extension)]
        if not existing_files:
            return f"{prefix}00000001{extension}"
        
        existing_files.sort()
        last_file = existing_files[-1]
        last_number = int(last_file[len(prefix):-len(extension)])
        next_number = last_number + 1
        next_filename = f"{prefix}{next_number:08d}{extension}"
        return next_filename  
    
    
        # Valores por defecto para nuevos estilos
        #modern_fonts = ['Arial-Bold', 'Helvetica-Bold', 'Verdana-Bold']
        #modern_colors = ['#39FF14', '#FF00FF', '#00FFFF']
        #modern_border_colors = ['#FF4500', '#32CD32', '#1E90FF']
        #modern_bg_colors = ['#000000', '#FFFFFF', '#FF1493']
        #font = data.get('font', modern_fonts[0])
        
    @app.route('/process_video', methods=['POST'])
    def process_video_endpoint():
        data = request.get_json()

        video_path = data['video_path']
        audio_music_path = data['audio_music_path']
        ia_voice_path = data.get('ia_voice_path')
        audio_music_volume = float(data.get('audio_music_volume', 1.0))
        ia_voice_volume = float(data.get('ia_voice_volume', 1.0))
        font_size = data.get('font_size', 18)
        color = data.get('color', '#FFFFFF')
        font = data.get('font', 'Arial')
        border_color = data.get('border_color', '#000000')
        bg_color = data.get('bg_color', '255,255,255')
        position_x = data.get('position_x', 0)
        position_y = data.get('position_y', 0)

        output_path = "C:\\Users\\horac\\video_editor_api\\app\\static\\videos\\output.mp4"

        try:
            app.logger.info("Starting to process video")
            video_with_audio = add_audio_to_video(video_path, audio_music_path, output_path, audio_music_volume, ia_voice_path, ia_voice_volume)

            if ia_voice_path:
                app.logger.info("Converting IA voice audio to WAV")
                wav_path = convert_audio_to_wav(ia_voice_path)
                app.logger.info("Transcribing IA voice audio")
                transcription = transcribe_audio(wav_path)
                app.logger.info("Creating subtitles")
                video_with_subtitles = create_subtitles(transcription, video_with_audio, font_size, color, font, border_color, bg_color, position_x, position_y)
            else:
                video_with_subtitles = video_with_audio

            app.logger.info("Writing final video to file")
            video_with_subtitles.write_videofile(output_path, codec='libx264')
            return jsonify({"output_video_path": output_path})
        except Exception as e:
            app.logger.error(f"Error processing video: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/get_video/<path:filename>')
    def serve_video(filename):
        return send_from_directory(os.path.join(app.config['STATIC_FOLDER'], 'videos'), filename)
        #return send_from_directory(app.config['VIDEO_DIRECTORY'], filename)
    
    @app.route('/list_videos', methods=['GET'])
    def list_videos():
        video_files = [f for f in os.listdir(os.path.join(app.config['STATIC_FOLDER'], 'videos')) if f.endswith('.mp4')]
        json_files = [f for f in os.listdir(os.path.join(app.config['STATIC_FOLDER'], 'data')) if f.endswith('.json')]
        return jsonify({"videos": video_files, "json_files": json_files})
        #video_files = [f for f in os.listdir(app.config['VIDEO_DIRECTORY']) if f.endswith('.mp4')]
        #json_files = [f for f in os.listdir(app.config['VIDEO_DIRECTORY']) if f.endswith('.json')]
    
    @app.route('/add_audio', methods=['POST'])
    def add_audio_endpoint():
        try:
            data = request.get_json()
            print("Datos recibidos:", data)  # Añadir esta línea
            if not data:
                return jsonify({"status": "error", "message": "Request body must be JSON"}), 400
        except Exception as e:
            print("Error al recibir los datos:", e)  # Añadir esta línea
            return jsonify({"status": "error", "message": str(e)}), 400

        video_path = data.get('video_path')
        audio_path = data.get('audio_path')
        
        print("Video Path:", video_path)  # Añadir esta línea
        print("Audio Path:", audio_path)  # Añadir esta línea

        if not video_path or not os.path.exists(video_path):
            return jsonify({"status": "error", "message": f"MoviePy error: the file {video_path} could not be found!\nPlease check that you entered the correct path."}), 400
        
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({"status": "error", "message": f"MoviePy error: the file {audio_path} could not be found!\nPlease check that you entered the correct path."}), 400

        result = add_audio_to_video(video_path, audio_path)
        return jsonify(result)

    @app.route('/generate_subtitles', methods=['POST'])
    def generate_subtitles_endpoint():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"status": "error", "message": "Request body must be JSON"}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        
        audio_path = data.get('audio_path')

        if not audio_path or not os.path.exists(audio_path):
            return jsonify({"error": "El archivo de audio no existe."}), 400

        subtitles = generate_subtitles(audio_path)

        return jsonify({"message": "Subtitles generated successfully", "subtitles": subtitles})

    return app

if __name__ == "__main__":
    app.run(debug=True)