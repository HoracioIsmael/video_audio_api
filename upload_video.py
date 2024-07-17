import os
from google.cloud import storage
import random
import string

# Establece la variable de entorno dentro del script
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\horac\video_editor_api\video-editor-service-account.json'

# Función para generar un nombre de archivo aleatorio
def generate_random_filename(length=10):
    characters = string.ascii_letters + string.digits
    random_filename = ''.join(random.choice(characters) for _ in range(length))
    return f"{random_filename}.mp4"

# Función para subir el archivo a Google Cloud Storage
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

# Ejemplo de uso
if __name__ == "__main__":
    # Configura tu bucket
    bucket_name = "staging.video-editor-api.appspot.com"  # Reemplaza con el nombre de tu bucket
    source_file_name = r"C:\Users\horac\video_editor_api\static\videos\videop1.mp4"  # Ruta del archivo local
    destination_blob_name = generate_random_filename()  # Nombre del archivo en GCS

    # Sube el archivo y obtiene la URL pública
    public_url = upload_to_gcs(bucket_name, source_file_name, destination_blob_name)
    print(f"El archivo se ha subido exitosamente a {public_url}")
