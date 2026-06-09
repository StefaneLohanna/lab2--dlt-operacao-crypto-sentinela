import json
import time
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
TOPICO_NOTAS = "sisdef/broadcast/notas"


def on_message(client, userdata, msg):
    print("\n=== PLACAR ===")
    print(json.dumps(
        json.loads(msg.payload.decode()),
        indent=4,
        ensure_ascii=False
    ))
    print("==============\n")


def main():

    client = mqtt.Client()

    client.on_message = on_message

    client.connect(
        BROKER,
        1883,
        60
    )

    client.subscribe(TOPICO_NOTAS)

    client.loop_start()

    client.publish(
        TOPICO_NOTAS,
        json.dumps({
            "cmd": "atualizar_notas"
        })
    )

    time.sleep(5)

    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()