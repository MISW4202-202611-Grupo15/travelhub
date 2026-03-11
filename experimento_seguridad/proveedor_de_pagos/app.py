import sys
import os
from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from librerias.servicio_de_encripcion.criptology_service import CryptologyService

app = Flask(__name__)


# Registrar pago
@app.route("/payment", methods=["POST"])
def create_payment():
    try:
        # encrypted_data = "something coming from the request body"
        encrypted_data = request.json
        decrypted_data = CryptologyService.decrypt(encrypted_data)
        print("Esta es la información encriptada")
        print(encrypted_data)
        print("")
        print("Esta es la información desencriptada")
        print(decrypted_data)
        return "Pago realizado", 201
    except:
        print("Ocurrió un error realizando el pago")
        return "Ocurrió un error realizando el pago", 500


# Ejecutar la app
if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host="127.0.0.1", port=5000)
