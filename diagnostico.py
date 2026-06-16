"""
diagnostico.py — Mostra exatamente o que o modelo transcreve para cada áudio.

Execute para descobrir como o modelo ASR interpreta cada comando:
    python diagnostico.py

Use a saída para ajustar config.json se necessário.
"""

import os
import sys
import torch
import json

from inicializador_modelo import iniciar_modelo, MODELO
from transcritor import carregar_fala, transcrever
from nltk import corpus, word_tokenize
import nltk

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

PASTA_AUDIOS = "audios"
CONFIGURACAO = "config.json"

AUDIOS_TESTE = [
    "abrir_cortinas.wav",
    "fechar_cortinas.wav",
    "ativar_fumaca.wav",
    "desativar_fumaca.wav",
    "descer_telao.wav",
    "subir_telao.wav",
    "acionar_emergencia.wav",
]

if __name__ == "__main__":
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo: {dispositivo}\n")

    iniciado, processador, modelo = iniciar_modelo(MODELO, dispositivo)
    if not iniciado:
        print("ERRO: modelo não pôde ser iniciado.")
        sys.exit(1)

    stopwords = set(corpus.stopwords.words("portuguese"))

    with open(CONFIGURACAO, encoding="utf-8") as f:
        config = json.load(f)
    sinonimos = config.get("sinonimos", {})

    print(f"{'ARQUIVO':<30} {'TRANSCRIÇÃO RAW':<35} {'TOKENS'}")
    print("─" * 90)

    for nome in AUDIOS_TESTE:
        caminho = os.path.join(PASTA_AUDIOS, nome)
        if not os.path.exists(caminho):
            print(f"{nome:<30} {'[arquivo não encontrado]'}")
            continue

        fala = carregar_fala(caminho)
        transcricao = transcrever(dispositivo, fala, modelo, processador)
        tokens = [t for t in word_tokenize(transcricao, language="portuguese")
                  if t not in stopwords]
        print(f"{nome:<30} {transcricao:<35} {tokens}")

    print("\nSe alguma transcrição estiver errada, adicione a variante")
    print("no campo 'dispositivos' ou 'sinonimos' do config.json.")
