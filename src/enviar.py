import paho.mqtt.client as mqtt

from mensageria import enviar_mensagem_segura

BROKER = "broker.hivemq.com"

client = mqtt.Client()

client.connect(
    BROKER,
    1883,
    60
)

client.loop_start()

unidade_destino = "ut-bravo"
mensagem = 'Mensagem secreta do Echo'

enviar_mensagem_segura(client, unidade_destino, mensagem)

client.loop_stop()
client.disconnect()