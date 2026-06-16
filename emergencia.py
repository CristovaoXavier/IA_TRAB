"""
Módulo Atuador: Protocolo de Iluminação de Emergência
Simula o acionamento do protocolo de segurança e iluminação de emergência
do ambiente de eventos.
"""

import time

# Estado interno do protocolo de emergência (simulação)
_estado = {"emergencia": "inativa"}


def iniciar():
    """Inicializa o módulo de protocolo de emergência."""
    _estado["emergencia"] = "inativa"
    print("[EMERGÊNCIA] Módulo de protocolo de iluminação de emergência inicializado.")
    print(f"[EMERGÊNCIA] Estado inicial: {_estado['emergencia']}")


def atuar(acao, objeto, local=None):
    """
    Executa o acionamento do protocolo de iluminação de emergência.
    
    Args:
        acao (str): 'acionar'
        objeto (str): 'emergência', 'emergencia' ou 'protocolo'
        local (str, optional): Localização (não utilizado)
    """
    if acao == "acionar":
        _estado["emergencia"] = "ativa"
        print("")
        print("[EMERGÊNCIA] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("[EMERGÊNCIA]  PROTOCOLO DE ILUMINAÇÃO DE EMERGÊNCIA ATIVO ")
        print("[EMERGÊNCIA] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("[EMERGÊNCIA]    → Iluminação de emergência LIGADA (100%)")
        print("[EMERGÊNCIA]    → Luzes de saída ATIVADAS")
        print("[EMERGÊNCIA]    → Holofotes de corredor LIGADOS")
        print("[EMERGÊNCIA]    → Efeitos cênicos DESATIVADOS")
        print("[EMERGÊNCIA]    → Sinalizações de evacuação ATIVAS")
        print("[EMERGÊNCIA]    → Notificando equipe de segurança...")
        print("[EMERGÊNCIA]    → Estado atual: EMERGÊNCIA ATIVA")
        print("")
    else:
        print(f"[EMERGÊNCIA] ✘  Ação '{acao}' não reconhecida para emergência.")


def obter_estado():
    return _estado["emergencia"]
