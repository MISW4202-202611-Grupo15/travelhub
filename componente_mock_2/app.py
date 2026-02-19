from orquestador import Orquestador
import time
import os

amqp_url = "amqps://lhgcccuh:zKo8dpTeDZvuvJIUB_da8uZXX3MeHjen@jackal.rmq.cloudamqp.com/lhgcccuh"
nombre_exchange = "events"
orquestador = Orquestador()
tiempo_de_resiliencia = 3

# Configuración para simular falla
# Cambiar a True para simular que el componente está caído (no responde a pings)
SIMULAR_FALLA = os.getenv("SIMULAR_FALLA", "false").lower() == "true"


def main():
    while True:
        try:
            conectado = orquestador.inicializar(amqp_url, nombre_exchange)

            if not conectado:
                raise Exception(
                    "No hay conexión entre el componente mock 2 y el orquestador"
                )

            print("Componente mock 2 conectado al orquestador")

            orquestador.subscribirse(nombre_exchange, "ping", procesar_ping)
            print("Componente mock 2 suscrito al ping")

            print("")

            while True:
                estado = "FALLA SIMULADA - NO RESPONDE" if SIMULAR_FALLA else "corriendo"
                print(f"Componente mock 2 {estado}...")
                time.sleep(1)

        except Exception as e:
            print("Reintentando conectar el componente mock 2 con el orquestador...")
            time.sleep(tiempo_de_resiliencia)


def reportar_estado():
    orquestador.subscribirse(nombre_exchange, "ping", procesar_ping)


def procesar_ping(pattern, payload):
    # Si estamos simulando falla, NO responder al ping
    if SIMULAR_FALLA:
        return  # No enviar echo
    
    orquestador.publicar(nombre_exchange, "echo.componente_mock_2", None)


main()
