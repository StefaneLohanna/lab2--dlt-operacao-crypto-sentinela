from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ec
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


def gerar_rsa():
    return rsa.generate_private_key(public_exponent=65537,key_size=2048)

def gerar_ecdsa():
    return ec.generate_private_key(ec.SECP256R1())



def criptografar_aes(mensagem: bytes):

    chave = AESGCM.generate_key(bit_length=256)

    aes = AESGCM(chave)

    nonce = os.urandom(12)

    ciphertext = aes.encrypt(nonce,mensagem,None)

    return chave, nonce, ciphertext


def descriptografar_aes(chave, nonce, ciphertext):

    aes = AESGCM(chave)

    return aes.decrypt(nonce, ciphertext, None)

def cifrar_chave_sessao(chave_sessao, chave_publica):

    return chave_publica.encrypt(
        chave_sessao,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def decifrar_chave_sessao(chave_cifrada, chave_privada):

    return chave_privada.decrypt(
        chave_cifrada,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def assinar(mensagem, chave_privada):

    return chave_privada.sign(
        mensagem,
        ec.ECDSA(
            hashes.SHA256()
        )
    )

def verificar_assinatura(mensagem, assinatura,chave_publica):

    try:

        chave_publica.verify(
            assinatura,
            mensagem,
            ec.ECDSA(
                hashes.SHA256()
            )
        )

        return True

    except:
        return False
    
