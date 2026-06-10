import hashlib
import json

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ec
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from key_manager import carregar_identidades, load_ecdsa_pub_key, salvar_identidade
from revogacao_manager import adicionar_revogada, esta_revogada


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
    

def processar_chave(mensagem):
    dados = json.loads(mensagem)

    if esta_revogada(dados["id_unidade"]):
        print("Chave ignorada (revogada)")
        return

    chave_assinatura = dados.get("chave_publica_ecdsa")

    if chave_assinatura is None:
        print("Mensagem ignorada")
        return

    salvar_identidade(
        dados["id_unidade"],
        dados["chave_publica_rsa"],
        chave_assinatura
    )

    print(f"Identidade salva: {dados['id_unidade']}")


def processar_revogacao(mensagem):
    dados = json.loads(mensagem)

    remetente = dados["remetente"]

    identidades = carregar_identidades()

    if remetente not in identidades:
        raise Exception("Remetente da revogação desconhecido")

    chave_pub = load_ecdsa_pub_key(
        identidades[remetente]["ecdsa"]
    )

    revogacao = dados["revogacao"]

    hash_rev = hashlib.sha256(
        json.dumps(
            revogacao,
            sort_keys=True
        ).encode()
    ).digest()

    assinatura = bytes.fromhex(
        dados["assinatura_b64"]
    )

    assinatura_valida = verificar_assinatura(
        hash_rev,
        assinatura,
        chave_pub
    )

    if not assinatura_valida:
        raise Exception(
            "Assinatura da revogação inválida"
        )

    unidade = revogacao["id_unidade"]

    adicionar_revogada(unidade)

    print(f"Unidade revogada: {unidade}")


def processar_mensagem_segura(mensagem):
    from mensagem_segura import receber_mensagem_segura

    pacote = json.loads(mensagem)

    texto = receber_mensagem_segura(pacote)

    print("\nMENSAGEM SEGURA RECEBIDA")

    print(
        f"De: "
        f"{pacote['id_unidade']}"
    )

    print(
        f"Texto: "
        f"{texto}"
    )


def obter_handler(topico):
    if topico.startswith("sisdef/broadcast/chaves/"):
        return processar_chave

    handlers = {
        "sisdef/broadcast/revogacao": processar_revogacao
    }

    return handlers.get(
        topico,
        processar_mensagem_segura
    )