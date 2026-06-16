"""
Módulo Atuador: Telão Central
Simula o controle da descida e subida do telão central do palco de eventos.
"""

# Estado interno do telão (simulação)
_estado = {"telao": "subido"}


def iniciar():
    """Inicializa o módulo de controle do telão central."""
    _estado["telao"] = "subido"
    print("[TELÃO] Módulo de controle do telão central inicializado.")
    print(f"[TELÃO] Estado inicial: {_estado['telao']}")


def atuar(acao, objeto, local=None):
    """
    Executa a ação sobre o telão central.
    
    Args:
        acao (str): 'descer' ou 'subir'
        objeto (str): 'telão', 'telao' ou 'tela'
        local (str, optional): Localização (não utilizado)
    """
    if acao == "descer":
        if _estado["telao"] == "descido":
            print("[TELÃO] ⚠  O telão já está na posição baixa.")
        else:
            _estado["telao"] = "descido"
            print("[TELÃO] ✔  Telão central sendo DESCIDO...")
            print("[TELÃO]    → Motor de descida acionado")
            print("[TELÃO]    → Velocidade: 0.5 m/s")
            print("[TELÃO]    → Posição estimada: 0% → 100%")
            print(f"[TELÃO]    → Estado atual: {_estado['telao']}")

    elif acao == "subir":
        if _estado["telao"] == "subido":
            print("[TELÃO] ⚠  O telão já está na posição alta.")
        else:
            _estado["telao"] = "subido"
            print("[TELÃO] ✔  Telão central sendo SUBIDO...")
            print("[TELÃO]    → Motor de subida acionado")
            print("[TELÃO]    → Velocidade: 0.5 m/s")
            print("[TELÃO]    → Posição estimada: 100% → 0%")
            print(f"[TELÃO]    → Estado atual: {_estado['telao']}")
    else:
        print(f"[TELÃO] ✘  Ação '{acao}' não reconhecida para o telão.")


def obter_estado():
    return _estado["telao"]
