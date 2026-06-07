import json
import time
import hashlib

import paho.mqtt.client as mqtt

from key_manager import carregar_chaves, load_ecdsa_private_key
from utils import assinar


ID_UNIDADE = "ut-echo"
ALVO = "ut-bravo"

client = mqtt.Client()

client.connect("broker.hivemq.com", 1883, 60)

client.loop_start()

dados = carregar_chaves()

ecdsa_privada = load_ecdsa_private_key(dados["ecdsa"]["private_key"])

revogacao = {"id_unidade": ALVO}

hash_rev = hashlib.sha256(json.dumps(revogacao,sort_keys=True).encode()).digest()

assinatura = assinar(hash_rev,ecdsa_privada)

mensagem = {
    "remetente": ID_UNIDADE,
    "revogacao": revogacao,
    "assinatura_b64": assinatura.hex()
}

client.publish(
    "sisdef/broadcast/revogacao",
    json.dumps(mensagem)
)

print("Revogação publicada")


client.loop_stop()
client.disconnect()