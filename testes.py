"""
PalcoBot - Testes Automatizados com UNITTEST
IFBA - Disciplina de Inteligência Artificial

Suite de testes que valida todos os comandos do assistente:
    1. abrir/fechar cortinas
    2. ativar/desativar fumaça
    3. descer/subir telão
    4. acionar emergência

Os testes incluem:
    - Validação da estrutura do arquivo de configuração JSON
    - Testes de NLP (tokenização e remoção de stopwords)
    - Testes de validação de comandos com o config real
    - Testes dos módulos atuadores (via captura de stdout)
    - Testes de transcrição usando os arquivos WAV pré-gravados

Uso:
    python -m unittest testes.py -v
"""

import unittest
import json
import os
import sys
import io
from unittest.mock import patch, MagicMock

# Garante que o diretório do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nltk
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

from nltk import corpus
from assistente import (
    processar_transcricao,
    validar_comando,
    normalizar_token,
    executar_comando,
    verificar_encerramento_por_voz,
)

CONFIGURACAO = "config.json"
PASTA_AUDIOS = "audios"

# Carrega configuração para uso nos testes
with open(CONFIGURACAO, "r", encoding="utf-8") as f:
    _CONFIG = json.load(f)
    _ACOES = _CONFIG["acoes"]
    _SINONIMOS = _CONFIG.get("sinonimos", {})


# ─── Testes de Configuração ───────────────────────────────────────────────────────

class TestConfiguracao(unittest.TestCase):
    """Verifica a estrutura e integridade do arquivo config.json."""

    def test_arquivo_config_existe(self):
        """O arquivo de configuração JSON deve existir."""
        self.assertTrue(os.path.exists(CONFIGURACAO), "config.json não encontrado")

    def test_config_tem_chave_acoes(self):
        """O JSON deve conter a chave 'acoes'."""
        self.assertIn("acoes", _CONFIG)

    def test_config_tem_minimo_4_acoes_unicas(self):
        """Deve haver pelo menos 4 ações distintas configuradas."""
        nomes = {a["nome"] for a in _ACOES}
        self.assertGreaterEqual(len(nomes), 4,
                                "Devem existir pelo menos 4 ações distintas no config.json")

    def test_todas_acoes_tem_campos_obrigatorios(self):
        """Cada ação deve ter nome, dispositivos, modulo e mensagem."""
        for acao in _ACOES:
            with self.subTest(acao=acao.get("nome")):
                self.assertIn("nome", acao)
                self.assertIn("dispositivos", acao)
                self.assertIn("modulo", acao)
                self.assertIn("mensagem", acao)
                self.assertIsInstance(acao["dispositivos"], list)
                self.assertGreater(len(acao["dispositivos"]), 0)

    def test_acoes_esperadas_presentes(self):
        """As 7 ações do mini-mundo devem estar configuradas."""
        nomes = {a["nome"] for a in _ACOES}
        for esperada in ["abrir", "fechar", "ativar", "desativar", "descer", "subir", "acionar"]:
            with self.subTest(acao=esperada):
                self.assertIn(esperada, nomes,
                              f"Ação '{esperada}' não encontrada em config.json")


# ─── Testes de NLP ────────────────────────────────────────────────────────────────

