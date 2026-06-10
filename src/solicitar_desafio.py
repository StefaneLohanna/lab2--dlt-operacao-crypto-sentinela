import paho.mqtt.client as mqtt
from desafio_oraculo import solicitar_desafio

BROKER = "broker.hivemq.com"
ID_UNIDADE = "ut-echo"


def on_connect(client, userdata, flags, rc):
    print("Conectado!")

    solicitar_desafio(client, ID_UNIDADE)

    client.disconnect()


def main():
    client = mqtt.Client()

    client.on_connect = on_connect

    client.connect(BROKER, 1883, 60)

    client.loop_forever()


if __name__ == "__main__":
    main()