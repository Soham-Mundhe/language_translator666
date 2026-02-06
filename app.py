from flask import Flask, render_template, request, jsonify, send_from_directory
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import uuid

app = Flask(__name__)
VOICE_FOLDER = "static/audio"

if not os.path.exists(VOICE_FOLDER):
    os.makedirs(VOICE_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    try:
        text = request.form['text']
        source_lang = request.form['source_lang']
        target_lang = request.form['target_lang']

        if not text.strip():
            return jsonify({'error': 'Please enter some text.'})

        # Translate text
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)

        # Convert translated text to speech using gTTS
        tts = gTTS(text=translated, lang=target_lang)
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(VOICE_FOLDER, filename)
        tts.save(filepath)

        return jsonify({
            'input_text': text,
            'translated_text': translated,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'audio_url': f"/{filepath.replace(os.sep, '/')}"
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/static/audio/<filename>')
def get_audio(filename):
    return send_from_directory(VOICE_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
