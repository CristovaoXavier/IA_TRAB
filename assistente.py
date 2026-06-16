"""
PalcoBot - Assistente Virtual para Automação de Palcos e Eventos
IFBA - Disciplina de Inteligência Artificial

Descrição:
    Assistente virtual com reconhecimento de voz para controle de dispositivos
    cênicos e de segurança em ambientes de eventos. Utiliza o modelo Wav2Vec2
    para transcrição de fala em português brasileiro e processa os comandos
    configurados em arquivo JSON externo.

Comandos disponíveis:
    1. "abrir cortinas"  / "fechar cortinas"
    2. "ativar fumaça"   / "desativar fumaça"
    3. "descer telão"    / "subir telão"
    4. "acionar emergência"

Controles do assistente:
    ENTER       → inicia gravação de um comando de voz
    E + ENTER   → encerra o assistente pelo teclado
    Falar "encerrar assistente" → encerra pelo microfone

Uso:
    python assistente.py
"""

from nltk import word_tokenize, corpus
from inicializador_modelo import iniciar_modelo, MODELO, TAXA_AMOSTRAGEM
from transcritor import carregar_fala, transcrever
import sounddevice as sd
import soundfile as sf
import torch
import secrets
import json
import os
import importlib
import unicodedata

# ─── Configurações ──────────────────────────────────────────────────────────────
CONFIGURACAO = "config.json"
LINGUAGEM = "portuguese"
TEMPO_GRAVACAO = 5
CAMINHO_AUDIO_FALAS = "temp"

# Tokens de voz que encerram o assistente
TOKENS_ENCERRAMENTO = {"encerrar", "sair", "finalizar", "parar", "desligar"}


# ─── Utilitários ─────────────────────────────────────────────────────────────────

