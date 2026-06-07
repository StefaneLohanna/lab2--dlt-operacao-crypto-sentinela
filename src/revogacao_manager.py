import json
import os

ARQUIVO = "revogadas.json"


def carregar_revogadas():

    if not os.path.exists(ARQUIVO):
        return []

    with open(
        ARQUIVO,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def adicionar_revogada(id_unidade):

    revogadas = carregar_revogadas()

    if id_unidade not in revogadas:
        revogadas.append(id_unidade)

    with open(
        ARQUIVO,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            revogadas,
            f,
            indent=4
        )


def esta_revogada(id_unidade):

    revogadas = carregar_revogadas()

    return id_unidade in revogadas