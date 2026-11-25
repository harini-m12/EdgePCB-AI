from flask import Flask, jsonify, render_template

from database import initialize_database, get_inspections

app = Flask(__name__)

initialize_database()


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/api/history")
def history():

    records = get_inspections(100)

    return jsonify(records)


@app.route("/health")
def health():

    return jsonify({
        "status": "running",
        "device": "Raspberry Pi 4",
        "system": "EdgePCB-AI"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )