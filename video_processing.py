from .audio_processing import add_audio_to_video
#from .subtitles import add_subtitles_to_video
import os

def process_video(video_path, audio_path, subtitle_text, output_directory, styles, position):
    try:
        # Add audio to video
        video_with_audio_path = add_audio_to_video(video_path, audio_path)
        
        # Ensure the output directory exists
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        # Determine the next filename
        output_filename = get_next_filename(output_directory)
        output_path = os.path.join(output_directory, output_filename)

        # Add subtitles to video
        result = add_subtitles_to_video(video_with_audio_path, subtitle_text, output_path, styles, position)
        
        if result['status'] == 'success':
            result['output_path'] = output_path
        
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
