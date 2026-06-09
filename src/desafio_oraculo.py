import json

from mensagem_segura import criar_pacote

TOPICO_ORACULO = "sisdef/direto/oraculo"


def solicitar_desafio(client, id_unidade):
    """
    Solicita um novo desafio ao Oráculo.
    """

    mensagem = {
        "id_unidade": id_unidade,
        "cmd": "desafio"
    }

    client.publish(
        TOPICO_ORACULO,
        json.dumps(mensagem)
    )

    print("Desafio solicitado.")


def criar_pacote_oraculo(
    resposta,
    rsa_publica_oraculo,
    ecdsa_privada,
    id_unidade
):
    """
    Cria o pacote de resposta para o Oráculo.

    O conteúdo protegido deve ser apenas a string da resposta,
    conforme especificado no PDF.
    """

    print("\nConteúdo que será protegido:")
    print(repr(str(resposta)))

    pacote = criar_pacote(
        str(resposta),
        rsa_publica_oraculo,
        ecdsa_privada,
        id_unidade
    )

    pacote["cmd"] = "resposta"

    return pacote


def enviar_resposta_oraculo(
    client,
    resposta,
    id_unidade,
    rsa_publica_oraculo,
    ecdsa_privada
):
    """
    Publica a resposta para o Oráculo.
    """

    pacote = criar_pacote_oraculo(
        resposta,
        rsa_publica_oraculo,
        ecdsa_privada,
        id_unidade
    )

    print("\n=== PACOTE ORÁCULO ===")
    print(json.dumps(
        pacote,
        indent=4,
        ensure_ascii=False
    ))
    print("======================\n")

    client.publish(
        TOPICO_ORACULO,
        json.dumps(pacote)
    )

    print(f"Resposta enviada ao Oráculo: {resposta}")