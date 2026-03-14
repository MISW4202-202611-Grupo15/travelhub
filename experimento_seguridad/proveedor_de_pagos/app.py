import sys
import os
from flask import Flask, request, jsonify
import json
import requests as http_client

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from librerias.servicio_de_encripcion.criptology_service import CryptologyService

app = Flask(__name__)

BACK_LLAVE_AES_DECRYPT = "MDFBM3g1aTkwTDBXMjg0bA=="
BACK_IV_AES_DECRYPT = "1050701070905080"
BACK_LLAVE_AES_ENCRYPT = "MzQyNHg2NiEyQUxPPXxaUA=="
BACK_IV_AES_ENCRYPT = "2648937582046372"

VALID_TOKEN = "tok-seguro-2024"
AUDIT_URL = "http://127.0.0.1:5001/audit"


def log_audit(person_id, mensaje):
    try:
        http_client.post(AUDIT_URL, json={"person_id": str(person_id), "message": mensaje}, timeout=2)
    except Exception:
        pass


# Registrar pago
@app.route("/payment", methods=["POST"])
def create_payment():
    # 1. Detección de spoofing: validar token de autenticación
    token = request.headers.get("X-Auth-Token")
    if token != VALID_TOKEN:
        log_audit("desconocido", "SPOOFING_DETECTED: token inválido o ausente")
        return jsonify({"error": "spoofing_detected", "detalle": "Token inválido"}), 401

    # 2. Detección de canal no cifrado: validar campo encrypted_data
    body = request.json or {}
    encrypted_field = body.get("encrypted_data")
    if not isinstance(encrypted_field, str) or not encrypted_field:
        log_audit("desconocido", "UNENCRYPTED_DETECTED: datos enviados sin cifrar")
        return jsonify({"error": "unencrypted_detected", "detalle": "Datos sin cifrar"}), 400

    # 3. Detección de tampering: intentar descifrar
    try:
        desencripcion = CryptologyService(BACK_LLAVE_AES_ENCRYPT)
        decrypted_data = json.loads(
            desencripcion.decrypt(encrypted_field, BACK_LLAVE_AES_ENCRYPT, BACK_IV_AES_ENCRYPT)
        )
        log_audit(decrypted_data.get("documento", "N/A"), "PAYMENT_OK: pago procesado")
        return jsonify({"status": "ok", "detalle": "Pago realizado"}), 201
    except Exception as e:
        log_audit("desconocido", f"TAMPERING_DETECTED: datos alterados - {e}")
        return jsonify({"error": "tampering_detected", "detalle": "Datos alterados o corruptos"}), 400


# Ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host="127.0.0.1", port=5000)
