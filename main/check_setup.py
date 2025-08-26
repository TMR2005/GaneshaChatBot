import importlib

packages = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "websockets",
    "python_multipart",
    "faster_whisper",
    "vosk",
    "langchain",
    "faiss",                 # faiss-cpu
    "sentence_transformers",
    "piper.voice",           # piper-tts
    "detoxify",
    "langdetect",
    "transformers",
    "accelerate",
    "torch",
    "torchvision",
    "torchaudio",
]

print("\n🔍 Checking installed packages...\n")
for pkg in packages:
    try:
        importlib.import_module(pkg)
        print(f"✅ {pkg}")
    except Exception as e:
        print(f"❌ {pkg} - {e}")

print("\nDone!\n")
