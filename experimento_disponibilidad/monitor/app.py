from orquestador import Orquestador
import time
from datetime import datetime
import sqlite3

amqp_url = "amqps://lhgcccuh:zKo8dpTeDZvuvJIUB_da8uZXX3MeHjen@jackal.rmq.cloudamqp.com/lhgcccuh"
nombre_exchange = "events"
orquestador = Orquestador()
tiempo_de_resiliencia = 1
frecuencia_de_monitoreo = 5  # Reducido a 5s para garantizar detección <10s
componentes_bajo_monitoreo = [
    {"nombre": "componente_mock_1", "estado": "inactivo"},
    {"nombre": "componente_mock_2", "estado": "inactivo"},
]

# Base de datos SQLite
db_path = "monitoreo.db"
db_conn = None
ciclo_actual = 0
tiempo_ultimo_ping = {}
estado_anterior = {}  # Rastrear el estado anterior de cada componente


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
        
        # Reiniciar estados ANTES de enviar ping
        reiniciar_estado_de_los_componentes()
        
        tiempo_ping = time.time()
        
        # Registrar ping enviado
        for comp in componentes_bajo_monitoreo:
            tiempo_ultimo_ping[comp['nombre']] = tiempo_ping
            registrar_evento(ciclo_actual, comp['nombre'], 'ping_enviado', 'esperando')
        
        orquestador.publicar(nombre_exchange, "ping", None)
        
        # Esperar respuestas durante el periodo de monitoreo
        time.sleep(frecuencia_de_monitoreo)
        
        # Reportar inmediatamente después del periodo
        reportar_estado_de_componentes()


def procesar_echo(pattern, payload):
    nombre = pattern.split(".")[1]  # pattern = echo.componente_mock_1
    
    # Calcular tiempo de respuesta
    tiempo_respuesta = None
    if nombre in tiempo_ultimo_ping:
        tiempo_respuesta = (time.time() - tiempo_ultimo_ping[nombre]) * 1000  # en ms
        
        # Solo considerar el echo válido si está dentro del período de monitoreo
        # (evita procesar mensajes antiguos de la cola)
        if tiempo_respuesta <= frecuencia_de_monitoreo * 1000:
            # Registrar echo recibido
            registrar_evento(ciclo_actual, nombre, 'echo_recibido', 'activo', tiempo_respuesta)
            actualizar_estado_componente(nombre, "activo")
        else:
            # Echo fuera de tiempo, ignorar
            print(f"Echo de {nombre} ignorado (fuera de tiempo: {tiempo_respuesta:.0f}ms)")
    else:
        # No hay registro de ping para este componente, ignorar
        print(f"Echo de {nombre} ignorado (sin ping previo)")


def actualizar_estado_componente(nombre, estado):
    for componente in componentes_bajo_monitoreo:
        if componente["nombre"] == nombre:
            componente["estado"] = estado
            break


def reportar_estado_de_componentes():
    tiempo_actual = time.time()
    print(f"Estado de componentes (Ciclo {ciclo_actual}):")
    for c in componentes_bajo_monitoreo:
        nombre = c['nombre']
        estado_actual = c['estado']
        estado_previo = estado_anterior.get(nombre, None)
        
        # Detectar cambio de estado
        hubo_cambio = estado_previo is not None and estado_previo != estado_actual
        
        if estado_actual == 'inactivo':
            # Calcular tiempo real de detección desde el último ping
            tiempo_deteccion_real = (tiempo_actual - tiempo_ultimo_ping.get(nombre, tiempo_actual)) * 1000
            registrar_evento(ciclo_actual, nombre, 'falla_detectada', 'inactivo', tiempo_deteccion_real)
            
            if hubo_cambio:
                print(f"- {nombre} : {estado_actual} (CAMBIO detectado en {tiempo_deteccion_real:.0f}ms / {tiempo_deteccion_real/1000:.2f}s)")
            else:
                print(f"- {nombre} : {estado_actual}")
        else:
            if hubo_cambio:
                # Calcular tiempo de detección de recuperación
                tiempo_recuperacion = (tiempo_actual - tiempo_ultimo_ping.get(nombre, tiempo_actual)) * 1000
                print(f"- {nombre} : {estado_actual} (RECUPERADO detectado en {tiempo_recuperacion:.0f}ms / {tiempo_recuperacion/1000:.2f}s)")
            else:
                print(f"- {nombre} : {estado_actual}")
        
        # Actualizar estado anterior
        estado_anterior[nombre] = estado_actual
    print(" ")


def reiniciar_estado_de_los_componentes():
    for componente in componentes_bajo_monitoreo:
        componente["estado"] = "inactivo"


main()
