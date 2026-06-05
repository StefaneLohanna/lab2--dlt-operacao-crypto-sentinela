import paho.mqtt.client as mqtt
import json
from key_manager import carregar_chaves, salvar_identidade, load_rsa_private_key, load_ecdsa_pub_key
from mensagem_segura import processar_pacote


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


def receber_mensagem_segura(
    pacote
):

    with open(
        "identidades.json",
        "r",
        encoding="utf-8"
    ) as f:

        identidades = json.load(f)

    remetente = pacote["id_unidade"]

    if remetente not in identidades:

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



        if msg.topic.startswith(
            "sisdef/broadcast/chaves/"
        ):

            dados = json.loads(
                mensagem
            )

            if "chave_publica_ecdsa" in dados:

                chave_assinatura = (
                    dados[
                        "chave_publica_ecdsa"
                    ]
                )

            elif "chave_publica_eddsa" in dados:

                chave_assinatura = (
                    dados[
                        "chave_publica_eddsa"
                    ]
                )

            else:

                print(
                    "Mensagem ignorada"
                )

                return

            salvar_identidade(
                dados["id_unidade"],
                dados["chave_publica_rsa"],
                chave_assinatura
            )

            print(
                f"Identidade salva: "
                f"{dados['id_unidade']}"
            )


        elif msg.topic == "sisdef/broadcast/revogacao":

            dados = json.loads(mensagem)

            unidade = dados["id_unidade"]

            with open(
                "identidades.json",
                "r",
                encoding="utf-8"
            ) as f:

                identidades = json.load(f)

            if unidade in identidades:

                del identidades[unidade]

                with open(
                    "identidades.json",
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        identidades,
                        f,
                        indent=4
                    )

                print(
                    f"Identidade revogada: {unidade}"
                )

            else:

                print(
                    f"Unidade {unidade} nao encontrada"
                )


        else:

            pacote = json.loads(
                mensagem
            )

            texto = (
                receber_mensagem_segura(
                    pacote
                )
            )

            print(
                "\nMENSAGEM SEGURA RECEBIDA"
            )

            print(
                f"De: "
                f"{pacote['id_unidade']}"
            )

            print(
                f"Texto: "
                f"{texto}"
            )

    except Exception as e:

        print(
            "ERRO:",
            e
        )


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

client.loop_forever()

