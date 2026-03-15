# from librerias.orquestador.app import Orquestador
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from librerias.servicio_de_encripcion.criptology_service import CryptologyService
import time
import requests
import json

BACK_LLAVE_AES_DECRYPT = "MDFBM3g1aTkwTDBXMjg0bA=="
BACK_IV_AES_DECRYPT="1050701070905080"
BACK_LLAVE_AES_ENCRYPT="MzQyNHg2NiEyQUxPPXxaUA=="
BACK_IV_AES_ENCRYPT="2648937582046372"

# Broker config
# orquestador = Orquestador()
# tiempo_de_resiliencia = 3
# amqp_url = "amqps://lhgcccuh:zKo8dpTeDZvuvJIUB_da8uZXX3MeHjen@jackal.rmq.cloudamqp.com/lhgcccuh"
# exchange_name = "events"

# Proveedor de pagos api config
payment_service_url = "http://127.0.0.1:5000/payment"
payment_service_url_falsa = "http://127.0.0.1:5001/payment"
sensible_data = {
    "documento": 10958346721,
    "banco": "BBVA",
    "cuenta": 98563627121,
    "tipo_cuenta": "AHORROS"
}  # Juan Cordona / Hector Malagrejo -> Aca se debe poner la data bancaria sensible que se debe encriptar




VALID_TOKEN = "tok-seguro-2024"
LLAVE_AES = "MzQyNHg2NiEyQUxPPXxaUA=="
IV_AES = "2648937582046372"








# def main():
#     while True:
#         try:
#             connected = orquestador.inicializar(amqp_url, exchange_name)
#             if not connected:
#                 raise Exception(
#                     "No hay conexión entre el servicio de pagos el orquestador"
#                 )
#             print("Servicio de pagos conectado al orquestador")
#             orquestador.subscribirse(exchange_name, "payment_required", request_payment)
#             print("Servicio de pagos suscrito al evento payment_required")
#             print("")
#             while True:
#                 print(f"Servicio de pagos corriendo...")
#                 time.sleep(1)
#         except Exception as e:
#             print("Reintentando conectar el servicio de pagos con el orquestador...")
#             time.sleep(tiempo_de_resiliencia)


def main_1():
    while True:
        print("Teclee la letra p para generar pago o cualquier otra para salir")
        _input = input()
        if _input in ("p", "P"):
            request_payment()
        else:
            break


def request_payment():
    encripcion = CryptologyService(BACK_LLAVE_AES_ENCRYPT)
    print("**** DATOS SENSIBLES *****")


    print(sensible_data)
    antes = json.dumps(sensible_data)

    encrypted_data = encripcion.encrypt(
        json.dumps(sensible_data),
        BACK_LLAVE_AES_ENCRYPT,
        BACK_IV_AES_ENCRYPT
    ).decode()
    despues = json.dumps({"encrypted_data": encrypted_data, "token": VALID_TOKEN})

    payload = {"encrypted_data": encrypted_data}
    headers = {"X-Auth-Token": VALID_TOKEN}





    print(" ")


    print("**** DATOS ENCRIPTADOS *****")
    print(encrypted_data)
    payload = {
        "encrypted_data" : encrypted_data
    }
    response = requests.post(payment_service_url, json=payload, headers = headers)

    print(" ")
    print("**** REPUESTA DEL PAGO (Normal) *****")
    print(response.status_code)
    print(response.text)
 
    print(" ")

    response = requests.post(payment_service_url_falsa, json=payload)
    print("**** REPUESTA DEL PAGO (Ataque) *****")
    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    main_1()
