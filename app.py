from flask import Flask, request, Response, abort
from gtts import gTTS
from pydub import AudioSegment
import io

app = Flask(__name__)
MAX_TEXT_LEN = 500

def apply_character_voice(mp3_bytes: bytes, pitch_factor: float) -> bytes:
    audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
    new_rate = int(audio.frame_rate * pitch_factor)
    shifted = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
    shifted = shifted.set_frame_rate(audio.frame_rate)
    out = io.BytesIO()
    shifted.export(out, format="mp3")
    return out.getvalue()

@app.route("/tts", methods=["GET"])
def tts():
    text = request.args.get("text", "")
    lang = request.args.get("lang", "ru")
    # < 1.0 — голос ниже и грубее ("ворчливый дед"), > 1.0 — выше и быстрее
    pitch = float(request.args.get("pitch", 1.3))
    pitch = max(0.5, min(pitch, 1.5))  # защита от экстремальных значений

    if not text:
        abort(400, "Параметр 'text' обязателен")
    if len(text) > MAX_TEXT_LEN:
        text = text[:MAX_TEXT_LEN]

    try:
        buf = io.BytesIO()
        gTTS(text=text, lang=lang).write_to_fp(buf)
        mp3_bytes = apply_character_voice(buf.getvalue(), pitch)
    except Exception as e:
        abort(500, f"Ошибка генерации речи: {e}")

    return Response(mp3_bytes, mimetype="audio/mpeg")

@app.route("/", methods=["GET"])
def health():
    return "Распиздяй TTS-мост жив и здоров."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
