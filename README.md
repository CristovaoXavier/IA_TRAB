# PalcoBot — Assistente Virtual para Automação de Palcos e Eventos

**Disciplina:** Inteligência Artificial — IFBA  
**Professor:** Luis Paulo da Silva Carvalho  

---

## 📋 Descrição do Mini-Mundo

O **PalcoBot** é um assistente virtual com reconhecimento de voz voltado para
a automação de dispositivos cênicos e de segurança em ambientes de eventos.
O operador de palco pode controlar os equipamentos falando comandos naturais
em português brasileiro, sem necessidade de interação manual.

---

## 🎭 Comandos Disponíveis

| Comando de Voz           | Ação Simulada                                   |
|--------------------------|-------------------------------------------------|
| "abrir cortinas"         | Abre as cortinas principais do palco            |
| "fechar cortinas"        | Fecha as cortinas principais do palco           |
| "ativar fumaça"          | Liga a máquina de fumaça cênica                 |
| "desativar fumaça"       | Desliga a máquina de fumaça cênica              |
| "descer telão"           | Desce o telão central do palco                  |
| "subir telão"            | Sobe o telão central do palco                   |
| "acionar emergência"     | Aciona o protocolo de iluminação de emergência  |

---

## 🗂 Estrutura do Projeto

```
assistente_palco/
├── assistente.py          # Script principal do assistente
├── inicializador_modelo.py # Carregamento do modelo Wav2Vec2
├── transcritor.py         # Transcrição de áudio para texto
├── cortinas.py            # Atuador: cortinas principais
├── maquina_fumaca.py      # Atuador: máquina de fumaça
├── telao.py               # Atuador: telão central
├── emergencia.py          # Atuador: protocolo de emergência
├── config.json            # Configuração externa dos comandos (JSON)
├── testes.py              # Testes automatizados (unittest)
├── gerar_audios_teste.py  # Gerador de áudios para os testes
├── requirements.txt       # Dependências do projeto
├── audios/                # Áudios pré-gravados para testes
└── temp/                  # Áudios temporários capturados pelo microfone
```

---

## ⚙️ Instalação

```bash
pip install -r requirements.txt
```

---

## ▶️ Como Executar o Assistente

```bash
python assistente.py
```

O assistente irá:
1. Carregar o modelo de reconhecimento de fala (Wav2Vec2)
2. Exibir os comandos disponíveis
3. Aguardar ENTER para iniciar a captura de voz (5 segundos)
4. Transcrever e executar o comando reconhecido

---

## 🧪 Como Executar os Testes

**Passo 1:** Gerar os arquivos de áudio de teste (execute apenas uma vez):
```bash
python gerar_audios_teste.py
```

**Passo 2:** Rodar a suite de testes:
```bash
python -m unittest testes.py -v
```

Os testes cobrem:
- ✅ Estrutura e integridade do `config.json`
- ✅ Processamento de linguagem natural (NLP)
- ✅ Validação de todos os 7 comandos
- ✅ Funcionamento de todos os atuadores
- ✅ Pipeline completo com arquivos WAV pré-gravados

---

## 🔧 Modelo de Reconhecimento de Fala

- **Modelo:** `lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2`
- **Fonte:** [Hugging Face](https://huggingface.co/lgris/wav2vec2-large-xlsr-open-brazilian-portuguese-v2)
- **Biblioteca:** `transformers` (Hugging Face)
- **NLP:** `nltk` (tokenização e remoção de stopwords)

---

## ⚠️ Observações

- O assistente **não usa** a biblioteca `SpeechRecognition`.
- Todos os comandos são lidos do arquivo `config.json` externo.
- As atuações são **simuladas** via impressão de mensagens no terminal.
- O sistema é composto de **sensor** (microfone via `sounddevice`) e **atuadores** (módulos Python).
