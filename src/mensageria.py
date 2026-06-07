import json

from mensagem_segura import criar_pacote

from key_manager import carregar_chaves, carregar_identidades, load_rsa_pub_key, load_ecdsa_private_key
from revogacao_manager import esta_revogada


def enviar_mensagem_segura(client, destino, texto):

    identidades = carregar_identidades()
    if destino not in identidades:
        print(
            f"Destino {destino} "
            f"não possui identidade válida."
        )
        return
    
    if esta_revogada(destino):
        print(f"Destino {destino} está revogado.")
        return

    rsa_publica_destino = (load_rsa_pub_key(identidades[destino]["rsa"]))

    minhas_chaves = carregar_chaves()

    ecdsa_privada = (load_ecdsa_private_key(minhas_chaves["ecdsa"]["private_key"]))

    pacote = criar_pacote(texto,rsa_publica_destino,ecdsa_privada,"ut-echo")

    topico = f"sisdef/direto/{destino}"

    print("\nPACOTE ENVIADO:")
    print(json.dumps(pacote,indent=4))

    client.publish(
        topico,
        json.dumps(pacote)
    )

    print(f"Mensagem enviada para {destino}")