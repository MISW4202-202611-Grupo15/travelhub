from event_bus import EventBus
import time

tiempo_de_resiliencia = 1
frecuencia_de_monitoreo = 10
componentes_a_monitorear = [
    {"nombre": "componente_mock_1", "estado": "inactivo"},
    {"nombre": "componente_mock_2", "estado": "inactivo"},
]
bus = EventBus()


def main():
    while True:
        bus_inicializado = bus.inicializar()
        if bus_inicializado:
            monitorear()
        else:
            print("No hay comunicación con el orquestador")
            time.sleep(tiempo_de_resiliencia)


def monitorear():
    bus.subscribirse(manejar_eventos)
    while True:
        bus.publicar("ping", None)
        time.sleep(frecuencia_de_monitoreo)
        reportar_componentes_inactivos()


def manejar_eventos(event, data):
    if event == "echo":
        actualizar_estado_componente(data["name"], data["estado"])


def actualizar_estado_componente(nombre, estado):
    for componente in componentes_a_monitorear:
        if componente["nombre"] == nombre:
            componente["estado"] = estado
            break


def reportar_componentes_inactivos():
    inactivos = [c for c in componentes_a_monitorear if c["estado"] == "inactivo"]
    if inactivos:
        print("Componentes inactivos:")
        for c in inactivos:
            print(f"- {c['nombre']}")
        print(" ")


main()
