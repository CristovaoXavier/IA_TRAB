from robo import inicializar, get_resposta as get_resposta_robo, NOME_ROBO
from flask import Flask, Response

import json

servico = Flask(NOME_ROBO)
inicializado, robo = inicializar()

@servico.get("/")
def get_info():
    info = {
        "descrição": "Robô de atendimento do IFBA",
        "email": "luispscarvalho@gmail.com",
        "versão": "1.0"
    }

    return Response(json.dumps(info), status=200, mimetype="application/json")

@servico.get("/resposta/<string:mensagem>")
def get_resposta(mensagem):
    resposta, confianca = get_resposta_robo(robo, mensagem)

    resposta = {
        "resposta": resposta,
        "confianca": confianca
    }

    return Response(json.dumps(resposta), status=200, mimetype="application/json")


if __name__ == "__main__":
    if inicializado:
        servico.run(host="0.0.0.0", port=6000, debug=True)
    else:
        print("não foi possível inicializar o robô")

