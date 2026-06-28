from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "KNOXX Downloader API is Running ✅"


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(silent=True) or {}

    url = data.get("url")
    download_type = data.get("type", "video")

    if not url:
        return jsonify({"error": "URL dena zaroori hai!"}), 400

    unique_id = str(uuid.uuid4())
    outtmpl = f"{unique_id}.%(ext)s"

    if download_type == "video":
        ydl_opts = {
            "format": "b[ext=mp4]/best",
            "outtmpl": outtmpl,
            "noplaylist": True,
            "quiet": True,
            "nocheckcertificate": True,
        }

    else:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "noplaylist": True,
            "quiet": True,
            "nocheckcertificate": True,
        }

    # Agar cookies.txt mojood ho to use kare
    if os.path.exists("cookies.txt"):
        ydl_opts["cookiefile"] = "cookies.txt"

    filename = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if download_type == "audio":
                filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
            else:
                filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            return jsonify({"error": "Downloaded file not found."}), 500

        @after_this_request
        def remove_file(response):
            try:
                if filename and os.path.exists(filename):
                    os.remove(filename)
            except Exception:
                pass
            return response

        return send_file(filename, as_attachment=True)

    except Exception as e:
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception:
                pass

        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
