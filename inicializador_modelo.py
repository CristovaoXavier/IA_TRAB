from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

MODELO = "lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2"

TAXA_AMOSTRAGEM = 16_000


def iniciar_modelo(nome_modelo, dispositivo="cpu"):
    iniciado, processador, modelo = False, None, None

    try:
        processador = Wav2Vec2Processor.from_pretrained(nome_modelo)
        modelo = Wav2Vec2ForCTC.from_pretrained(nome_modelo).to(dispositivo)

        iniciado = True
    except Exception as e:
        print(f"erro iniciando modelo: {str(e)}")

    return iniciado, processador, modelo


if __name__ == "__main__":
    iniciado, _, __ = iniciar_modelo(MODELO)
    if iniciado:
        print(f"modelo {MODELO} iniciado com sucesso")
    else:
        print("falha ao iniciar o modelo")
