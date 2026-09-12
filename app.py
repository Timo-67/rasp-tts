"""
Маленький TTS-мост для проекта "Распиздяй".

Зачем он нужен: gTTS — это Python-библиотека, ESP32 не может вызвать её
напрямую. Поэтому ESP32 обращается по HTTP к этому серверу, а сервер
превращает текст в MP3 и отдаёт его в ответ. Задеплойте этот сервер
один раз на бесплатном хостинге (Render / Railway / PythonAnywhere) —
и дальше ваш ПК для работы горшка не нужен, только сам ESP32.

Локальный запуск для теста:
    pip install -r requirements.txt
    python app.py
    # затем откройте в браузере:
    # http://localhost:5000/tts?text=Привет&lang=ru
"""

from flask import Flask, request, Response, abort
from gtts import gTTS
import io

app = Flask(__name__)

MAX_TEXT_LEN = 500  # защита от слишком длинных/абузных запросов


@app.route("/tts", methods=["GET"])
def tts():
    text = request.args.get("text", "")
    lang = request.args.get("lang", "ru")

    if not text:
        abort(400, "Параметр 'text' обязателен")
    if len(text) > MAX_TEXT_LEN:
        text = text[:MAX_TEXT_LEN]

    try:
        tts_obj = gTTS(text=text, lang=lang)
        buf = io.BytesIO()
        tts_obj.write_to_fp(buf)
        buf.seek(0)
    except Exception as e:
        abort(500, f"Ошибка генерации речи: {e}")

    return Response(
        buf.read(),
        mimetype="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=speech.mp3"},
    )


@app.route("/", methods=["GET"])
def health():
    return "Распиздяй TTS-мост жив и здоров."


if __name__ == "__main__":
    # Для локального теста. На проде используйте gunicorn (см. Procfile).
    app.run(host="0.0.0.0", port=5000)
