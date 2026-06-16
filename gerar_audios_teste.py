"""
Script para geração dos arquivos de áudio de teste.

Utiliza gTTS (Google Text-to-Speech) para sintetizar os comandos
de voz em português brasileiro e os salva na pasta audios/.

Execute este script UMA vez antes de rodar os testes:
    python gerar_audios_teste.py
"""

import os

try:
    from gtts import gTTS
    GTTS_DISPONIVEL = True
except ImportError:
    GTTS_DISPONIVEL = False

try:
    import pyttsx3
    PYTTSX3_DISPONIVEL = True
except ImportError:
    PYTTSX3_DISPONIVEL = False

import soundfile as sf
import numpy as np

PASTA_AUDIOS = "audios"

# Comandos que serão gravados para os testes
COMANDOS_TESTE = {
    "abrir_cortinas.wav": "abrir cortinas",
    "fechar_cortinas.wav": "fechar cortinas",
    "ativar_fumaca.wav": "ativar fumaça",
    "desativar_fumaca.wav": "desativar fumaça",
    "descer_telao.wav": "descer telão",
    "abaixar_telao.wav": "abaixar telão",
    "subir_telao.wav": "subir telão",
    "acionar_emergencia.wav": "acionar emergência",
}


def gerar_com_gtts(texto, caminho_saida):
    """Gera áudio usando gTTS e salva em WAV via pydub."""
    try:
        from pydub import AudioSegment
        import io

        tts = gTTS(text=texto, lang="pt-br", slow=False)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        audio = AudioSegment.from_mp3(mp3_buffer)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(caminho_saida, format="wav")
        return True
    except Exception as e:
        print(f"  Erro com gTTS: {e}")
        return False


def gerar_silencio(caminho_saida, duracao_s=3):
    """
    Gera um arquivo WAV de silêncio como fallback.
    O arquivo terá o nome correto mas não representará fala real —
    serve apenas para que os testes possam ser executados sem erros de I/O.
    """
    taxa = 16000
    amostras = np.zeros(int(taxa * duracao_s), dtype=np.float32)
    sf.write(caminho_saida, amostras, taxa)
    return True


if __name__ == "__main__":
    os.makedirs(PASTA_AUDIOS, exist_ok=True)

    print("Gerando arquivos de áudio para testes...\n")

    for nome_arquivo, texto in COMANDOS_TESTE.items():
        caminho = os.path.join(PASTA_AUDIOS, nome_arquivo)

        if os.path.exists(caminho):
            print(f"  [OK] {nome_arquivo} já existe — ignorando.")
            continue

        print(f"  Gerando: '{texto}' → {nome_arquivo}")
        gerado = False

        if GTTS_DISPONIVEL:
            gerado = gerar_com_gtts(texto, caminho)

        if not gerado:
            print(f"    gTTS indisponível ou falhou. Gerando silêncio como placeholder.")
            gerar_silencio(caminho)
            gerado = True

        if gerado:
            print(f"  ✔  {nome_arquivo} salvo.")
        else:
            print(f"  ✘  Falha ao gerar {nome_arquivo}.")

    print("\nConcluído! Arquivos disponíveis em:", PASTA_AUDIOS)
    print("\nIMPORTANTE: Se os arquivos foram gerados como silêncio (placeholder),")
    print("grave manualmente os comandos de voz para testes mais precisos.")
