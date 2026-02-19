"""Script para preparar nuevo experimento"""
import os
import shutil
from datetime import datetime

db_paths = ['monitoreo.db', 'monitor/monitoreo.db']

for db_path in db_paths:
    if os.path.exists(db_path):
        backup = f"{db_path.replace('.db', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy(db_path, backup)
        os.remove(db_path)
        print(f"Respaldo creado: {backup}")
        print(f"BD eliminada: {db_path}")
        print("Listo para nuevo experimento")
        break
else:
    print("No hay BD anterior. Listo para experimento")
