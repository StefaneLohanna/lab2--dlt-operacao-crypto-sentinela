import base64
from cryptography.hazmat.primitives import serialization
import json
import os
import base64

def export_keys_as_string(private_key, public_key):
    _priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    _pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    chaves = {
        "private_key": base64.b64encode(_priv_bytes).decode(),
        "public_key": base64.b64encode(_pub_bytes).decode()
    }

    return chaves


def load_rsa_pub_key(b64_str):
    key_bytes = base64.b64decode(b64_str)
    return serialization.load_der_public_key(key_bytes)

def load_ecdsa_pub_key(b64_str):
    key_bytes = base64.b64decode(b64_str)
    return serialization.load_der_public_key(key_bytes)

def carregar_chaves():

    if not os.path.exists("minhas_chaves.json"):
        return None

    with open(
        "minhas_chaves.json",
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)
    
def existe_chaves():

    return os.path.exists(
        "minhas_chaves.json"
    )


def salvar_identidade(
    id_unidade,
    rsa_pub,
    ecdsa_pub
):

    import json
    import os

    arquivo = "identidades.json"

    if os.path.exists(arquivo):

        with open(
            arquivo,
            "r",
            encoding="utf-8"
        ) as f:

            dados = json.load(f)

    else:

        dados = {}

    dados[id_unidade] = {
        "rsa": rsa_pub,
        "ecdsa": ecdsa_pub
    }

    with open(
        arquivo,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dados,
            f,
            indent=4
        )


def load_rsa_private_key(b64_str):

    key_bytes = base64.b64decode(
        b64_str
    )

    return serialization.load_der_private_key(
        key_bytes,
        password=None
    )

def load_ecdsa_private_key(b64_str):

    key_bytes = base64.b64decode(
        b64_str
    )

    return serialization.load_der_private_key(
        key_bytes,
        password=None
    )

def carregar_rsa_privada():

    dados = carregar_chaves()

    return load_rsa_private_key(
        dados["rsa"]["private_key"]
    )


def carregar_ecdsa_privada():

    dados = carregar_chaves()

    return load_ecdsa_private_key(
        dados["ecdsa"]["private_key"]
    )