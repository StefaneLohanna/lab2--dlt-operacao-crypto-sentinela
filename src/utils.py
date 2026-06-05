from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ec
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


def gerar_rsa():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )


def gerar_ecdsa():
    return ec.generate_private_key(
        ec.SECP256R1()
    )


def criptografar_aes(mensagem: bytes):

    chave = AESGCM.generate_key(bit_length=256)

    aes = AESGCM(chave)

    nonce = os.urandom(12)

    ciphertext = aes.encrypt(
        nonce,
        mensagem,
        None
    )

    return chave, nonce, ciphertext


def descriptografar_aes(
    chave,
    nonce,
    ciphertext
):

    aes = AESGCM(chave)

    return aes.decrypt(
        nonce,
        ciphertext,
        None
    )

def cifrar_chave_sessao(
    chave_sessao,
    chave_publica
):

    return chave_publica.encrypt(
        chave_sessao,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def decifrar_chave_sessao(
    chave_cifrada,
    chave_privada
):

    return chave_privada.decrypt(
        chave_cifrada,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def assinar(hash_msg, chave_privada):

    return chave_privada.sign(
        hash_msg,
        ec.ECDSA(hashes.SHA256())
    )

def verificar_assinatura(
    hash_msg,
    assinatura,
    chave_publica
):

    try:

        chave_publica.verify(
            assinatura,
            hash_msg,
            ec.ECDSA(hashes.SHA256())
        )

        return True

    except:
        return False
    
def processar_pacote(
    pacote,
    chave_privada_rsa,
    chave_publica_ecdsa
):

    ciphertext = base64.b64decode(
        pacote["ciphertext_b64"]
    )

    tag = base64.b64decode(
        pacote["tag_autenticacao_b64"]
    )

    nonce = base64.b64decode(
        pacote["nonce_b64"]
    )

    chave_sessao_cifrada = (
        base64.b64decode(
            pacote["chave_sessao_cifrada_b64"]
        )
    )

    assinatura = base64.b64decode(
        pacote["assinatura_b64"]
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

    mensagem_bytes = (
        descriptografar_aes(
            chave_sessao,
            nonce,
            ciphertext_completo
        )
    )

    hash_msg = hashlib.sha256(
        mensagem_bytes
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

    return mensagem_bytes.decode()