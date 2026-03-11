from librerias.orquestador.app import Orquestador
from librerias.servicio_de_encripcion.criptology_service import CryptologyService
import time
import requests

# Broker config
orquestador = Orquestador()
tiempo_de_resiliencia = 3
amqp_url = "amqps://lhgcccuh:zKo8dpTeDZvuvJIUB_da8uZXX3MeHjen@jackal.rmq.cloudamqp.com/lhgcccuh"
exchange_name = "events"

# Proveedor de pagos api config
payment_service_url = "http://127.0.0.1:5000/payment"
sensible_data = (
    {}
)  # Juan Cordona / Hector Malagrejo -> Aca se debe poner la data bancaria sensible que se debe encriptar


def main():
    while True:
        try:
            connected = orquestador.inicializar(amqp_url, exchange_name)
            if not connected:
                raise Exception(
                    "No hay conexión entre el servicio de pagos el orquestador"
                )
            print("Servicio de pagos conectado al orquestador")
            orquestador.subscribirse(exchange_name, "payment_required", request_payment)
            print("Servicio de pagos suscrito al evento payment_required")
            print("")
            while True:
                print(f"Servicio de pagos corriendo...")
                time.sleep(1)
        except Exception as e:
            print("Reintentando conectar el servicio de pagos con el orquestador...")
            time.sleep(tiempo_de_resiliencia)


def main_1():
    while True:
        print("Teclee la letra p para generar pago o cualquier otra para salir")
        input = input()
        if input in ("p", "P"):
            request_payment()
        else:
            break


def request_payment():
    encrypted_data = CryptologyService.encrypt(sensible_data)
    response = requests.post(payment_service_url, encrypted_data)
    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
    main_1()
