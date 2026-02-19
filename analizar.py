"""
Análisis de Detección de fallas desde SQLite
"""
import sqlite3
import os

def analizar():
    # Buscar BD
    db_paths = ['monitoreo.db', 'monitor/monitoreo.db']
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("No se encontró la base de datos monitoreo.db")
        print("Asegúrate de que el monitor esté corriendo")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtener todos los registros
    cursor.execute("SELECT * FROM eventos ORDER BY timestamp")
    registros = cursor.fetchall()
    
    if not registros:
        print("No hay registros en la base de datos")
        return
    
    # Análisis
    total = len(registros)
    fallas = cursor.execute("SELECT * FROM eventos WHERE evento='falla_detectada'").fetchall()
    echos = cursor.execute("SELECT * FROM eventos WHERE evento='echo_recibido'").fetchall()
    pings = cursor.execute("SELECT * FROM eventos WHERE evento='ping_enviado'").fetchall()
    
    print("\n" + "="*70)
    print("ANÁLISIS DE DETECCIÓN DE FALLAS - EXPERIMENTO")
    print("="*70)
    print(f"\nTotal de registros: {total}")
    print(f"Pings enviados: {len(pings)}")
    print(f"Echos recibidos: {len(echos)}")
    print(f"Fallas detectadas: {len(fallas)}")
    
    # Verificar requisitos
    print(f"\n--- Cumplimiento de Requisitos ---")
    if total >= 60:
        print(f"Requisito 1: {total} registros (≥60 requeridos)")
    else:
        print(f"Requisito 1: {total} registros (se requieren ≥60)")
    
    if fallas:
        tiempos = [f[6]/1000 for f in fallas if f[6]]  # tiempo_deteccion_ms a segundos
        todas_bajo_10s = all(t <= 10 for t in tiempos)
        if todas_bajo_10s:
            print(f"Requisito 2: Todas las fallas detectadas en <10s")
            print(f"  Tiempo promedio: {sum(tiempos)/len(tiempos):.2f}s")
        else:
            print(f"Requisito 2: Algunas fallas excedieron 10s")
    else:
        print(f"No hay fallas registradas para evaluar")
    
    # Análisis por componente
    print(f"\n--- Por Componente ---")
    for comp in ['componente_mock_1', 'componente_mock_2']:
        comp_pings = cursor.execute("SELECT COUNT(*) FROM eventos WHERE componente=? AND evento='ping_enviado'", (comp,)).fetchone()[0]
        comp_echos = cursor.execute("SELECT COUNT(*) FROM eventos WHERE componente=? AND evento='echo_recibido'", (comp,)).fetchone()[0]
        if comp_pings > 0:
            disp = (comp_echos / comp_pings) * 100
            print(f"{comp}: {disp:.1f}% disponibilidad ({comp_echos}/{comp_pings} respuestas)")
    
    print("\n" + "="*70)
    print(f"Base de datos: {db_path}")
    print("="*70 + "\n")
    
    conn.close()

if __name__ == "__main__":
    analizar()
