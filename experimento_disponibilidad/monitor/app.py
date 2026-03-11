from orquestador import Orquestador
import time
from datetime import datetime
import sqlite3

amqp_url = "amqps://lhgcccuh:zKo8dpTeDZvuvJIUB_da8uZXX3MeHjen@jackal.rmq.cloudamqp.com/lhgcccuh"
nombre_exchange = "events"
orquestador = Orquestador()
tiempo_de_resiliencia = 1
frecuencia_de_monitoreo = 10
componentes_bajo_monitoreo = [
    {"nombre": "componente_mock_1", "estado": "inactivo"},
    {"nombre": "componente_mock_2", "estado": "inactivo"},
]

# Base de datos SQLite
db_path = "monitoreo.db"
db_conn = None
ciclo_actual = 0
tiempo_ultimo_ping = {}


def inicializar_bd():
    """Crea la base de datos y tabla si no existe"""
    global db_conn
    db_conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = db_conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ciclo INTEGER NOT NULL,
            componente TEXT NOT NULL,
            evento TEXT NOT NULL,
            estado TEXT NOT NULL,
            tiempo_deteccion_ms REAL
        )
    ''')
    db_conn.commit()
    print(f"Base de datos inicializada: {db_path}")


def registrar_evento(ciclo, componente, evento, estado, tiempo_deteccion_ms=None):
    """Registra un evento en la base de datos"""
    if db_conn:
        cursor = db_conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO eventos (timestamp, ciclo, componente, evento, estado, tiempo_deteccion_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, ciclo, componente, evento, estado, tiempo_deteccion_ms))
        db_conn.commit()


def main():
    inicializar_bd()
    
    while True:
        try:
            conectado = orquestador.inicializar(amqp_url, nombre_exchange)

            if conectado:
                print("Monitor conectado al orquestador")
                print(f"Registros guardados en: {db_path}")
                print("")
                monitorear()
            else:
                raise Exception("No hay conexión entre el monitor y el orquestador")

        except Exception as e:
            print("Reintentando conectar el monitor con el orquestador...")
            time.sleep(tiempo_de_resiliencia)


def monitorear():
    global ciclo_actual
    orquestador.subscribirse(nombre_exchange, "echo.*", procesar_echo)

    while True:
        ciclo_actual += 1
        tiempo_ping = time.time()
        
        # Registrar ping enviado
        for comp in componentes_bajo_monitoreo:
            tiempo_ultimo_ping[comp['nombre']] = tiempo_ping
            registrar_evento(ciclo_actual, comp['nombre'], 'ping_enviado', 'esperando')
        
        orquestador.publicar(nombre_exchange, "ping", None)
        time.sleep(frecuencia_de_monitoreo)
        reportar_estado_de_componentes()
        reiniciar_estado_de_los_componentes()


def procesar_echo(pattern, payload):
    nombre = pattern.split(".")[1]  # pattern = echo.componente_mock_1
    
    # Calcular tiempo de respuesta
    tiempo_respuesta = None
    if nombre in tiempo_ultimo_ping:
        tiempo_respuesta = (time.time() - tiempo_ultimo_ping[nombre]) * 1000  # en ms
    
    # Registrar echo recibido
    registrar_evento(ciclo_actual, nombre, 'echo_recibido', 'activo', tiempo_respuesta)
    actualizar_estado_componente(nombre, "activo")


def actualizar_estado_componente(nombre, estado):
    for componente in componentes_bajo_monitoreo:
        if componente["nombre"] == nombre:
            componente["estado"] = estado
            break


def reportar_estado_de_componentes():
    print(f"Estado de componentes (Ciclo {ciclo_actual}):")
    for c in componentes_bajo_monitoreo:
        print(f"- {c['nombre']} : {c['estado']}")
        
        # Registrar estado final del ciclo
        if c['estado'] == 'inactivo':
            registrar_evento(ciclo_actual, c['nombre'], 'falla_detectada', 'inactivo', frecuencia_de_monitoreo * 1000)
    print(" ")


def reiniciar_estado_de_los_componentes():
    for componente in componentes_bajo_monitoreo:
        componente["estado"] = "inactivo"


main()
