import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request


app = Flask(__name__)

DB_PATH = Path(__file__).resolve().parent / "auditoria.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


@app.post("/audit")
def create_audit():
    data = request.get_json(silent=True)

    if isinstance(data, dict):
        person_id = data.get("person_id") or data.get("persona_id") or data.get("id_persona")
        mensaje = data.get("message") or data.get("mensaje")
    else:
        person_id = None
        mensaje = None

    if not person_id or not mensaje:
        return (
            jsonify(
                {
                    "error": "Debes enviar person_id y message en el body JSON"
                }
            ),
            400,
        )

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO auditoria (person_id, mensaje) VALUES (?, ?)",
            (str(person_id), mensaje),
        )
        conn.commit()

    return (
        jsonify(
            {
                "id": cursor.lastrowid,
                "person_id": str(person_id),
                "mensaje": mensaje,
                "detalle": "Registro guardado correctamente",
            }
        ),
        201,
    )


@app.get("/audit")
def list_audits():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, person_id, mensaje, creado_en FROM auditoria ORDER BY id DESC"
        ).fetchall()

    return jsonify([dict(row) for row in rows])


init_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
