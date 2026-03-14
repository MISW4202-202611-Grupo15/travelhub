# Experimento de Seguridad - Sistema de Pagos con Encriptación

## 📋 Descripción del Proyecto

Este proyecto implementa un **sistema de pagos seguro** que demuestra el uso de encriptación AES (Advanced Encryption Standard) para proteger información bancaria sensible durante su transmisión entre servicios.

## 🏗️ Arquitectura del Sistema

El proyecto está compuesto por los siguientes componentes:

### 1. **Servicio de Pagos** (`servicio_de_pagos/`)
- **Rol**: Cliente que solicita pagos
- **Funcionalidad**: 
  - Encripta datos bancarios sensibles (documento, banco, cuenta, tipo de cuenta)
  - Envía la información encriptada al Proveedor de Pagos
  - Utiliza algoritmo AES con modo CBC para la encriptación
- **Tecnologías**: Python, requests, CryptologyService

### 2. **Proveedor de Pagos** (`proveedor_de_pagos/`)
- **Rol**: API REST que procesa pagos
- **Funcionalidad**:
  - Recibe datos encriptados vía HTTP POST
  - Desencripta la información utilizando las claves correspondientes
  - Procesa el pago con los datos bancarios
  - Retorna código de estado de la transacción
- **Tecnologías**: Flask, Python, CryptologyService
- **Endpoint**: `POST /payment`

### 3. **Servicio de Encriptación** (`librerias/servicio_de_encripcion/`)
- **Rol**: Librería compartida de criptografía
- **Funcionalidad**:
  - Proporciona métodos `encrypt()` y `decrypt()`
  - Implementa AES-256 en modo CBC
  - Utiliza padding PKCS7
  - Genera claves derivadas mediante SHA-256
- **Tecnologías**: pycryptodome

### 4. **Orquestador** (`librerias/orquestador/`)
- **Rol**: Librería para comunicación asíncrona (opcional)
- **Funcionalidad**:
  - Gestiona conexión con RabbitMQ
  - Permite publicar y suscribirse a eventos
  - Facilita comunicación event-driven entre servicios
- **Tecnologías**: pika (RabbitMQ client)

### 5. **Registro de Auditoría** (`registro_de_auditoria/`)
- **Rol**: Servicio de auditoría (en desarrollo)
- **Funcionalidad**: Escucha eventos del sistema para registro de auditoría
- **Tecnologías**: Python, Orquestador

## 🔐 Flujo de Seguridad

```
┌─────────────────────┐
│ Servicio de Pagos   │
│                     │
│ 1. Datos sensibles  │
│ 2. Encriptar (AES)  │
└──────────┬──────────┘
           │ Datos Encriptados
           │ (Base64)
           ▼
┌─────────────────────┐
│ Proveedor de Pagos  │
│                     │
│ 3. Recibir datos    │
│ 4. Desencriptar     │
│ 5. Procesar pago    │
└─────────────────────┘
```

### Claves de Encriptación

El sistema utiliza dos pares de claves AES:

**Para Encriptación:**
- Llave: `MzQyNHg2NiEyQUxPPXxaUA==` (Base64)
- IV: `2648937582046372`

**Para Desencriptación:**
- Llave: `MDFBM3g1aTkwTDBXMjg0bA==` (Base64)
- IV: `1050701070905080`

> ⚠️ **Nota de Seguridad**: En un sistema de producción, estas claves NUNCA deben estar hardcodeadas en el código. Se deben usar variables de entorno o servicios de gestión de secretos (AWS Secrets Manager, Azure Key Vault, etc.).

## 📦 Dependencias

- **Python 3.8+**
- **Flask 3.0.2**: Framework web para el proveedor de pagos
- **requests 2.32.5**: Cliente HTTP para el servicio de pagos
- **pycryptodome**: Biblioteca de encriptación AES
- **pika**: Cliente RabbitMQ (para funcionalidad de orquestador)

## 🚀 Instalación y Ejecución

### Paso 1: Instalación de Dependencias

