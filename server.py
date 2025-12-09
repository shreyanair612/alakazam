import subprocess
import threading
import re
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

last_result = {"raw": "", "song": None, "score": None}

# helper function to parse through results

def parse_result_text(text):
    song = None
    score = None

    m_song = re.search(r"Detected song:\s*(.+)", text)
    if m_song:
        song = m_song.group(1).strip()

    m_score = re.search(r"Score:\s*(\d+)", text)
    if m_score:
        score = int(m_score.group(1))

    return song, score

# define routes that start & coordinate that background process thread

@app.route("/run", methods=["POST"])
def run_mqtt():
    def worker():
        global last_result

        proc = subprocess.Popen(
            ["python3", "mqtt_client.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        out, _ = proc.communicate()  # mqtt_client exits on its own
        song, score = parse_result_text(out)

        last_result = {
            "raw": out,
            "song": song,
            "score": score
        }

    threading.Thread(target=worker, daemon=True).start()
    return jsonify({"status": "listening"})

# routes to fetch results

@app.route("/last_result", methods=["GET"])
def last_result_route():
    return jsonify(last_result)

# entry point

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
