from orquestador import Orquestador
import time

amqp_url = "amqps://lhgcccuh:zKo8dpTeDZvuvJIUB_da8uZXX3MeHjen@jackal.rmq.cloudamqp.com/lhgcccuh"
nombre_exchange = "events"
orquestador = Orquestador()
tiempo_de_resiliencia = 3


def main():
    while True:
        try:
            conectado = orquestador.inicializar(amqp_url, nombre_exchange)

            if not conectado:
                raise Exception(
                    "No hay conexión entre el componente mock 1 y el orquestador"
                )

            print("Componente mock 1 conectado al orquestador")
            print("")

            orquestador.subscribirse(nombre_exchange, "ping", procesar_ping)

            while True:
                print("Componente mock 1 corriendo...")
                time.sleep(1)

        except Exception as e:
            print("Reintentando conectar el componente mock 1 con el orquestador...")
            time.sleep(tiempo_de_resiliencia)


def reportar_estado():
    orquestador.subscribirse(nombre_exchange, "ping", procesar_ping)


def procesar_ping():
    orquestador.publicar(nombre_exchange, "echo.componente_mock_1", None)


main()
