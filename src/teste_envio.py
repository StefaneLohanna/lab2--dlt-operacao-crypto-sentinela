import json

from mensagem_segura import criar_pacote

from key_manager import (
    carregar_chaves,
    load_rsa_pub_key,
    load_ecdsa_private_key
)

minhas_chaves = carregar_chaves()

with open(
    "identidades.json",
    "r"
) as f:

    identidades = json.load(f)

rsa_bravo = load_rsa_pub_key(
    identidades["ut-bravo"]["rsa"]
)

ecdsa_privada = load_ecdsa_private_key(
    minhas_chaves["ecdsa"]["private_key"]
)

pacote = criar_pacote(
    "Mensagem ultra secreta",
    rsa_bravo,
    ecdsa_privada,
    "ut-echo"
)

print(
    json.dumps(
        pacote,
        indent=4
    )
)