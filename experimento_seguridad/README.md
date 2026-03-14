# Experimento de Seguridad - Sistema de Pagos con Encriptación

## Descripción

Sistema de pagos que transmite datos bancarios cifrados (AES-CBC) entre servicios. Un script automatizado (`run_security_experiment.py`) inyecta ataques aleatorios y mide la capacidad del sistema para detectarlos, registrando métricas en SQLite y eventos en un servicio de auditoría.

## Arquitectura

```
servicio_de_pagos/     → Cliente: cifra datos y envía al proveedor
proveedor_de_pagos/    → API (puerto 5000): recibe, valida token, descifra, detecta ataques
componente_auditoria/  → API (puerto 5001): registra eventos en SQLite (auditoria.db)
librerias/
  servicio_de_encripcion/  → Librería AES encrypt/decrypt
  orquestador/             → Librería RabbitMQ (opcional)
```

## Experimento de Seguridad

El script `run_security_experiment.py` ejecuta **60 iteraciones** contra el proveedor de pagos, inyectando aleatoriamente:

| Ataque | Qué hace | Detección |
|---|---|---|
| **Tampering** | Corrompe bytes del dato cifrado | Fallo al descifrar → HTTP 400 |
| **Spoofing** | Envía token de autenticación falso | Token inválido → HTTP 401 |
| **Sin cifrado** | Envía datos en texto plano | Campo `encrypted_data` ausente → HTTP 400 |
| **Normal** | Petición legítima (cifrada + token válido) | Pago exitoso → HTTP 201 |

Cada ataque detectado se registra en el componente de auditoría y las métricas (tipo, tiempo de detección, código HTTP, resultado) se guardan en `resultados_experimento.db`.

## Instalación

```powershell
cd experimento_seguridad
pip install -r requirements.txt
```

## Ejecución del Experimento

```powershell
python run_security_experiment.py
```

Esto levanta automáticamente los servidores (proveedor de pagos en puerto 5000, auditoría en puerto 5001), ejecuta las 60 iteraciones y muestra el resumen en consola.

### Ejemplo de salida

```
#    Tipo            Detectado    Tiempo(ms)   HTTP
-----------------------------------------------------
1    spoofing        Sí           138.0        401
2    tampering       Sí           32.28        400
3    normal          N/A          72.59        201
...

============================================================
RESUMEN DEL EXPERIMENTO DE SEGURIDAD
============================================================
Total iteraciones:      60
Peticiones normales:    15  (exitosas: 15)
Ataques inyectados:     45  (detectados: 45/45)
  tampering      : 15/15 detectados, promedio 63.6 ms
  spoofing       : 16/16 detectados, promedio 88.1 ms
  sin_cifrado    : 14/14 detectados, promedio 61.1 ms
============================================================
```

## Consultar resultados

**Base de datos de métricas** → `resultados_experimento.db` (tabla `resultados`)

**Auditoría** → Levantar el servicio y consultar con Postman o curl:
```powershell
python componente_auditoria/app.py
# GET http://127.0.0.1:5001/audit
```

## Ejecución manual (sin experimento)

```powershell
# Terminal 1: Proveedor de pagos
python proveedor_de_pagos/app.py

# Terminal 2: Servicio de pagos (presionar 'p' para generar pago)
python servicio_de_pagos/app.py
```
