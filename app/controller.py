# backend/app.py
from flask import Flask, request, jsonify,g
from werkzeug.utils import secure_filename
from utils import extract_audio, split_audio,update_processing_progress
import os
from datetime import datetime


app = Flask(__name__)

# Configurations
app.config['UPLOAD_FOLDER'] = 'data/upload/'
app.config['OUTPUT_FOLDER'] = 'data/extracted_audio/'
app.config['AUDIO_CHUNKS_FOLDER'] = 'data/audio_chunks/'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mkv'}
app.config['processing_progress'] = {"current_step": 0, "total_steps": 2, "progress_percent": 0}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Function to create directories if they don't exist
def create_directories():
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['AUDIO_CHUNKS_FOLDER']]:
        os.makedirs(folder, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload_file():
    global processing_progress
    try:
        # Check and create directories if they don't exist
        create_directories()

        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
             # Save the file with the original filename
            original_filename = secure_filename(file.filename)
            original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            file.save(original_filepath)

            # Remove file extension from the original filename
            filename_without_extension = os.path.splitext(original_filename)[0]

            # Generate a unique filename with a timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_filename = f"{filename_without_extension}_{timestamp}.mp4"  # Adjust the prefix and extension as needed

            # Rename the file on the path
            new_filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            os.rename(original_filepath, new_filepath)

            return jsonify({"status": "success", "filename": new_filename, "message": "Video uploaded successfully"}), 200
    except Exception as e:
        # Log the exception
        app.logger.error(f"Error in upload_file: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Endpoint for extracting audio
@app.route('/extract_audio', methods=['POST'])
def extract_audio_endpoint():
    try:
        # Check and create directories if they don't exist
        create_directories()
        
        # Get filename from the request payload or URL
        filename = request.json.get('filename')  


        #Call the extract_audio method
        extracted_audio_path = extract_audio(os.path.join(app.config['UPLOAD_FOLDER'], filename),
                                        os.path.join(app.config['OUTPUT_FOLDER'], f'{filename}_audio.mp3'))



        return jsonify({"status": "success",filename:extracted_audio_path, "message": "Audio extracted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error while extracting audio: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Endpoint for splitting audio
@app.route('/split_audio', methods=['POST'])
def split_audio_endpoint():
    try:
        # Check and create directories if they don't exist
        create_directories()

        filename = request.json.get('filename')  

        extracted_audio_path= request.json.get('filename')

         # Split the audio into 15-minute intervals
        audio_chunks_path = split_audio(extracted_audio_path, app.config['AUDIO_CHUNKS_FOLDER'],filename)


        return jsonify({"status": "success", "message": "Audio split successfully","audio_path": audio_chunks_path}), 200
    except Exception as e:
        app.logger.error(f"Error while spiliting audio: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run(debug=True)