import time

import paho.mqtt.client as mqtt

from key_manager import (
    carregar_chaves,
    carregar_identidades,
    load_ecdsa_private_key,
    load_rsa_pub_key
)

from desafio_oraculo import enviar_resposta_oraculo


BROKER = "broker.hivemq.com"
ID_UNIDADE = "ut-echo"

RESPOSTA = "16"


def main():
    resposta = RESPOSTA

    identidades = carregar_identidades()

    id_oraculo = "oraculo"

    if id_oraculo not in identidades:
        raise Exception(
            f"Oráculo não encontrado em identidades.json: "
            f"{id_oraculo}"
        )

    rsa_publica_oraculo = load_rsa_pub_key(
        identidades[id_oraculo]["rsa"]
    )

    minhas_chaves = carregar_chaves()

    ecdsa_privada = load_ecdsa_private_key(
        minhas_chaves["ecdsa"]["private_key"]
    )

    client = mqtt.Client()

    client.connect(
        BROKER,
        1883,
        60
    )

    client.loop_start()

    enviar_resposta_oraculo(
        client,
        resposta,
        ID_UNIDADE,
        rsa_publica_oraculo,
        ecdsa_privada
    )

    time.sleep(2)

    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()