class TestNLP(unittest.TestCase):
    """Testa o processamento de linguagem natural."""

    def setUp(self):
        self.stopwords = set(corpus.stopwords.words("portuguese"))

    def test_processar_transcricao_remove_stopwords(self):
        """Stopwords devem ser removidas da transcrição."""
        transcricao = "por favor abrir as cortinas do palco"
        tokens = processar_transcricao(transcricao, self.stopwords)
        for sw in self.stopwords:
            self.assertNotIn(sw, tokens)

    def test_processar_transcricao_retorna_lista(self):
        """processar_transcricao deve retornar uma lista."""
        tokens = processar_transcricao("abrir cortinas", self.stopwords)
        self.assertIsInstance(tokens, list)

    def test_processar_transcricao_mantém_palavras_chave(self):
        """Palavras-chave de comando devem permanecer após processamento."""
        transcricao = "abrir cortinas"
        tokens = processar_transcricao(transcricao, self.stopwords)
        self.assertIn("abrir", tokens)
        self.assertIn("cortinas", tokens)

    def test_normalizar_token_com_sinonimo(self):
        """Sinônimos devem ser normalizados para a forma canônica."""
        self.assertEqual(normalizar_token("liga", _SINONIMOS), "ativar")
        self.assertEqual(normalizar_token("desliga", _SINONIMOS), "desativar")

    def test_normalizar_token_sem_sinonimo(self):
        """Tokens sem sinônimo devem retornar o próprio token."""
        self.assertEqual(normalizar_token("xyztoken", _SINONIMOS), "xyztoken")


# ─── Testes de Validação de Comandos ─────────────────────────────────────────────

class TestValidacaoComandos(unittest.TestCase):
    """Testa a validação dos comandos contra as ações configuradas."""

    def _validar(self, texto):
        """Helper: processa um texto e valida como comando."""
        sw = set(corpus.stopwords.words("portuguese"))
        tokens = processar_transcricao(texto, sw)
        return validar_comando(tokens, _ACOES, _SINONIMOS)

    # Cortinas
    def test_comando_abrir_cortinas(self):
        valido, acao, objeto = self._validar("abrir cortinas")
        self.assertTrue(valido)
        self.assertEqual(acao, "abrir")
        self.assertIn(objeto, ["cortina", "cortinas"])

    def test_comando_fechar_cortinas(self):
        valido, acao, objeto = self._validar("fechar cortinas")
        self.assertTrue(valido)
        self.assertEqual(acao, "fechar")

    # Fumaça
    def test_comando_ativar_fumaca(self):
        valido, acao, objeto = self._validar("ativar fumaça")
        self.assertTrue(valido)
        self.assertEqual(acao, "ativar")

    def test_comando_desativar_fumaca(self):
        valido, acao, objeto = self._validar("desativar fumaça")
        self.assertTrue(valido)
        self.assertEqual(acao, "desativar")

    # Telão
    def test_comando_descer_telao(self):
        valido, acao, objeto = self._validar("descer telão")
        self.assertTrue(valido)
        self.assertEqual(acao, "descer")

    def test_comando_abaixar_telao(self):
        valido, acao, objeto = self._validar("abaixar telão")
        self.assertTrue(valido)
        self.assertEqual(acao, "descer")

    def test_comando_subir_telao(self):
        valido, acao, objeto = self._validar("subir telão")
        self.assertTrue(valido)
        self.assertEqual(acao, "subir")

    # Emergência
    def test_comando_acionar_emergencia(self):
        valido, acao, objeto = self._validar("acionar emergência")
        self.assertTrue(valido)
        self.assertEqual(acao, "acionar")

    # Comandos inválidos
    def test_comando_invalido_retorna_falso(self):
        valido, _, __ = self._validar("bom dia assistente")
        self.assertFalse(valido)

    def test_comando_vazio_retorna_falso(self):
        valido, _, __ = validar_comando([], _ACOES, _SINONIMOS)
        self.assertFalse(valido)


# ─── Testes dos Atuadores ─────────────────────────────────────────────────────────

