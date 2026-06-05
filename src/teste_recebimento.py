import json

from key_manager import (
    carregar_chaves,
    carregar_rsa_privada,
    carregar_ecdsa_privada,
    load_rsa_pub_key,
    load_ecdsa_pub_key
)

from mensagem_segura import criar_pacote
from mensagem_recebida import abrir_pacote


dados = carregar_chaves()

rsa_publica = load_rsa_pub_key(
    dados["rsa"]["public_key"]
)

ecdsa_publica = load_ecdsa_pub_key(
    dados["ecdsa"]["public_key"]
)

rsa_privada = carregar_rsa_privada()

ecdsa_privada = carregar_ecdsa_privada()


pacote = criar_pacote(
    "Mensagem ultra secreta",
    rsa_publica,
    ecdsa_privada,
    "ut-echo"
)

print("\nPACOTE GERADO\n")

print(
    json.dumps(
        pacote,
        indent=4
    )
)

print("\n============================\n")

mensagem = abrir_pacote(
    pacote,
    rsa_privada,
    ecdsa_publica
)

print("MENSAGEM RECUPERADA\n")
print(mensagem)