```powershell
# Navegar al directorio del experimento
cd experimento_seguridad

# Activar entorno virtual (si existe)
& "..\.venv\Scripts\Activate.ps1"

# Opción A: Instalar todas las dependencias desde el archivo consolidado
pip install -r requirements.txt

# Opción B: Instalar dependencias por componente
pip install pycryptodome  # Servicio de encriptación
pip install Flask==3.0.2  # Proveedor de pagos
pip install requests==2.32.5  # Servicio de pagos
pip install pika  # Orquestador (opcional)
```

### Paso 2: Ejecución del Sistema

**Terminal 1 - Iniciar Proveedor de Pagos (API)**
```powershell
cd proveedor_de_pagos
python app.py
```
La API estará disponible en `http://127.0.0.1:5000`

**Terminal 2 - Ejecutar Servicio de Pagos (Cliente)**
```powershell
cd servicio_de_pagos
python app.py
```
Presionar `p` para generar un pago de prueba

## 🧪 Pruebas del Sistema

1. **Iniciar el Proveedor de Pagos** (Terminal 1):
   ```powershell
   cd proveedor_de_pagos
   python app.py
   ```
   Verifica que el servidor Flask inicie en `http://127.0.0.1:5000`

2. **Ejecutar Servicio de Pagos** (Terminal 2):
   ```powershell
   cd servicio_de_pagos
   python app.py
   ```
   - Presiona `p` cuando se solicite
   - Observarás:
     - ✓ Datos sensibles originales
     - ✓ Datos encriptados (Base64)
     - ✓ Respuesta del servidor (código 201 si fue exitoso)

3. **Verificar Logs**:
   - En el Terminal 1 (Proveedor de Pagos) verás:
     - Datos encriptados recibidos
     - Datos desencriptados
     - Confirmación de pago realizado

## 📊 Ejemplo de Ejecución

**Servicio de Pagos (Cliente):**
```
**** DATOS SENSIBLES *****
{'documento': 10958346721, 'banco': 'BBVA', 'cuenta': 98563627121, 'tipo_cuenta': 'AHORROS'}

**** DATOS ENCRIPTADOS *****
aG9sYSBtdW5kbyBlbmNyaXB0YWRv...

**** REPUESTA DEL PAGO *****
201
Pago realizado
```

**Proveedor de Pagos (API):**
```
Esta es la información encriptada
{'encrypted_data': 'aG9sYSBtdW5kbyBlbmNyaXB0YWRv...'}

Esta es la información desencriptada
{'documento': 10958346721, 'banco': 'BBVA', 'cuenta': 98563627121, 'tipo_cuenta': 'AHORROS'}

127.0.0.1 - - [14/Mar/2026 10:30:45] "POST /payment HTTP/1.1" 201 -
```

## 🎯 Objetivos del Experimento

1. **Demostrar encriptación end-to-end** de datos sensibles
2. **Implementar AES-256** con modo CBC y padding adecuado
3. **Separar responsabilidades** entre cliente y servidor
4. **Validar transmisión segura** de información bancaria
5. **Mostrar buenas prácticas** de seguridad en microservicios

## 🔧 Posibles Mejoras

- Implementar gestión de claves mediante variables de entorno
- Agregar autenticación JWT entre servicios
- Implementar registro de auditoría completo
- Agregar validaciones de datos antes del procesamiento
- Implementar manejo de errores más robusto
- Agregar tests unitarios y de integración
- Implementar rate limiting en la API
- Usar HTTPS para la comunicación

## ⚠️ Solución de Problemas

**Error: "ModuleNotFoundError"**
```powershell
pip install -r requirements.txt
```

**Error: "Puerto 5000 en uso"**
- Cierra otras aplicaciones usando el puerto 5000
- O modifica el puerto en `proveedor_de_pagos/app.py` cambiando `app.run(debug=True, port=NUEVO_PUERTO)`

**Error: "Connection refused"**
- Verifica que el Proveedor de Pagos esté ejecutándose
- Espera unos segundos para que el servidor Flask inicie completamente
- Verifica que la URL sea correcta: `http://127.0.0.1:5000`

## 📝 Notas Importantes

- Este es un **proyecto educativo** para demostrar conceptos de seguridad
- **NO usar en producción** sin implementar las mejoras de seguridad necesarias
- Las claves están expuestas con fines demostrativos únicamente
- En producción, usar protocolos seguros (HTTPS/TLS) y gestión adecuada de secretos
