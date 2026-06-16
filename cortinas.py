"""
Módulo Atuador: Cortinas Principais do Palco
Simula o controle das cortinas principais do palco de eventos.
"""

# Estado interno das cortinas (simulação)
_estado = {"cortinas": "fechadas"}


def iniciar():
    """Inicializa o módulo de controle das cortinas."""
    _estado["cortinas"] = "fechadas"
    print("[CORTINAS] Módulo de controle das cortinas principais inicializado.")
    print(f"[CORTINAS] Estado inicial: {_estado['cortinas']}")


def atuar(acao, objeto, local=None):
    """
    Executa a ação sobre as cortinas.
    
    Args:
        acao (str): 'abrir' ou 'fechar'
        objeto (str): 'cortina' ou 'cortinas'
        local (str, optional): Localização (não utilizado para cortinas)
    """
    if acao == "abrir":
        if _estado["cortinas"] == "abertas":
            print("[CORTINAS] ⚠  As cortinas já estão abertas.")
        else:
            _estado["cortinas"] = "abertas"
            print("[CORTINAS] ✔  Cortinas principais sendo ABERTAS...")
            print("[CORTINAS]    → Motor de abertura acionado")
            print("[CORTINAS]    → Posição: 0% → 100%")
            print(f"[CORTINAS]    → Estado atual: {_estado['cortinas']}")

    elif acao == "fechar":
        if _estado["cortinas"] == "fechadas":
            print("[CORTINAS] ⚠  As cortinas já estão fechadas.")
        else:
            _estado["cortinas"] = "fechadas"
            print("[CORTINAS] ✔  Cortinas principais sendo FECHADAS...")
            print("[CORTINAS]    → Motor de fechamento acionado")
            print("[CORTINAS]    → Posição: 100% → 0%")
            print(f"[CORTINAS]    → Estado atual: {_estado['cortinas']}")
    else:
        print(f"[CORTINAS] ✘  Ação '{acao}' não reconhecida para cortinas.")


def obter_estado():
    return _estado["cortinas"]
