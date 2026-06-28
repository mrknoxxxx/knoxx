```python
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "KNOXX API v2.1 ✅ MP3 + MP4 720p/1080p"


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(silent=True) or {}

    url = data.get("url")
    format_type = str(data.get("format", "mp3")).lower()
    quality = str(data.get("quality", "best"))

    if not url:
        return jsonify({"error": "URL dena zaroori hai!"}), 400

    unique_id = str(uuid.uuid4())
    outtmpl = f"{unique_id}.%(ext)s"
    filename = ""

    try:
        if format_type == "mp3":

            if not quality.isdigit():
                quality = "192"

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": quality
                }],
                "noplaylist": True,
                "quiet": True,
                "nocheckcertificate": True
            }

        else:

            if quality.isdigit():
                q = int(quality)

                if q > 1080:
                    quality = "1080"
                elif q < 144:
                    quality = "144"
            else:
                quality = "1080"

            ydl_opts = {
                "format": f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
                "outtmpl": outtmpl,
                "noplaylist": True,
                "quiet": True,
                "nocheckcertificate": True
            }

        # cookies.txt agar mojood ho tabhi use kare
        if os.path.exists("cookies.txt"):
            ydl_opts["cookiefile"] = "cookies.txt"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            ext = "mp3" if format_type == "mp3" else "mp4"
            filename = f"{unique_id}.{ext}"

            if not os.path.exists(filename):
                prepared = ydl.prepare_filename(info)

                alt = prepared.rsplit(".", 1)[0] + f".{ext}"

                if os.path.exists(alt):
                    filename = alt
                elif os.path.exists(prepared):
                    filename = prepared

        if not filename or not os.path.exists(filename):
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
        try:
            if filename and os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass

        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
```
