import sys
import os
from flask import Flask, request, jsonify
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from librerias.servicio_de_encripcion.criptology_service import CryptologyService

app = Flask(__name__)

BACK_LLAVE_AES_DECRYPT = "MDFBM3g1aTkwTDBXMjg0bA=="
BACK_IV_AES_DECRYPT="1050701070905080"
BACK_LLAVE_AES_ENCRYPT="MzQyNHg2NiEyQUxPPXxaUA=="
BACK_IV_AES_ENCRYPT="2648937582046372"

# Registrar pago
@app.route("/payment", methods=["POST"])
def create_payment():
    try:
        # encrypted_data = "something coming from the request body"
        encrypted_data = request.json
        print("Esta es la información encriptada")
        print(encrypted_data)
        print("")
        desencripcion = CryptologyService(BACK_LLAVE_AES_ENCRYPT)
        decrypted_data = json.loads(
                            desencripcion.decrypt(
                                encrypted_data.get("encrypted_data"),
                                BACK_LLAVE_AES_ENCRYPT, 
                                BACK_IV_AES_ENCRYPT
                            )
                        )
        print("Esta es la información desencriptada")
        print(decrypted_data)
        return "Pago realizado", 201
    except Exception as e:
        print("Ocurrió un error realizando el pago",e)
        return "Ocurrió un error realizando el pago", 500


# Ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host="127.0.0.1", port=5000)
