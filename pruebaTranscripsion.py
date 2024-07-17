from flask import Flask
import speech_recognition as sr

app = Flask(__name__)

def transcribe_audio_with_timestamps(audio_path, language="es-ES"):
    with app.app_context():
        print("Iniciando transcripción...")
        try:
            recognizer = sr.Recognizer()
            audio_file = sr.AudioFile(audio_path)
            with audio_file as source:
                audio = recognizer.record(source)

            transcription = recognizer.recognize_google(audio, language=language, show_all=True)
            print("Transcripción completa. Procesando...")

            # Imprimir la transcripción completa
            print("Transcripción raw:", transcription)

            words = []
            if 'results' in transcription:
                for result in transcription['results']:
                    if 'alternatives' in result:
                        for alternative in result['alternatives']:
                            if 'words' in alternative:
                                for word in alternative['words']:
                                    start_time = float(word['startTime'].replace('s', ''))
                                    end_time = float(word['endTime'].replace('s', ''))
                                    word_text = word['word']
                                    words.append({
                                        'word': word_text,
                                        'startTime': start_time,
                                        'endTime': end_time
                                    })

            return words
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return []
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return []
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return []

if __name__ == "__main__":
    audio_path = "C:\\Users\\horac\\video_editor_api\\app\\static\\videos\\audioPruebaSubtitulos.wav"
    with app.app_context():
        transcriptions = transcribe_audio_with_timestamps(audio_path)
        if transcriptions:
            for t in transcriptions:
                print(t)
        else:
            print("No se encontraron subtítulos.")
