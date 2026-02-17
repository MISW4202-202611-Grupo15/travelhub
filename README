# Experimento de táctica de arquitectura de detección de fallas para el favocerimiento de la disponibilidad

## Objetivo

Este proyecto busca simular el monitoreo de la disponibilidad de microservicios utilizando mensajería asíncrona sin comunicación directa entre los servicios.

---

## Contenido del repositorio

Este repositorio contiene una simulación de una arquitectura distribuida basada en comunicación asíncrona mediante un broker de mensajes (orquestador).

Dentro del repositorio existen **cuatro carpetas principales**, cada una correspondiente a un proyecto Python:

* **monitor/** → Simula el componente Monitor del sistema
* **mock1/** → Simula un servicio del sistema (consumidor de ping)
* **mock2/** → Simula otro servicio del sistema (consumidor de ping)
* **orquestador/** → Librería compartida que encapsula la comunicación con el broker

La librería `orquestador` es utilizada por todos los demás componentes para conectarse y comunicarse con el broker de mensajería en la nube.

---

## Componentes del sistema

### Monitor

Aplicación desarrollada en Python encargada de verificar la disponibilidad de otros componentes del sistema.

Roles:

* Productor de eventos `ping`
* Consumidor de eventos `echo`

El Monitor envía periódicamente mensajes para comprobar si los demás servicios están activos.

---

### Mock 1 y Mock 2

Servicios simulados que representan microservicios reales dentro de la arquitectura.

Roles:

* Consumidores de eventos `ping`
* Productores de eventos `echo`

Cuando reciben un `ping`, responden con un `echo`, indicando que el servicio se encuentra disponible.

---

### Orquestador (Librería)

Corresponde a una librería Python compartida encargada de:

* Gestionar la conexión al broker
* Publicar eventos
* Suscribirse a colas
* Abstraer la lógica de mensajería

Todos los componentes dependen de esta librería para comunicarse, evitando duplicar lógica de conexión y manteniendo desacoplados los servicios de la infraestructura de mensajería.

---

### Orquestador (Broker de Mensajes)

El broker del sistema fue implementado utilizando **CloudAMQP (RabbitMQ as a Service)**.

Su propósito es desacoplar los servicios permitiendo comunicación asíncrona entre productores y consumidores, facilitando:

* Escalabilidad
* Tolerancia a fallos
* Distribución de carga
* Independencia entre componentes

---

## Flujo de comunicación

1. El **Monitor** envía periódicamente eventos `ping`
2. **Mock1** y **Mock2** reciben el `ping`
3. Cada mock responde enviando un evento `echo`
4. El **Monitor** consume los `echo` y determina qué servicios están activos

Este comportamiento implementa un mecanismo de **heartbeat distribuido**.

---

## Cómo ejecutar el sistema

Antes de iniciar los componentes es importante crear el ambiente virtual e instalar las dependencias del proyecto.

1. Abrir **tres terminales**.

2. En cada terminal ubicarse en la carpeta raíz de cada componente:

   * Terminal 1 → `monitor/`
   * Terminal 2 → `mock1/`
   * Terminal 3 → `mock2/`

3. En cada una ejecutar:

```
python app.py
```

Una vez iniciados, el Monitor comenzará a enviar eventos `ping` y recibirá `echo` desde los otros componentes mostrando su estado.

Para conocer como implementar el broker de mansajería consultar las referencias al final del documento.

---

## Simular la caída de un servicio

Para simular que un componente deja de estar disponible:

* Cerrar la terminal donde se está ejecutando el componente, o
* Presionar `Ctrl + C`

El Monitor dejará de recibir los `echo` correspondientes y podrá detectar que el servicio se encuentra inactivo.

---

## Infraestructura utilizada

* RabbitMQ
* CloudAMQP
* Protocolo AMQP
* Implementación de clientes en Python

---

## Referencias

La implementación conceptual del broker se basó en la documentación oficial de CloudAMQP:

* https://www.cloudamqp.com/blog/part1-rabbitmq-for-beginners-what-is-rabbitmq.html
* https://www.cloudamqp.com/blog/part3-rabbitmq-for-beginners_the-management-interface.html
