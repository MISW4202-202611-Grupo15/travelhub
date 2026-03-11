from librerias.orquestador.app import Orquestador
import time
import os

amqp_url = "amqps://lhgcccuh:zKo8dpTeDZvuvJIUB_da8uZXX3MeHjen@jackal.rmq.cloudamqp.com/lhgcccuh"
nombre_exchange = "events"
orquestador = Orquestador()
tiempo_de_resiliencia = 3