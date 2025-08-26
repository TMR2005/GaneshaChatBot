import subprocess
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from main.agent import get_ganesh_response
from main.tts import speak

app = Flask(__name__)
CORS(app)

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WHISPER_CLI_PATH = os.path.join(BASE_DIR, "whisper.cpp", "build", "bin", "whisper-cli")
MODEL_PATH = os.path.join(BASE_DIR, "whisper.cpp", "models", "ggml-medium.bin")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
CONVERTED_DIR = os.path.join(BASE_DIR, "converted")
TRANSCRIPTIONS_DIR = os.path.join(BASE_DIR, "transcriptions")
# --- ADDED: Directory for audio responses ---
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR)


os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTIONS_DIR, exist_ok=True)
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)


# --- ADDED: Helper function to convert Windows paths to WSL paths ---
def to_wsl_path(windows_path):
    """Converts a Windows path (e.g., D:\\folder\\file) to a WSL path (e.g., /mnt/d/folder/file)."""
    path_parts = windows_path.split(":", 1)
    if len(path_parts) != 2:
        return windows_path # Not a standard Windows path with a drive letter
    
    drive_letter = path_parts[0].lower()
    rest_of_path = path_parts[1].replace("\\", "/")
    return f"/mnt/{drive_letter}{rest_of_path}"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file uploaded"}), 400

        # --- 1. Save original audio file ---
        audio_file = request.files["audio"]
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}.webm")
        audio_file.save(input_path)

        # --- 2. Convert to WAV format ---
        wav_path = os.path.join(CONVERTED_DIR, f"{file_id}.wav")
        convert_cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            wav_path
        ]
        try:
            subprocess.run(convert_cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            return jsonify({"error": "ffmpeg command not found.", "details": "Please ensure ffmpeg is installed and in your system's PATH."}), 500
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "ffmpeg failed to convert audio.", "details": e.stderr}), 500

        # --- 3. Run Whisper.cpp for transcription ---
        transcript_base = os.path.join(TRANSCRIPTIONS_DIR, file_id)

        # --- CORRECTED: Convert all Windows paths to WSL paths before calling ---
        whisper_cmd = [
            "wsl",
            to_wsl_path(WHISPER_CLI_PATH),
            "-m", to_wsl_path(MODEL_PATH),
            "-f", to_wsl_path(wav_path),
            "-otxt",
            "-of", to_wsl_path(transcript_base),
            "-l", "auto"
        ]
        try:
            subprocess.run(whisper_cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            return jsonify({"error": "wsl or whisper-cli command not found.", "details": f"Ensure WSL is installed and the path is correct: {WHISPER_CLI_PATH}"}), 500
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "Whisper failed to transcribe audio.", "details": e.stderr}), 500

        # --- 4. Read the generated transcript file ---
        transcript_path = f"{transcript_base}.txt"
        if not os.path.exists(transcript_path):
            return jsonify({"error": "Transcription file not created by Whisper."}), 500

        with open(transcript_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        
        # Handle empty transcription
        if not text:
            # Create a "refusal" response object
            ganesha_response = GaneshResponse(
                lang='en',
                blessing_open='',
                answer='I am sorry, I could not hear anything in your message. Please speak clearly.',
                blessing_close='',
                refusal=True,
                refusal_reason='Empty transcription'
            )
            # You might want to generate a TTS for this refusal as well
            speak(ganesha_response.answer, ganesha_response.lang)

        else:
            print(f"Transcribed the text: {text}")
            ganesha_response = get_ganesh_response(text)
            print(f"Ganesha responded with: {ganesha_response.answer}")
            res = ganesha_response.blessing_open + ganesha_response.answer + ganesha_response.blessing_close
            speak(res, ganesha_response.lang)


        # --- 5. Return the result ---
        # **THE FIX IS HERE**: We call .to_dict() on the ganesha_response object
        # This assumes your GaneshResponse class has this method.
        return jsonify({
            "id": file_id,
            "transcription": text,
            "ganesha_response": ganesha_response.to_dict(),
            "audio_url": f"http://localhost:5000/audio/output.wav"
        })

    except Exception as e:
        return jsonify({"error": "An unexpected server error occurred.", "details": str(e)}), 500

# --- ADDED: Route to serve the generated audio file ---
@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serves the generated audio file from the 'main' directory."""
    return send_from_directory(AUDIO_OUTPUT_DIR, 'output.wav')

# --- ADDED: Import uuid if you haven't already ---
import uuid

# --- CORRECTED AND COMPLETE TEXT MESSAGE ROUTE ---
@app.route('/text-message', methods=['POST'])
def process_text_message():
    """
    Handles incoming text messages sent as JSON from the frontend.
    """
    try:
        # 1. Get the JSON data from the request body.
        data = request.get_json()

        # 2. Validate that the data and the 'message' key exist.
        if not data or 'message' not in data:
            return jsonify({"error": "Invalid request: JSON body must contain a 'message' key"}), 400
        
        text = data['message']

        # Handle case where the message string is empty
        if not text:
            return jsonify({"error": "Message cannot be empty"}), 400

        print(f"Agent received text: '{text}'")

        # --- Your Core Application Logic ---
        file_id = str(uuid.uuid4())
        ganesha_response = get_ganesh_response(text)
    
        # 3. Construct the JSON response to match the frontend's expected format
        return jsonify({
            "id": file_id,
            "transcription": text,  # The original text serves as the "transcription"
            "ganesha_response": ganesha_response.to_dict(), # Assumes your class has a .to_dict() method
        })

    except Exception as e:
        # Catch any other unexpected errors
        return jsonify({"error": "An unexpected server error occurred.", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
