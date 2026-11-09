# 🌐 AI Language Translator

> *The first project at first year: a modern, responsive language translator with voice input & speech synthesis.*

A full-stack web application for multi-language translation, speech-to-text, and voice synthesis (Text-to-Speech) built with Flask and Python.

---

## ✨ Features

- **Multi-Language Support**: Translates between 35+ major world and regional languages with Auto-Detection.
- **Fast & Resilient Translation**: Primary high-speed translation engine with fallbacks so translations never fail with 429/CAPTCHA blocks.
- **Voice Synthesis (TTS)**: Listens to the translation spoken aloud in the target language (gTTS and Web Speech API).
- **Speech Recognition (STT)**: Speak into your microphone and convert speech to text with animated recording status.
- **Auto-Cleanup**: Automatically cleans up temporary audio files every 30 minutes to prevent disk bloat.
- **Smart Swapping**: Swaps languages and current text without breaking auto-detection.
- **Modern UI / UX**:
  - Light & Dark mode (persisted across sessions).
  - One-click copy translation with feedback.
  - Live character counter.
  - Keyboard shortcut: <kbd>Ctrl</kbd> + <kbd>Enter</kbd> (or <kbd>Cmd</kbd> + <kbd>Enter</kbd>).
  - Fully mobile-responsive.
- **Production-Ready**: Configured for Render, Railway, Docker, Heroku, AWS, and Cloud Run.

---

## 🚀 Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/Soham-Mundhe/language_translator666.git
cd language_translator666
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🚢 Deployment Guide

### Option 1: Deploy on Vercel (One-Click Serverless)
1. Fork or push this repository to GitHub.
2. Sign in to [Vercel](https://vercel.com) and click **Add New...** -> **Project**.
3. Import your `language_translator666` repository.
4. Vercel automatically detects `vercel.json` and `api/index.py`. Click **Deploy**.
5. Your application is instantly live with zero configuration!

---

### Option 2: Deploy on Render (Recommended - Free Tier)
1. Fork or push this repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click **Create Web Service**. Render will build and deploy your app with a live HTTPS URL.

---

### Option 3: Deploy on Railway
1. Sign in to [Railway](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select this repository.
4. Railway will automatically detect `Procfile` / `requirements.txt` and deploy.

---

### Option 4: Deploy with Docker
1. Build the Docker image:
```bash
docker build -t language-translator .
```
2. Run the container:
```bash
docker run -p 5000:5000 language-translator
```
3. Visit `http://localhost:5000`.

---

### Option 5: Deploy on Heroku
```bash
heroku create my-language-translator
git push heroku main
```

---

## 📂 Project Structure

```text
├── api/
│   └── index.py        # Vercel Serverless Function entry point
├── vercel.json         # Vercel routing and rewrite configuration
├── app.py              # Main Flask application & translation logic
├── requirements.txt    # Production dependencies
├── Procfile            # Deployment start command for Render / Heroku / Railway
├── runtime.txt         # Python runtime version
├── Dockerfile          # Container build configuration
├── .dockerignore       # Ignored files for Docker build
├── .gitignore          # Git ignore configuration
├── templates/
│   └── index.html      # Responsive frontend UI
└── static/
    └── audio/          # Generated temporary voice audio files (.gitkeep)
```

---

## 🛡 License
MIT License
