"""
Módulo Atuador: Máquina de Fumaça
Simula o controle da máquina de fumaça cênica do palco de eventos.
"""

# Estado interno da máquina de fumaça (simulação)
_estado = {"maquina_fumaca": "desativada"}


def iniciar():
    """Inicializa o módulo de controle da máquina de fumaça."""
    _estado["maquina_fumaca"] = "desativada"
    print("[FUMAÇA] Módulo de controle da máquina de fumaça inicializado.")
    print(f"[FUMAÇA] Estado inicial: {_estado['maquina_fumaca']}")


def atuar(acao, objeto, local=None):
    """
    Executa a ação sobre a máquina de fumaça.
    
    Args:
        acao (str): 'ativar' ou 'desativar'
        objeto (str): 'fumaça', 'fumaca' ou 'maquina'
        local (str, optional): Localização (não utilizado)
    """
    if acao == "ativar":
        if _estado["maquina_fumaca"] == "ativada":
            print("[FUMAÇA] ⚠  A máquina de fumaça já está ativada.")
        else:
            _estado["maquina_fumaca"] = "ativada"
            print("[FUMAÇA] ✔  Máquina de fumaça sendo ATIVADA...")
            print("[FUMAÇA]    → Resistência de aquecimento ligada")
            print("[FUMAÇA]    → Aguardando temperatura de operação (45°C)")
            print("[FUMAÇA]    → Bomba de fluido acionada")
            print(f"[FUMAÇA]    → Estado atual: {_estado['maquina_fumaca']}")

    elif acao == "desativar":
        if _estado["maquina_fumaca"] == "desativada":
            print("[FUMAÇA] ⚠  A máquina de fumaça já está desativada.")
        else:
            _estado["maquina_fumaca"] = "desativada"
            print("[FUMAÇA] ✔  Máquina de fumaça sendo DESATIVADA...")
            print("[FUMAÇA]    → Bomba de fluido desligada")
            print("[FUMAÇA]    → Resistência de aquecimento desligada")
            print("[FUMAÇA]    → Iniciando resfriamento do equipamento")
            print(f"[FUMAÇA]    → Estado atual: {_estado['maquina_fumaca']}")
    else:
        print(f"[FUMAÇA] ✘  Ação '{acao}' não reconhecida para máquina de fumaça.")


def obter_estado():
    return _estado["maquina_fumaca"]
