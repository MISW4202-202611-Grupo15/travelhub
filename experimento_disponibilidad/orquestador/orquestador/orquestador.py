import pika, json, threading


class Orquestador:

    def inicializar(self, url=None, exchange_name="events") -> bool:
        try:
            if url:
                params = pika.URLParameters(url)
            else:
                params = pika.ConnectionParameters("localhost")

            self.conn = pika.BlockingConnection(params)
            self.channel = self.conn.channel()
            self.channel.exchange_declare(exchange=exchange_name, exchange_type="topic")

            return True
        except Exception as e:
            print("Error conectando:", e)
            return False

    def publicar(self, exchange, routing_key, data):
        msg = json.dumps(data)
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=msg)

    def subscribirse(self, exchange, routing_key, handler):
        result = self.channel.queue_declare("", exclusive=True)
        queue = result.method.queue
        self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

        def callback(ch, method, properties, body):
            payload = json.loads(body)
            handler(method.routing_key, payload)

        self.channel.basic_consume(
            queue=queue, on_message_callback=callback, auto_ack=True
        )
        threading.Thread(target=self.channel.start_consuming, daemon=True).start()
