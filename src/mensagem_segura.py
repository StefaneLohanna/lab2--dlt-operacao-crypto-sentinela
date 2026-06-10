import base64

from key_manager import carregar_chaves, carregar_identidades, load_ecdsa_pub_key, load_rsa_private_key
from revogacao_manager import esta_revogada
from utils import criptografar_aes, cifrar_chave_sessao, assinar, decifrar_chave_sessao, descriptografar_aes, verificar_assinatura


def criar_pacote(mensagem_texto, chave_rsa_destino, chave_privada_ecdsa,remetente):
    mensagem_bytes = mensagem_texto.encode()

    assinatura = assinar(mensagem_bytes, chave_privada_ecdsa)

    chave_sessao, nonce, ciphertext_com_tag = (criptografar_aes(mensagem_bytes))

    tag = ciphertext_com_tag[-16:]
    ciphertext = ciphertext_com_tag[:-16]

    chave_cifrada = (cifrar_chave_sessao(chave_sessao, chave_rsa_destino))

    pacote = {

        "id_unidade": remetente,

        "ciphertext_b64":
        base64.b64encode(ciphertext).decode(),

        "tag_autenticacao_b64":
        base64.b64encode(tag).decode(),

        "nonce_b64":
        base64.b64encode(nonce).decode(),

        "chave_sessao_cifrada_b64":
        base64.b64encode(chave_cifrada).decode(),

        "assinatura_b64":
        base64.b64encode(assinatura).decode()
    }

    return pacote

def processar_pacote(pacote, chave_privada_rsa, chave_publica_ecdsa):
    ciphertext = base64.b64decode(pacote["ciphertext_b64"])

    tag = base64.b64decode(pacote["tag_autenticacao_b64"])

    nonce = base64.b64decode(pacote["nonce_b64"])

    chave_sessao_cifrada = (base64.b64decode(pacote["chave_sessao_cifrada_b64"]))

    assinatura = base64.b64decode(pacote["assinatura_b64"])

    chave_sessao = (decifrar_chave_sessao(chave_sessao_cifrada, chave_privada_rsa))

    ciphertext_completo = (ciphertext + tag)

    mensagem_bytes = (descriptografar_aes(chave_sessao, nonce, ciphertext_completo))

    assinatura_valida = (verificar_assinatura(mensagem_bytes, assinatura, chave_publica_ecdsa))

    if not assinatura_valida:

        raise Exception("Assinatura inválida")

    return mensagem_bytes.decode()


def receber_mensagem_segura(pacote):
    identidades = carregar_identidades()

    remetente = pacote["id_unidade"]

    if remetente not in identidades or esta_revogada(remetente):

        raise Exception(
            f"Remetente revogado ou desconhecido: "
            f"{remetente}"
        )
    
    chave_pub_ecdsa = (
        load_ecdsa_pub_key(
            identidades[remetente]["ecdsa"]
        )
    )

    minhas_chaves = carregar_chaves()

    rsa_privada = (
        load_rsa_private_key(
            minhas_chaves["rsa"]["private_key"]
        )
    )

    return processar_pacote(
        pacote,
        rsa_privada,
        chave_pub_ecdsa
    )