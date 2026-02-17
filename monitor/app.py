from orquestador import Orquestador
import time

amqp_url = "amqps://lhgcccuh:zKo8dpTeDZvuvJIUB_da8uZXX3MeHjen@jackal.rmq.cloudamqp.com/lhgcccuh"
nombre_exchange = "events"
orquestador = Orquestador()
tiempo_de_resiliencia = 1
frecuencia_de_monitoreo = 10
componentes_bajo_monitoreo = [
    {"nombre": "componente_mock_1", "estado": "inactivo"},
    {"nombre": "componente_mock_2", "estado": "inactivo"},
]


def main():
    while True:
        try:
            conectado = orquestador.inicializar(amqp_url, nombre_exchange)

            if conectado:
                print("Monitor conectado al orquestador")
                print("")
                monitorear()
            else:
                raise Exception("No hay conexión entre el monitor y el orquestador")

        except Exception as e:
            print("Reintentando conectar el monitor con el orquestador...")
            time.sleep(tiempo_de_resiliencia)


def monitorear():
    orquestador.subscribirse(nombre_exchange, "echo.*", procesar_echo)

    while True:
        orquestador.publicar(nombre_exchange, "ping", None)
        time.sleep(frecuencia_de_monitoreo)
        reportar_estado_de_componentes()
        reiniciar_estado_de_los_componentes()


def procesar_echo(routing_key):
    nombre = routing_key.split(".")[1]  # routing_key = echo.componente_mock_1
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


def reiniciar_estado_de_los_componentes():
    for componente in componentes_bajo_monitoreo:
        componente["estado"] = "inactivo"


main()