class TestAtuadores(unittest.TestCase):
    """Testa os módulos atuadores verificando saída no terminal."""

    def _capturar_saida(self, modulo_nome, acao, objeto):
        """Captura stdout ao chamar modulo.atuar(acao, objeto)."""
        import importlib
        modulo = importlib.import_module(modulo_nome)
        capturado = io.StringIO()
        with patch("sys.stdout", capturado):
            modulo.atuar(acao, objeto)
        return capturado.getvalue()

    def test_atuador_abrir_cortinas(self):
        import cortinas
        cortinas._estado["cortinas"] = "fechadas"
        saida = self._capturar_saida("cortinas", "abrir", "cortinas")
        self.assertIn("ABERTAS", saida.upper())

    def test_atuador_fechar_cortinas(self):
        import cortinas
        cortinas._estado["cortinas"] = "abertas"
        saida = self._capturar_saida("cortinas", "fechar", "cortinas")
        self.assertIn("FECHADAS", saida.upper())

    def test_atuador_ativar_fumaca(self):
        import maquina_fumaca
        maquina_fumaca._estado["maquina_fumaca"] = "desativada"
        saida = self._capturar_saida("maquina_fumaca", "ativar", "fumaça")
        self.assertIn("ATIVADA", saida.upper())

    def test_atuador_desativar_fumaca(self):
        import maquina_fumaca
        maquina_fumaca._estado["maquina_fumaca"] = "ativada"
        saida = self._capturar_saida("maquina_fumaca", "desativar", "fumaça")
        self.assertIn("DESATIVADA", saida.upper())

    def test_atuador_descer_telao(self):
        import telao
        telao._estado["telao"] = "subido"
        saida = self._capturar_saida("telao", "descer", "telão")
        self.assertIn("DESCIDO", saida.upper())

    def test_atuador_subir_telao(self):
        import telao
        telao._estado["telao"] = "descido"
        saida = self._capturar_saida("telao", "subir", "telão")
        self.assertIn("SUBIDO", saida.upper())

    def test_atuador_acionar_emergencia(self):
        import emergencia
        saida = self._capturar_saida("emergencia", "acionar", "emergência")
        self.assertIn("EMERG", saida.upper())

    def test_atuador_acao_invalida_nao_lanca_excecao(self):
        """Ações inválidas não devem lançar exceção, apenas imprimir aviso."""
        try:
            self._capturar_saida("cortinas", "explodir", "cortinas")
        except Exception as e:
            self.fail(f"atuador lançou exceção inesperada: {e}")


# ─── Testes de Transcrição (com arquivos WAV pré-gravados) ───────────────────────

