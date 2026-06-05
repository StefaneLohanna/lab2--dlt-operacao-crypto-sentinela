import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client()

client.connect(
    "broker.hivemq.com",
    1883,
    60
)

client.loop_start()

mensagem = {
    "id_unidade": "ut-bravo"
}

resultado = client.publish(
    "sisdef/broadcast/revogacao",
    json.dumps(mensagem)
)

print("Status:", resultado.rc)

time.sleep(3)

client.loop_stop()
client.disconnect()