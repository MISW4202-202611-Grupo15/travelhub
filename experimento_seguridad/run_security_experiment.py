"""
Experimento de Seguridad - Inyección de ataques y métricas.
Ejecuta N iteraciones contra el proveedor de pagos, inyectando
ataques aleatorios (tampering, spoofing, canal sin cifrar) y
registrando los resultados en SQLite.
"""

import sys
import os
import time
import random
import json
import sqlite3
import threading
import logging
import requests
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from librerias.servicio_de_encripcion.criptology_service import CryptologyService

# ── Config ─────────────────────────────────────────────────────
PAYMENT_URL = "http://127.0.0.1:5000/payment"
AUDIT_URL = "http://127.0.0.1:5001/audit"
NUM_ITERATIONS = 60
DB_PATH = os.path.join(BASE_DIR, "resultados_experimento.db")

VALID_TOKEN = "tok-seguro-2024"
LLAVE_AES = "MzQyNHg2NiEyQUxPPXxaUA=="
IV_AES = "2648937582046372"

SENSIBLE_DATA = {
    "documento": 10958346721,
    "banco": "BBVA",
    "cuenta": 98563627121,
    "tipo_cuenta": "AHORROS",
}


# ── Base de datos de resultados ────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS resultados (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            iteracion       INTEGER,
            tipo_ataque     TEXT,
            detectado       INTEGER,
            tiempo_ms       REAL,
            codigo_http     INTEGER,
            detalle         TEXT,
            timestamp       TEXT
        )"""
    )
    conn.commit()
    return conn


# ── Constructores de peticiones ────────────────────────────────
def _encrypt(data):
    svc = CryptologyService(LLAVE_AES)
    return svc.encrypt(json.dumps(data), LLAVE_AES, IV_AES).decode()


def build_normal():
    """Petición legítima: cifrada + token válido."""
    payload = {"encrypted_data": _encrypt(SENSIBLE_DATA)}
    headers = {"X-Auth-Token": VALID_TOKEN}
    return payload, headers


def build_tampering():
    """Dato cifrado pero corrompido (bytes alterados)."""
    enc = _encrypt(SENSIBLE_DATA)
    corrupted = enc[:10] + "XXXX" + enc[14:]
    payload = {"encrypted_data": corrupted}
    headers = {"X-Auth-Token": VALID_TOKEN}
    return payload, headers


def build_spoofing():
    """Token falso simulando suplantación de identidad."""
    payload = {"encrypted_data": _encrypt(SENSIBLE_DATA)}
    headers = {"X-Auth-Token": "token-falso-atacante"}
    return payload, headers


def build_unencrypted():
    """Datos sensibles enviados en texto plano (sin cifrar)."""
    payload = SENSIBLE_DATA.copy()  # sin campo encrypted_data
    headers = {"X-Auth-Token": VALID_TOKEN}
    return payload, headers


ATTACKS = {
    "normal": build_normal,
    "tampering": build_tampering,
    "spoofing": build_spoofing,
    "sin_cifrado": build_unencrypted,
}


# ── Ejecución de iteraciones ──────────────────────────────────
def run_iteration(iteration):
    attack_type = random.choice(list(ATTACKS.keys()))
    payload, headers = ATTACKS[attack_type]()

    start = time.perf_counter()
    try:
        resp = requests.post(PAYMENT_URL, json=payload, headers=headers, timeout=10)
        elapsed = (time.perf_counter() - start) * 1000
        code = resp.status_code
        detail = resp.text[:200]
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        code = 0
        detail = str(e)[:200]

    if attack_type == "normal":
        detected = None  # N/A
    else:
        detected = 1 if code != 201 else 0

    return {
        "iteracion": iteration,
        "tipo_ataque": attack_type,
        "detectado": detected,
        "tiempo_ms": round(elapsed, 2),
        "codigo_http": code,
        "detalle": detail,
        "timestamp": datetime.now().isoformat(),
    }


# ── Utilidades ─────────────────────────────────────────────────
def wait_for_server(url, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        try:
            requests.get(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def print_summary(results):
    attacks = [r for r in results if r["tipo_ataque"] != "normal"]
    normals = [r for r in results if r["tipo_ataque"] == "normal"]
    detected = sum(1 for r in attacks if r["detectado"] == 1)
    normal_ok = sum(1 for r in normals if r["codigo_http"] == 201)

    print(f"\n{'=' * 60}")
    print("RESUMEN DEL EXPERIMENTO DE SEGURIDAD")
    print(f"{'=' * 60}")
    print(f"Total iteraciones:      {len(results)}")
    print(f"Peticiones normales:    {len(normals)}  (exitosas: {normal_ok})")
    print(f"Ataques inyectados:     {len(attacks)}  (detectados: {detected}/{len(attacks)})")

    for atype in ("tampering", "spoofing", "sin_cifrado"):
        subset = [r for r in results if r["tipo_ataque"] == atype]
        if subset:
            det = sum(1 for r in subset if r["detectado"] == 1)
            avg = sum(r["tiempo_ms"] for r in subset) / len(subset)
            print(f"  {atype:<15}: {det}/{len(subset)} detectados, promedio {avg:.1f} ms")

    avg_all = sum(r["tiempo_ms"] for r in results) / len(results)
    print(f"\nTiempo promedio total:  {avg_all:.1f} ms")
    print(f"Resultados en BD:       {DB_PATH}")

    # Mostrar registros de auditoría
    try:
        audit_resp = requests.get(AUDIT_URL, timeout=3)
        if audit_resp.status_code == 200:
            audits = audit_resp.json()
            print(f"Registros de auditoría: {len(audits)}")
    except Exception:
        pass

    print(f"{'=' * 60}")


# ── Main ──────────────────────────────────────────────────────
def main():
    # Suprimir logs de werkzeug para no ensuciar la salida
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    from proveedor_de_pagos.app import app as proveedor_app
    from componente_auditoria.app import app as auditoria_app

    print("Iniciando servidores...")
    threading.Thread(
        target=lambda: proveedor_app.run(port=5000, use_reloader=False),
        daemon=True,
    ).start()
    threading.Thread(
        target=lambda: auditoria_app.run(port=5001, use_reloader=False),
        daemon=True,
    ).start()

    if not wait_for_server(PAYMENT_URL.replace("/payment", "/")):
        print("ERROR: proveedor_de_pagos no respondió en el puerto 5000")
        return
    if not wait_for_server(AUDIT_URL.replace("/audit", "/")):
        print("ERROR: componente_auditoria no respondió en el puerto 5001")
        return

    print("Servidores listos.\n")

    conn = init_db()
    results = []

    header = f"{'#':<4} {'Tipo':<15} {'Detectado':<12} {'Tiempo(ms)':<12} {'HTTP':<6}"
    print(header)
    print("-" * len(header))

    for i in range(1, NUM_ITERATIONS + 1):
        r = run_iteration(i)
        results.append(r)
        conn.execute(
            "INSERT INTO resultados (iteracion,tipo_ataque,detectado,tiempo_ms,codigo_http,detalle,timestamp) VALUES (?,?,?,?,?,?,?)",
            (r["iteracion"], r["tipo_ataque"], r["detectado"], r["tiempo_ms"], r["codigo_http"], r["detalle"], r["timestamp"]),
        )
        conn.commit()

        det_str = "N/A" if r["detectado"] is None else ("Sí" if r["detectado"] else "No")
        print(f"{r['iteracion']:<4} {r['tipo_ataque']:<15} {det_str:<12} {r['tiempo_ms']:<12} {r['codigo_http']:<6}")

    conn.close()
    print_summary(results)


if __name__ == "__main__":
    main()