def remover_acentos(texto):
    """Remove acentos de uma string para facilitar comparações fonéticas."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


# ─── Inicialização ───────────────────────────────────────────────────────────────

def iniciar_assistente(dispositivo):
    """
    Inicializa o modelo de reconhecimento de fala, carrega configurações
    e inicializa todos os módulos atuadores.
    """
    print("=" * 60)
    print("   PalcoBot - Assistente de Automação de Palcos e Eventos")
    print("=" * 60)

    print(f"\n[INIT] Carregando modelo de transcrição ({MODELO})...")
    iniciado, processador, modelo = iniciar_modelo(MODELO, dispositivo)
    if not iniciado:
        return False, None, None, None, None, None

    print("[INIT] Modelo carregado com sucesso!")

    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))

    with open(CONFIGURACAO, "r", encoding="utf-8") as arquivo_configuracao:
        configuracoes = json.load(arquivo_configuracao)
        acoes = configuracoes["acoes"]
        sinonimos = configuracoes.get("sinonimos", {})
        arquivo_configuracao.close()

    print(f"[INIT] Configuração carregada: {len(acoes)} ações configuradas.")

    modulos_carregados = set()
    for acao in acoes:
        nome_modulo = acao.get("modulo")
        if nome_modulo and nome_modulo not in modulos_carregados:
            try:
                modulo = importlib.import_module(nome_modulo)
                modulo.iniciar()
                modulos_carregados.add(nome_modulo)
            except Exception as e:
                print(f"[INIT] Aviso: não foi possível iniciar módulo '{nome_modulo}': {e}")

    print("\n[INIT] PalcoBot pronto para receber comandos!\n")
    return iniciado, processador, modelo, palavras_de_parada, acoes, sinonimos


# ─── Captura e gravação de áudio ─────────────────────────────────────────────────

def capturar_fala():
    """Captura áudio do microfone pelo tempo configurado."""
    print(f"\n[MIC] Fale o comando agora ({TEMPO_GRAVACAO}s)...")
    fala = sd.rec(
        int(TEMPO_GRAVACAO * TAXA_AMOSTRAGEM),
        samplerate=TAXA_AMOSTRAGEM,
        channels=1
    )
    sd.wait()
    print("[MIC] Fala capturada!")
    return fala


def gravar_fala(fala):
    """Salva o áudio capturado em arquivo temporário."""
    gravado = False
    arquivo = f"{CAMINHO_AUDIO_FALAS}/{secrets.token_hex(32).lower()}.wav"

    try:
        os.makedirs(CAMINHO_AUDIO_FALAS, exist_ok=True)
        sf.write(arquivo, fala, TAXA_AMOSTRAGEM)
        gravado = True
    except Exception as e:
        print(f"[ERRO] Erro gravando áudio: {e}")

    return gravado, arquivo


# ─── Processamento de linguagem natural ──────────────────────────────────────────

def processar_transcricao(transcricao, palavras_de_parada):
    """
    Tokeniza a transcrição e remove stopwords para extrair
    apenas os tokens relevantes do comando.
    """
    tokens = word_tokenize(transcricao, language=LINGUAGEM)
    comando = [token for token in tokens if token not in palavras_de_parada]
    return comando


def normalizar_token(token, sinonimos):
    """
    Normaliza um token para sua forma canônica usando o mapeamento
    de sinônimos definido no arquivo de configuração JSON.
    Tenta também a versão sem acentos do token.
    """
    token_sem_acento = remover_acentos(token)
    for forma_canonica, variantes in sinonimos.items():
        variantes_sem_acento = [remover_acentos(v) for v in variantes]
        if token in variantes or token_sem_acento in variantes_sem_acento:
            return forma_canonica
    return token


def validar_comando(comando, acoes, sinonimos):
    """
    Valida se os tokens do comando correspondem a uma ação configurada.

    Estratégias de correspondência (em ordem de prioridade):
      1. Exata após normalização de sinônimos e remoção de acentos.
      2. Prefixo de 4+ caracteres (lida com erros fonéticos do ASR).
      3. Substring bidirecional — cobre casos como "tela" ↔ "telão",
         "emergenci" ↔ "emergência".
    """
    valido = False
    acao_encontrada = None
    objeto_encontrado = None

    tokens_normalizados = [normalizar_token(t, sinonimos) for t in comando]
    todos_tokens = set(tokens_normalizados) | set(comando)
    # Versões sem acento de todos os tokens
    todos_tokens_sa = {remover_acentos(t) for t in todos_tokens}

    def token_bate_dispositivo(dispositivo):
        disp_sa = remover_acentos(dispositivo)
        for tok in todos_tokens:
            tok_sa = remover_acentos(tok)
            # 1. Exata (com ou sem acento)
            if tok == dispositivo or tok_sa == disp_sa:
                return True
            # 2. Prefixo de 4+ caracteres
            if len(disp_sa) >= 4 and len(tok_sa) >= 4:
                if tok_sa.startswith(disp_sa[:4]) or disp_sa.startswith(tok_sa[:4]):
                    return True
            # 3. Substring bidirecional
            if len(tok_sa) >= 3 and len(disp_sa) >= 3:
                if tok_sa in disp_sa or disp_sa in tok_sa:
                    return True
        return False

    for acao_configurada in acoes:
        nome_acao = acao_configurada["nome"]
        dispositivos = acao_configurada["dispositivos"]

        if nome_acao in tokens_normalizados:
            for dispositivo in dispositivos:
                if token_bate_dispositivo(dispositivo):
                    valido = True
                    acao_encontrada = nome_acao
                    objeto_encontrado = dispositivo
                    break

        if valido:
            break

    return valido, acao_encontrada, objeto_encontrado


def verificar_encerramento_por_voz(transcricao):
    """
    Verifica se a transcrição contém um comando de encerramento do assistente.
    Exemplos: "encerrar assistente", "sair", "finalizar", "parar"
    """
    tokens = set(word_tokenize(transcricao.lower(), language=LINGUAGEM))
    return bool(tokens & TOKENS_ENCERRAMENTO)


# ─── Execução do comando ──────────────────────────────────────────────────────────

def executar_comando(acao, objeto, acoes):
    """
    Despacha a execução do comando para o módulo atuador correto,
    conforme definido no arquivo de configuração JSON.
    """
    modulo_destino = None
    mensagem_config = None

    for acao_configurada in acoes:
        if (acao_configurada["nome"] == acao and
                objeto in acao_configurada["dispositivos"]):
            modulo_destino = acao_configurada.get("modulo")
            mensagem_config = acao_configurada.get("mensagem")
            break

    if mensagem_config:
        print(f"\n[CMD] {mensagem_config}")

    if modulo_destino:
        try:
            modulo = importlib.import_module(modulo_destino)
            modulo.atuar(acao, objeto)
        except Exception as e:
            print(f"[ERRO] Falha ao executar módulo '{modulo_destino}': {e}")
    else:
        print(f"[CMD] Executando: {acao} → {objeto}")


# ─── Loop principal ───────────────────────────────────────────────────────────────

def exibir_ajuda(acoes):
    """Exibe os comandos disponíveis conforme o arquivo de configuração."""
    print("\n┌──────────────────────────────────────────────────────────┐")
    print("│            COMANDOS DISPONÍVEIS - PalcoBot               │")
    print("├──────────────────────────────────────────────────────────┤")
    comandos_exibidos = {}
    for acao in acoes:
        mod = acao.get("modulo", "")
        if mod not in comandos_exibidos:
            comandos_exibidos[mod] = acao["descricao"]
            print(f"│  • {acao['descricao']:<54}│")
    print("├──────────────────────────────────────────────────────────┤")
    print("│  CONTROLES:                                              │")
    print("│  ENTER             → gravar comando de voz              │")
    print("│  E + ENTER         → encerrar pelo teclado              │")
    print("│  Falar 'encerrar'  → encerrar pelo microfone            │")
    print("└──────────────────────────────────────────────────────────┘\n")


if __name__ == "__main__":
    import nltk
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    nltk.download("stopwords", quiet=True)

    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"[SISTEMA] Dispositivo de inferência: {dispositivo}")

    iniciado, processador, modelo, palavras_de_parada, acoes, sinonimos = iniciar_assistente(dispositivo)

    if not iniciado:
        print("[ERRO] Não foi possível iniciar o PalcoBot.")
        exit(1)

    exibir_ajuda(acoes)

    while True:
        print("\n" + "─" * 60)
        print("  ENTER = gravar comando  |  E + ENTER = encerrar")
        entrada = input("→ ").strip().lower()

        # Encerramento pelo teclado
        if entrada == "e":
            print("\n[SISTEMA] PalcoBot encerrado pelo teclado. Até logo!")
            break

        # Apenas ENTER → inicia gravação
        fala_bruta = capturar_fala()
        gravado, arquivo = gravar_fala(fala_bruta)

        if not gravado:
            print("[ERRO] Não foi possível salvar o áudio.")
            continue

        print("[NLP] Realizando transcrição...")
        fala_tensor = carregar_fala(arquivo)
        transcricao = transcrever(dispositivo, fala_tensor, modelo, processador)
        print(f"[NLP] Transcrição: \"{transcricao}\"")

        # Encerramento por voz
        if verificar_encerramento_por_voz(transcricao):
            print("\n[SISTEMA] Comando de encerramento reconhecido. PalcoBot encerrado!")
            break

        # Processamento e validação do comando
        comando = processar_transcricao(transcricao, palavras_de_parada)
        print(f"[NLP] Tokens do comando: {comando}")

        valido, acao, objeto = validar_comando(comando, acoes, sinonimos)

        if valido:
            executar_comando(acao, objeto, acoes)
        else:
            print("[CMD] ✘  Comando não reconhecido. Verifique os comandos disponíveis.")
            print(f"[DBG] Tokens recebidos: {comando}")
            exibir_ajuda(acoes)



# ─── Inicialização ───────────────────────────────────────────────────────────────

def iniciar_assistente(dispositivo):
    """
    Inicializa o modelo de reconhecimento de fala, carrega configurações
    e inicializa todos os módulos atuadores.
    """
    print("=" * 60)
    print("   PalcoBot - Assistente de Automação de Palcos e Eventos")
    print("=" * 60)

    # Carrega modelo de reconhecimento de fala
    print(f"\n[INIT] Carregando modelo de transcrição ({MODELO})...")
    iniciado, processador, modelo = iniciar_modelo(MODELO, dispositivo)
    if not iniciado:
        return False, None, None, None, None, None

    print("[INIT] Modelo carregado com sucesso!")

    # Carrega stopwords do NLTK
    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))

    # Lê arquivo de configuração externo
    with open(CONFIGURACAO, "r", encoding="utf-8") as arquivo_configuracao:
        configuracoes = json.load(arquivo_configuracao)
        acoes = configuracoes["acoes"]
        sinonimos = configuracoes.get("sinonimos", {})
        arquivo_configuracao.close()

    print(f"[INIT] Configuração carregada: {len(acoes)} ações configuradas.")

    # Inicializa módulos atuadores definidos no config
    modulos_carregados = set()
    for acao in acoes:
        nome_modulo = acao.get("modulo")
        if nome_modulo and nome_modulo not in modulos_carregados:
            try:
                modulo = importlib.import_module(nome_modulo)
                modulo.iniciar()
                modulos_carregados.add(nome_modulo)
            except Exception as e:
                print(f"[INIT] Aviso: não foi possível iniciar módulo '{nome_modulo}': {e}")

    print("\n[INIT] PalcoBot pronto para receber comandos!\n")
    return iniciado, processador, modelo, palavras_de_parada, acoes, sinonimos


# ─── Captura e gravação de áudio ─────────────────────────────────────────────────

def capturar_fala():
    """Captura áudio do microfone pelo tempo configurado."""
    print(f"\n[MIC] Fale o comando agora ({TEMPO_GRAVACAO}s)...")
    fala = sd.rec(
        int(TEMPO_GRAVACAO * TAXA_AMOSTRAGEM),
        samplerate=TAXA_AMOSTRAGEM,
        channels=1
    )
    sd.wait()
    print("[MIC] Fala capturada!")
    return fala


def gravar_fala(fala):
    """Salva o áudio capturado em arquivo temporário."""
    gravado = False
    arquivo = f"{CAMINHO_AUDIO_FALAS}/{secrets.token_hex(32).lower()}.wav"

    try:
        os.makedirs(CAMINHO_AUDIO_FALAS, exist_ok=True)
        sf.write(arquivo, fala, TAXA_AMOSTRAGEM)
        gravado = True
    except Exception as e:
        print(f"[ERRO] Erro gravando áudio: {e}")

    return gravado, arquivo


# ─── Processamento de linguagem natural ──────────────────────────────────────────

def processar_transcricao(transcricao, palavras_de_parada):
    """
    Tokeniza a transcrição e remove stopwords para extrair
    apenas os tokens relevantes do comando.
    """
    tokens = word_tokenize(transcricao, language=LINGUAGEM)
    comando = [token for token in tokens if token not in palavras_de_parada]
    return comando


def normalizar_token(token, sinonimos):
    """
    Normaliza um token para sua forma canônica usando o mapeamento
    de sinônimos definido no arquivo de configuração JSON.
    """
    for forma_canonica, variantes in sinonimos.items():
        if token in variantes:
            return forma_canonica
    return token


def validar_comando(comando, acoes, sinonimos):
    """
    Valida se os tokens do comando correspondem a uma ação configurada.

    Estratégia em duas passagens:
      1. Correspondência exata (após normalização de sinônimos).
      2. Correspondência parcial por prefixo — lida com erros fonéticos do
         modelo ASR (ex: "tela" reconhecida como "telom", "emergência" como
         "emergenci").
    """
    valido = False
    acao_encontrada = None
    objeto_encontrado = None

    # Normaliza todos os tokens usando sinônimos
    tokens_normalizados = [normalizar_token(t, sinonimos) for t in comando]
    todos_tokens = set(tokens_normalizados) | set(comando)

    def token_bate_dispositivo(dispositivo):
        """Verifica correspondência exata ou por prefixo (min 4 chars)."""
        for tok in todos_tokens:
            if tok == dispositivo:
                return True
            # Correspondência por prefixo: útil para erros fonéticos do ASR
            prefixo = dispositivo[:4] if len(dispositivo) >= 4 else dispositivo
            if len(prefixo) >= 4 and (tok.startswith(prefixo) or dispositivo.startswith(tok[:4])):
                return True
        return False

    for acao_configurada in acoes:
        nome_acao = acao_configurada["nome"]
        dispositivos = acao_configurada["dispositivos"]

        if nome_acao in tokens_normalizados:
            for dispositivo in dispositivos:
                if token_bate_dispositivo(dispositivo):
                    valido = True
                    acao_encontrada = nome_acao
                    objeto_encontrado = dispositivo
                    break

        if valido:
            break

    return valido, acao_encontrada, objeto_encontrado


# ─── Execução do comando ──────────────────────────────────────────────────────────

def executar_comando(acao, objeto, acoes):
    """
    Despacha a execução do comando para o módulo atuador correto,
    conforme definido no arquivo de configuração JSON.
    """
    modulo_destino = None
    mensagem_config = None

    for acao_configurada in acoes:
        if (acao_configurada["nome"] == acao and
                objeto in acao_configurada["dispositivos"]):
            modulo_destino = acao_configurada.get("modulo")
            mensagem_config = acao_configurada.get("mensagem")
            break

    if mensagem_config:
        print(f"\n[CMD] {mensagem_config}")

    if modulo_destino:
        try:
            modulo = importlib.import_module(modulo_destino)
            modulo.atuar(acao, objeto)
        except Exception as e:
            print(f"[ERRO] Falha ao executar módulo '{modulo_destino}': {e}")
    else:
        print(f"[CMD] Executando: {acao} → {objeto}")


# ─── Loop principal ───────────────────────────────────────────────────────────────

def exibir_ajuda(acoes):
    """Exibe os comandos disponíveis conforme o arquivo de configuração."""
    print("\n┌─────────────────────────────────────────────────────┐")
    print("│           COMANDOS DISPONÍVEIS - PalcoBot           │")
    print("├─────────────────────────────────────────────────────┤")
    for acao in acoes:
        dispositivos_str = ", ".join(acao["dispositivos"])
        print(f"│  {acao['nome']:12} {dispositivos_str:20} │")
    print("└─────────────────────────────────────────────────────┘\n")


if __name__ == "__main__":
    import nltk
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    nltk.download("stopwords", quiet=True)

    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"[SISTEMA] Dispositivo de inferência: {dispositivo}")

    iniciado, processador, modelo, palavras_de_parada, acoes, sinonimos = iniciar_assistente(dispositivo)

    if not iniciado:
        print("[ERRO] Não foi possível iniciar o PalcoBot.")
        exit(1)

    exibir_ajuda(acoes)

    while True:
        print("\n" + "─" * 60)
        entrada = input("Pressione ENTER para falar um comando (ou 'sair' para encerrar): ").strip().lower()

        if entrada == "sair":
            print("\n[SISTEMA] PalcoBot encerrado. Até logo!")
            break

        # Captura e transcreve a fala
        fala_bruta = capturar_fala()
        gravado, arquivo = gravar_fala(fala_bruta)

        if not gravado:
            print("[ERRO] Não foi possível salvar o áudio.")
            continue

        print("[NLP] Realizando transcrição...")
        fala_tensor = carregar_fala(arquivo)
        transcricao = transcrever(dispositivo, fala_tensor, modelo, processador)
        print(f"[NLP] Transcrição: \"{transcricao}\"")

        # Processamento e validação
        comando = processar_transcricao(transcricao, palavras_de_parada)
        print(f"[NLP] Tokens do comando: {comando}")

        valido, acao, objeto = validar_comando(comando, acoes, sinonimos)

        if valido:
            executar_comando(acao, objeto, acoes)
        else:
            print("[CMD] ✘  Comando não reconhecido. Verifique os comandos disponíveis.")
            exibir_ajuda(acoes)
