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
        comp_fallas = cursor.execute("SELECT COUNT(*) FROM eventos WHERE componente=? AND evento='falla_detectada'", (comp,)).fetchone()[0]
        if comp_pings > 0:
            disp = (comp_echos / comp_pings) * 100
            print(f"{comp}:")
            print(f"  Disponibilidad: {disp:.1f}% ({comp_echos}/{comp_pings})")
            print(f"  Fallas: {comp_fallas} ciclos")
    
    # Estadísticas de latencia de respuesta (echo)
    latencias = cursor.execute("SELECT tiempo_deteccion_ms FROM eventos WHERE evento='echo_recibido' AND tiempo_deteccion_ms IS NOT NULL").fetchall()
    if latencias:
        lats = sorted([l[0] for l in latencias])
        print(f"\n--- Latencias de Respuesta (Echo) ---")
        print(f"Promedio: {sum(lats)/len(lats):.2f} ms")
        print(f"Mínima: {min(lats):.2f} ms")
        print(f"Máxima: {max(lats):.2f} ms")
        print(f"Mediana (P50): {lats[len(lats)//2]:.2f} ms")
        if len(lats) > 1:
            print(f"P95: {lats[int(len(lats)*0.95)]:.2f} ms")
    
    # Estadísticas de tiempo de detección de fallas
    tiempos_falla = cursor.execute("SELECT tiempo_deteccion_ms FROM eventos WHERE evento='falla_detectada' AND tiempo_deteccion_ms IS NOT NULL").fetchall()
    if tiempos_falla:
        t_fallas = sorted([t[0] for t in tiempos_falla])
        print(f"\n--- Tiempos de Detección de Fallas ---")
        print(f"Promedio: {sum(t_fallas)/len(t_fallas):.2f} ms ({sum(t_fallas)/len(t_fallas)/1000:.2f}s)")
        print(f"Mínimo: {min(t_fallas):.2f} ms ({min(t_fallas)/1000:.2f}s)")
        print(f"Máximo: {max(t_fallas):.2f} ms ({max(t_fallas)/1000:.2f}s)")
        print(f"Mediana (P50): {t_fallas[len(t_fallas)//2]:.2f} ms ({t_fallas[len(t_fallas)//2]/1000:.2f}s)")
        if len(t_fallas) > 1:
            print(f"P95: {t_fallas[int(len(t_fallas)*0.95)]:.2f} ms ({t_fallas[int(len(t_fallas)*0.95)]/1000:.2f}s)")
        print(f"✓ Todas bajo 10s: {'SÍ' if max(t_fallas) < 10000 else 'NO'}")
    
    # Duración del experimento
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM eventos")
    inicio, fin = cursor.fetchone()
    if inicio and fin:
        from datetime import datetime
        t_inicio = datetime.fromisoformat(inicio)
        t_fin = datetime.fromisoformat(fin)
        duracion = (t_fin - t_inicio).total_seconds()
        print(f"\n--- Duración del Experimento ---")
        print(f"Inicio: {inicio[:19]}")
        print(f"Fin: {fin[:19]}")
        print(f"Duración: {duracion/60:.1f} minutos ({duracion:.0f} segundos)")
    
    print("\n" + "="*70)
    print(f"Base de datos: {db_path}")
    print("="*70 + "\n")
    
    conn.close()

if __name__ == "__main__":
    analizar()
