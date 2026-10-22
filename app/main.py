"""Petite API Flask utilisée pour le TP2 DevSecOps."""
import os
import sqlite3
import subprocess
import tempfile

from flask import Flask, abort, jsonify, request

DB_PATH = os.environ.get("DB_PATH", os.path.join(tempfile.gettempdir(), "app.db"))

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT OR IGNORE INTO users (id, name) VALUES (1, 'alice'), (2, 'bob')")


@app.after_request
def security_headers(response):
    # En-têtes de sécurité vérifiés par le scan DAST (OWASP ZAP)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.errorhandler(404)
def not_found(_error):
    return jsonify(error="not found"), 404


@app.route("/")
def index():
    return jsonify(message="TP2 DevSecOps API", routes=["/health", "/users/<id>"])


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/users/<int:user_id>")
def get_user(user_id):
    with get_db() as conn:
        # Requête paramétrée : pas d'injection SQL possible
        row = conn.execute("SELECT id, name FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        abort(404)
    return jsonify(id=row["id"], name=row["name"])


@app.route("/ping")
def ping():
    # VULNERABLE : l'entrée utilisateur est passée à un shell (injection de commande)
    host = request.args.get("host", "127.0.0.1")
    result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True, text=True)
    return jsonify(output=result.stdout + result.stderr)


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
