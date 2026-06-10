import json

from utils import gerar_rsa, gerar_ecdsa
from key_manager import export_keys_as_string


def criar_chaves():
    rsa_priv = gerar_rsa()
    rsa_pub = rsa_priv.public_key()

    ecdsa_priv = gerar_ecdsa()
    ecdsa_pub = ecdsa_priv.public_key()

    rsa_dict = export_keys_as_string(rsa_priv, rsa_pub)

    ecdsa_dict = export_keys_as_string(ecdsa_priv, ecdsa_pub)

    dados = {
        "rsa": rsa_dict,
        "ecdsa": ecdsa_dict
    }

    with open(
        "minhas_chaves.json",
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            indent=4
        )


if __name__ == "__main__":
    criar_chaves()