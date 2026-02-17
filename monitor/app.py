from orquestador import Orquestador
import time

tiempo_de_resiliencia = 1
frecuencia_de_monitoreo = 10

nombre_exchange = "events"
AMQP_URL = "amqps://lhgcccuh:zKo8dpTeDZvuvJIUB_da8uZXX3MeHjen@jackal.rmq.cloudamqp.com/lhgcccuh"

componentes_bajo_monitoreo = [
    {"nombre": "componente_mock_1", "estado": "inactivo"},
    {"nombre": "componente_mock_2", "estado": "inactivo"},
]
cliente_broker = Orquestador()


def main():
    while True:
        bus_inicializado = cliente_broker.inicializar(AMQP_URL)
        if bus_inicializado:
            monitorear()
        else:
            print("No hay comunicación con el orquestador")
            time.sleep(tiempo_de_resiliencia)


def monitorear():
    # escuchar todos los ecos
    cliente_broker.subscribirse(nombre_exchange, "echo.*", manejar_eventos)

    while True:
        cliente_broker.publicar(nombre_exchange, "ping", {"source": "monitor"})
        time.sleep(frecuencia_de_monitoreo)
        reportar_estado_de_componentes()


def manejar_eventos(routing_key, data):
    # routing_key = echo.componente_mock_1
    nombre = routing_key.split(".")[1]
    actualizar_estado_componente(nombre, "activo")


def actualizar_estado_componente(nombre, estado):
    for componente in componentes_bajo_monitoreo:
        if componente["nombre"] == nombre:
            componente["estado"] = estado
            break


def reportar_estado_de_componentes():
    print("Estado de componentes:")
    for c in componentes_bajo_monitoreo:
        print(f"- {c['nombre']} : {c['estado']}")
    print(" ")


main()
