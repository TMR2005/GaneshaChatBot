import os
import subprocess
import platform
import sounddevice as sd
import soundfile as sf

def speak(text: str, lang: str = "hi"):
    """
    Convert text to speech using Piper TTS and play it.
    
    Args:
        text (str): The text to convert to speech
        lang (str): Language code ("hi" for Hindi, "en" for English, etc.)
    """

    # Folder where piper.exe and voices live
    piper_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "piper")
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output.wav")

    # Detect piper binary (Windows vs Linux)
    if platform.system() == "Windows":
        piper_binary = os.path.join(piper_dir, "piper.exe")
    else:
        piper_binary = os.path.join(piper_dir, "piper")

    # Map language codes to voice model filenames
    lang_map = {
        "en": "en_GB-alan-medium",
        "hi": "hi_IN-pratham-medium"
    }

    if lang not in lang_map:
        raise ValueError(f"❌ Unsupported language '{lang}'. Available: {list(lang_map.keys())}")

    # Resolve paths to model + json
    model_name = lang_map[lang]
    model_path = os.path.join(piper_dir, f"{model_name}.onnx")
    json_path = os.path.join(piper_dir, f"{model_name}.onnx.json")
    print(f"Piper directory: {piper_dir}")
    print(f"Model path: {model_path}")
    print(f"JSON path: {json_path}")
    print(f"Model exists: {os.path.exists(model_path)}")
    print(f"JSON exists: {os.path.exists(json_path)}")
    if not os.path.exists(model_path) or not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ Model or config not found for {lang}: {model_name}")

    # Build Piper command
    command = [
        piper_binary,
        "-m", model_path,
        "-c", json_path,
        "-f", output_file
    ]

    print(f"🔊 Running Piper: {command}")

    # Run Piper (send text via stdin)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process.communicate(text.encode("utf-8"))
    process.wait()

 

if __name__ == "__main__":
    speak("Hello, how are you?", "en")