# 🚀 GaneshaBot: Installation & Setup Guide

This is a detailed guide to get the GaneshaBot project running on your local machine.

---

## ✅ Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python** 3.8+
* **Node.js** and **npm**
* A **C++ compiler** (like g++ or clang) for building `whisper.cpp`.
* **Git** for version control.
* **ffmpeg** for audio processing.

---

## ⚙️ Installation Steps

Follow these steps to set up both the backend and frontend components of the application.

### 1. Clone the Main Repository

First, clone this repository to your local machine using Git.

```bash
git clone https://github.com/TMR2005/GaneshaChatBot.git
cd ganeshabot
```

Of course. Here is the installation guide formatted as a GitHub Markdown file.

Markdown

# 🚀 GaneshaBot: Installation & Setup Guide

This is a detailed guide to get the GaneshaBot project running on your local machine.

---

## ✅ Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python** 3.8+
* **Node.js** and **npm**
* A **C++ compiler** (like g++ or clang) for building `whisper.cpp`.
* **Git** for version control.
* **ffmpeg** for audio processing.

---

## ⚙️ Installation Steps

Follow these steps to set up both the backend and frontend components of the application.

### 1. Clone the Main Repository

First, clone this repository to your local machine using Git.

```bash
git clone [https://github.com/your-username/ganeshabot.git](https://github.com/your-username/ganeshabot.git)
cd ganeshabot
```

### 2. Backend Setup
This involves setting up the Python environment, building the transcription model, and preparing the knowledge base.

#### a. Install ffmpeg
ffmpeg is required for audio processing and must be accessible from your system's PATH.

Windows: Download the binaries from ffmpeg.org and add the bin folder to your system's PATH.

macOS (using Homebrew): brew install ffmpeg

Linux (Debian/Ubuntu): sudo apt update && sudo apt install ffmpeg

#### b. Set Up Whisper.cpp for Transcription
We will clone and build whisper.cpp inside the backend folder.

```bash
# Navigate to the backend directory from the project root
cd backend

# Clone the whisper.cpp repository
git clone [https://github.com/ggerganov/whisper.cpp.git](https://github.com/ggerganov/whisper.cpp.git)

# Navigate into the whisper.cpp directory and build it
cd whisper.cpp
make

# Download the ggml-medium.bin model
cd model
bash ./models/download-ggml-model.sh medium

# Go back to the backend directory
cd ..
```

#### c. Download LLM and TTS Models
You need to download the language model and the text-to-speech models and place them in a models directory inside the backend folder.

GPT4All Llama 3 8B Instruct: Download the model file from the GPT4All website. Place the downloaded .gguf file into backend/models/.

Piper TTS Model: Download your desired voice model from the Piper models page. You will need both the .onnx and .onnx.json files. Place them in backend/models/ as well.

Install gpt4all and install the Llama 3 8B instrcut model, paste the correct path in the models path in agent.py

##### d. Python Dependencies
```bash
pip install -r requirements.txt
```

#### 5.For RAG, run the embed.py once
```bash
cd main
python embed.py
```

#### 6. Run the backend app.py
```bash
cd ..
python app.py
```


