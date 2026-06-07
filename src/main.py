import paho.mqtt.client as mqtt
import json
import hashlib
from key_manager import carregar_chaves, carregar_identidades, salvar_identidade, load_rsa_private_key, load_ecdsa_pub_key
from mensagem_segura import processar_pacote
from utils import verificar_assinatura
from revogacao_manager import adicionar_revogada, esta_revogada


BROKER = "broker.hivemq.com"

ID_UNIDADE = "ut-echo"

TOPICOS = [
    f"sisdef/direto/{ID_UNIDADE}",
    "sisdef/broadcast/revogacao",
    "sisdef/broadcast/chaves/+"
]

def publicar_identidade(client):

    dados = carregar_chaves()

    mensagem = {
        "id_unidade": ID_UNIDADE,
        "chave_publica_rsa": dados["rsa"]["public_key"],
        "chave_publica_ecdsa": dados["ecdsa"]["public_key"]
    }

    topico = f"sisdef/broadcast/chaves/{ID_UNIDADE}"

    client.publish(
        topico,
        json.dumps(mensagem),
        retain=True
    )

    print("Identidade publicada!")
    print("Topico:", topico)

def on_connect(client, userdata, flags, rc):

    print("Conectado!")

    publicar_identidade(client)

    for topico in TOPICOS:
        client.subscribe(topico)
        print(f"Inscrito em {topico}")


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

def on_message(client, userdata, msg):


    try:

        mensagem = msg.payload.decode()

        print("\nMensagem recebida")
        print("Topico:", msg.topic)



        if msg.topic.startswith("sisdef/broadcast/chaves/"):

            dados = json.loads(mensagem)
            if esta_revogada(dados["id_unidade"]):
                print("Chave ignorada (revogada)")
                return

            if "chave_publica_ecdsa" in dados:

                chave_assinatura = (dados["chave_publica_ecdsa"])


            else:

                print("Mensagem ignorada")
                return

            salvar_identidade(dados["id_unidade"],dados["chave_publica_rsa"],chave_assinatura)

            print(
                f"Identidade salva: "
                f"{dados['id_unidade']}"
            )


        elif msg.topic == "sisdef/broadcast/revogacao":

            dados = json.loads(mensagem)

            remetente = dados["remetente"]

            identidades = carregar_identidades()

            if remetente not in identidades:

                raise Exception("Remetente da revogação desconhecido")

            chave_pub = load_ecdsa_pub_key(identidades[remetente]["ecdsa"])

            revogacao = dados["revogacao"]

            hash_rev = hashlib.sha256(
                json.dumps(
                    revogacao,
                    sort_keys=True
                ).encode()
            ).digest()

            assinatura = bytes.fromhex(dados["assinatura_b64"])

            assinatura_valida = verificar_assinatura(hash_rev, assinatura, chave_pub)

            if not assinatura_valida:

                raise Exception("Assinatura da revogação inválida")

            unidade = revogacao["id_unidade"]

            adicionar_revogada(unidade)

            print(f"Unidade revogada: {unidade}")


        else:

            pacote = json.loads(mensagem)

            texto = (receber_mensagem_segura(pacote))

            print("\nMENSAGEM SEGURA RECEBIDA")

            print(
                f"De: "
                f"{pacote['id_unidade']}"
            )

            print(
                f"Texto: "
                f"{texto}"
            )

    except Exception as e:

        print("ERRO:",e)


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

client.loop_forever()

