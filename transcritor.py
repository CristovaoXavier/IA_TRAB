import torch
import soundfile as sf
import numpy as np

TAXA_AMOSTRAGEM = 16_000


def carregar_fala(audio_fala):
    """
    Carrega um arquivo de áudio WAV e o prepara para transcrição.
    Usa soundfile como backend principal (compatível com torchaudio >= 2.6
    sem necessidade do torchcodec).
    """
    # soundfile lê WAV/FLAC/OGG sem depender do torchcodec
    audio, amostragem = sf.read(audio_fala, dtype="float32", always_2d=True)

    # audio shape: (amostras, canais) → converte para mono
    if audio.shape[1] > 1:
        audio = audio.mean(axis=1)
    else:
        audio = audio[:, 0]

    # Converte para tensor PyTorch 1D
    audio = torch.from_numpy(audio)

    # Reamostragem para 16.000 Hz se necessário
    if amostragem != TAXA_AMOSTRAGEM:
        import torchaudio
        adaptador = torchaudio.transforms.Resample(amostragem, TAXA_AMOSTRAGEM)
        audio = adaptador(audio.unsqueeze(0)).squeeze(0)

    return audio


def transcrever(dispositivo, fala, modelo, processador):
    """Transcreve um tensor de áudio para texto."""
    saida = processador(
        fala, return_tensors="pt", sampling_rate=TAXA_AMOSTRAGEM
    ).input_values.to(dispositivo)

    saida = modelo(saida).logits

    predicao = torch.argmax(saida, dim=-1)
    transcricao = processador.batch_decode(predicao)[0]

    return transcricao.lower()
