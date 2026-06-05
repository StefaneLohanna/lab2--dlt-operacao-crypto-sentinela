import paho.mqtt.client as mqtt

from mensageria import (
    enviar_mensagem_segura
)

BROKER = "broker.hivemq.com"

client = mqtt.Client()

client.connect(
    BROKER,
    1883,
    60
)

client.loop_start()

enviar_mensagem_segura(
    client,
    "ut-bravo",
    "Mensagem secreta do Echo"
)

client.loop_stop()
client.disconnect()