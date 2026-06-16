from chatterbot import ChatBot

NOME_ROBO = "IFBABot"
CONFIANCA_MINIMA = 0.65

def inicializar():
    inicializado, robo = False, None

    try:
        robo = ChatBot(NOME_ROBO, read_only=True, logic_adapters=[{
            "import_path": "chatterbot.logic.BestMatch"
        }])

        inicializado = True
    except Exception as e:
        print(f"erro inicilizando o {NOME_ROBO}: {str(e)}")
        
    return inicializado, robo

# 🤖👤
def get_resposta(robo, mensagem):
    resposta = robo.get_response(mensagem.lower())

    return resposta.text, resposta.confidence


def executar_robo(robo):
    print(f"Olá, sou o IFBABot, robô de atendimento do IFBA. Posso esclarecer dúvidas sobre a instituição e sobre os cursos oferecidos. Deseja saber alguma coisa?")

    while True:
        mensagem = input("👤 ")
        resposta, confianca = get_resposta(robo, mensagem)

        if confianca >= CONFIANCA_MINIMA:
            print(f"🤖 {resposta} [confiança: {confianca}]")
        else:
            print(f"🤖 Ainda não sei responder esta pergunta. Você pode encontrar mais informações sobre o IFBA no site https://portal.ifba.edu.br/conquista [confiança: {confianca}]")


if __name__ == "__main__":
    inicializado, robo = inicializar()
    if inicializado:
        executar_robo(robo)