class TestTranscricao(unittest.TestCase):
    """
    Testa o pipeline completo de transcrição usando arquivos de áudio
    pré-gravados na pasta audios/.

    Requer que o script gerar_audios_teste.py tenha sido executado antes.
    O modelo Wav2Vec2 é inicializado uma única vez para toda a classe.
    """

    _modelo = None
    _processador = None
    _dispositivo = None
    _iniciado = False

    @classmethod
    def setUpClass(cls):
        """Inicializa o modelo uma única vez para todos os testes de transcrição."""
        import torch
        from inicializador_modelo import iniciar_modelo, MODELO

        cls._dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
        cls._iniciado, cls._processador, cls._modelo = iniciar_modelo(
            MODELO, cls._dispositivo
        )
        if not cls._iniciado:
            print("\n[AVISO] Modelo não pôde ser iniciado. Testes de transcrição serão ignorados.")

    def _transcrever_arquivo(self, nome_arquivo):
        """Helper: carrega e transcreve um arquivo WAV."""
        import torchaudio
        from transcritor import transcrever, carregar_fala

        caminho = os.path.join(PASTA_AUDIOS, nome_arquivo)
        if not os.path.exists(caminho):
            self.skipTest(f"Arquivo de áudio não encontrado: {caminho}. Execute gerar_audios_teste.py")

        fala = carregar_fala(caminho)
        return transcrever(self._dispositivo, fala, self._modelo, self._processador)

    def _pipeline_completo(self, nome_arquivo):
        """
        Executa o pipeline completo: transcrição → NLP → validação.
        Retorna (valido, acao, objeto).
        """
        if not self._iniciado:
            self.skipTest("Modelo não iniciado")

        transcricao = self._transcrever_arquivo(nome_arquivo)
        sw = set(corpus.stopwords.words("portuguese"))
        tokens = processar_transcricao(transcricao, sw)
        return validar_comando(tokens, _ACOES, _SINONIMOS)

    def test_transcricao_abrir_cortinas(self):
        if not self._iniciado:
            self.skipTest("Modelo não iniciado")
        valido, acao, _ = self._pipeline_completo("abrir_cortinas.wav")
        self.assertTrue(valido, "Comando 'abrir cortinas' não reconhecido")
        self.assertEqual(acao, "abrir")

    def test_transcricao_fechar_cortinas(self):
        if not self._iniciado:
            self.skipTest("Modelo não iniciado")
        valido, acao, _ = self._pipeline_completo("fechar_cortinas.wav")
        self.assertTrue(valido, "Comando 'fechar cortinas' não reconhecido")
        self.assertEqual(acao, "fechar")

    def test_transcricao_ativar_fumaca(self):
        if not self._iniciado:
            self.skipTest("Modelo não iniciado")
        valido, acao, _ = self._pipeline_completo("ativar_fumaca.wav")
        self.assertTrue(valido, "Comando 'ativar fumaça' não reconhecido")
        self.assertEqual(acao, "ativar")

    def test_transcricao_desativar_fumaca(self):
        if not self._iniciado:
            self.skipTest("Modelo não iniciado")
        valido, acao, _ = self._pipeline_completo("desativar_fumaca.wav")
        self.assertTrue(valido, "Comando 'desativar fumaça' não reconhecido")
        self.assertEqual(acao, "desativar")

    def test_transcricao_descer_telao(self):
        if not self._iniciado:
            self.skipTest("Modelo não iniciado")
        transcricao = self._transcrever_arquivo("descer_telao.wav")
        sw = set(corpus.stopwords.words("portuguese"))
        tokens = processar_transcricao(transcricao, sw)
        valido, acao, _ = validar_comando(tokens, _ACOES, _SINONIMOS)
        self.assertTrue(valido,
            f"Comando 'descer telão' não reconhecido. "
            f"Transcrição obtida: '{transcricao}' | Tokens: {tokens}")
        self.assertEqual(acao, "descer")

    def test_transcricao_abaixar_telao(self):
        if not self._iniciado:
            self.skipTest("Modelo não iniciado")
        transcricao = self._transcrever_arquivo("abaixar_telao.wav")
        sw = set(corpus.stopwords.words("portuguese"))
        tokens = processar_transcricao(transcricao, sw)
        valido, acao, _ = validar_comando(tokens, _ACOES, _SINONIMOS)
        self.assertTrue(valido,
            f"Comando 'abaixar telão' não reconhecido. "
            f"Transcrição obtida: '{transcricao}' | Tokens: {tokens}")
        self.assertEqual(acao, "descer")

    def test_transcricao_subir_telao(self):
        if not self._iniciado:
            self.skipTest("Modelo não iniciado")
        valido, acao, _ = self._pipeline_completo("subir_telao.wav")
        self.assertTrue(valido, "Comando 'subir telão' não reconhecido")
        self.assertEqual(acao, "subir")

    def test_transcricao_acionar_emergencia(self):
        if not self._iniciado:
            self.skipTest("Modelo não iniciado")
        valido, acao, _ = self._pipeline_completo("acionar_emergencia.wav")
        self.assertTrue(valido, "Comando 'acionar emergência' não reconhecido")
        self.assertEqual(acao, "acionar")


# ─── Testes de Encerramento por Voz ──────────────────────────────────────────────

class TestEncerramentoPorVoz(unittest.TestCase):
    """Testa o reconhecimento do comando de encerramento falado."""

    def test_encerrar_reconhecido(self):
        self.assertTrue(verificar_encerramento_por_voz("encerrar assistente"))

    def test_sair_reconhecido(self):
        self.assertTrue(verificar_encerramento_por_voz("sair"))

    def test_finalizar_reconhecido(self):
        self.assertTrue(verificar_encerramento_por_voz("finalizar sistema"))

    def test_comando_normal_nao_encerra(self):
        self.assertFalse(verificar_encerramento_por_voz("abrir cortinas"))

    def test_transcricao_vazia_nao_encerra(self):
        self.assertFalse(verificar_encerramento_por_voz(""))


if __name__ == '__main__':
    unittest.main(verbosity=2)
