import base64
import hashlib

from utils import (
    decifrar_chave_sessao,
    descriptografar_aes,
    verificar_assinatura
)

def abrir_pacote(
    pacote,
    chave_privada_rsa,
    chave_publica_ecdsa
):

    chave_sessao_cifrada = (
        base64.b64decode(
            pacote["chave_sessao_cifrada_b64"]
        )
    )

    nonce = (
        base64.b64decode(
            pacote["nonce_b64"]
        )
    )

    ciphertext = (
        base64.b64decode(
            pacote["ciphertext_b64"]
        )
    )

    tag = (
        base64.b64decode(
            pacote["tag_autenticacao_b64"]
        )
    )

    assinatura = (
        base64.b64decode(
            pacote["assinatura_b64"]
        )
    )

    chave_sessao = (
        decifrar_chave_sessao(
            chave_sessao_cifrada,
            chave_privada_rsa
        )
    )

    ciphertext_completo = (
        ciphertext + tag
    )

    mensagem = (
        descriptografar_aes(
            chave_sessao,
            nonce,
            ciphertext_completo
        )
    )

    hash_msg = hashlib.sha256(
        mensagem
    ).digest()

    assinatura_valida = (
        verificar_assinatura(
            hash_msg,
            assinatura,
            chave_publica_ecdsa
        )
    )

    if not assinatura_valida:

        raise Exception(
            "Assinatura inválida"
        )

    return mensagem.decode()