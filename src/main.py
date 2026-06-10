from desafio_oraculo import solicitar_desafio
import paho.mqtt.client as mqtt
import json
from key_manager import carregar_chaves
from utils import obter_handler


BROKER = "broker.hivemq.com"

ID_UNIDADE = "ut-echo"

TOPICOS = [
    f"sisdef/direto/{ID_UNIDADE}",
    "sisdef/broadcast/revogacao",
    "sisdef/broadcast/chaves/+"
]

def publicar_identidade(client):
    dados = carregar_chaves()

    mensagem = {
        "id_unidade": ID_UNIDADE,
        "chave_publica_rsa": dados["rsa"]["public_key"],
        "chave_publica_ecdsa": dados["ecdsa"]["public_key"]
    }

    topico = f"sisdef/broadcast/chaves/{ID_UNIDADE}"

    client.publish(
        topico,
        json.dumps(mensagem),
        retain=True
    )

    print("Identidade publicada!")
    print("Topico:", topico)

def on_connect(client, userdata, flags, rc):
    print("Conectado!")

    publicar_identidade(client)

    for topico in TOPICOS:
        client.subscribe(topico)
        print(f"Inscrito em {topico}")


def on_message(client, userdata, msg):
    try:
        mensagem = msg.payload.decode()

        print("\nMensagem recebida")
        print("Topico:", msg.topic)

        handler = obter_handler(msg.topic)

        handler(mensagem)

    except Exception as e:

        print("ERRO:", e)


def main():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, 1883, 60)

    client.loop_forever()


if __name__ == "__main__":
    main()

