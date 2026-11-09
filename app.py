import os
import time
import uuid
import logging
import io
import base64
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory
from gtts import gTTS

# Base directory for reliable cross-platform path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_FOLDER = os.path.join(BASE_DIR, "static", "audio")

try:
    os.makedirs(VOICE_FOLDER, exist_ok=True)
except OSError:
    pass

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_old_audio_files(folder, max_age_seconds=1800):
    """Remove generated audio files older than max_age_seconds (default 30 mins) to prevent disk exhaustion."""
    try:
        now = time.time()
        for filename in os.listdir(folder):
            if filename.endswith(".mp3"):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    if now - os.path.getmtime(file_path) > max_age_seconds:
                        try:
                            os.remove(file_path)
                        except OSError:
                            pass
    except Exception as e:
        logger.warning(f"Audio cleanup warning: {e}")


def translate_text_engine(text, source_lang="auto", target_lang="en"):
    """
    Robust translation engine:
    1. Primary: Direct Google Translate endpoint (fast, handles sentences, emojis, long text, bypasses 429 block).
    2. Fallback 1: deep_translator GoogleTranslator.
    3. Fallback 2: deep_translator MyMemoryTranslator.
    """
    if source_lang == target_lang and source_lang != "auto":
        return text, source_lang

    # 1. Primary endpoint
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_lang if source_lang else "auto",
            "tl": target_lang if target_lang else "en",
            "dt": "t",
            "q": text,
        }
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, params=params, headers=headers, timeout=12)
        if response.status_code == 200:
            data = response.json()
            translated = "".join([segment[0] for segment in data[0] if segment and segment[0]])
            detected = (
                data[2]
                if len(data) > 2 and isinstance(data[2], str)
                else (source_lang if source_lang != "auto" else "unknown")
            )
            if translated and translated.strip():
                return translated.strip(), detected
    except Exception as e:
        logger.warning(f"Primary translation failed: {e}")

    # 2. Fallback: deep-translator GoogleTranslator
    try:
        from deep_translator import GoogleTranslator
        src = "auto" if source_lang == "auto" else source_lang
        res = GoogleTranslator(source=src, target=target_lang).translate(text)
        if res and res.strip():
            return res.strip(), source_lang
    except Exception as e:
        logger.warning(f"Fallback GoogleTranslator failed: {e}")

    # 3. Fallback: deep-translator MyMemoryTranslator
    try:
        from deep_translator import MyMemoryTranslator
        src = "en" if source_lang == "auto" else source_lang
        res = MyMemoryTranslator(source=src, target=target_lang).translate(text)
        if res and res.strip():
            return res.strip(), source_lang
    except Exception as e:
        logger.warning(f"Fallback MyMemoryTranslator failed: {e}")

    raise RuntimeError("Unable to translate text at this moment. Please check your connection and try again.")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint for deployment monitoring (Render, Railway, Vercel, AWS, Docker)."""
    return jsonify({"status": "healthy", "service": "language_translator"}), 200


@app.route("/translate", methods=["POST"])
def translate():
    try:
        # Support both form data and JSON payloads
        if request.is_json:
            data = request.get_json(silent=True) or {}
            text = data.get("text", "")
            source_lang = data.get("source_lang", "auto")
            target_lang = data.get("target_lang", "en")
        else:
            text = request.form.get("text", "")
            source_lang = request.form.get("source_lang", "auto")
            target_lang = request.form.get("target_lang", "en")

        if not text or not text.strip():
            return jsonify({"error": "Please enter some text to translate."}), 400

        text = text.strip()
        source_lang = (source_lang or "auto").strip()
        target_lang = (target_lang or "en").strip()

        # Target language cannot be "auto"
        if target_lang == "auto":
            target_lang = "en"

        # Translate text
        translated, detected_lang = translate_text_engine(
            text, source_lang=source_lang, target_lang=target_lang
        )

        # Generate audio TTS if possible (graceful fallback if TTS fails)
        audio_url = None
        try:
            # Limit TTS text to first 500 characters to prevent timeouts on large inputs
            tts_text = translated[:500].strip()
            if tts_text:
                tts = gTTS(text=tts_text, lang=target_lang)
                # In serverless environments (Vercel) or read-only filesystems,
                # generate audio in-memory as a Base64 data URL
                try:
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    b64_audio = base64.b64encode(fp.read()).decode("utf-8")
                    audio_url = f"data:audio/mp3;base64,{b64_audio}"
                except Exception as mem_err:
                    cleanup_old_audio_files(VOICE_FOLDER, max_age_seconds=1800)
                    filename = f"{uuid.uuid4().hex}.mp3"
                    filepath = os.path.join(VOICE_FOLDER, filename)
                    tts.save(filepath)
                    audio_url = f"/static/audio/{filename}"
        except Exception as tts_err:
            logger.info(f"gTTS audio generation skipped or unavailable: {tts_err}")
            audio_url = None

        return jsonify({
            "success": True,
            "input_text": text,
            "translated_text": translated,
            "source_lang": source_lang,
            "detected_lang": detected_lang,
            "target_lang": target_lang,
            "audio_url": audio_url,
        })
    except Exception as e:
        logger.error(f"Translation route error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/static/audio/<path:filename>")
def get_audio(filename):
    """Explicit audio serving endpoint with correct audio/mpeg MIME type."""
    return send_from_directory(VOICE_FOLDER, filename, mimetype="audio/mpeg")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(host="0.0.0.0", port=port, debug=debug)
