# Esta clase es para definir las reglas de negocio
from src.state import AgentState

UMBRAL = 3000


#TODO 
def importe_superado (agent: AgentState):
    umbral_siniestro = agent.tool_results["importe_estimado"] 
    if umbral_siniestro > UMBRAL: 
        agent.interrupt_reason(f"importe de umbral para el siniestro superado: {umbral_siniestro} euros")
        return True
    else:
        return False

#Por consultar con Javi, en teoria estos dos casos  
def es_queja_formal(agent: AgentState):

    queja = agent.queja_formal
    if queja:
        agent.interrupt_reason(f"queja formal del cliente: {queja}")
        return True
    else: 
        return False
        
def es_no_resolvible (agent: AgentState):

    

    return True


def necesita_humano(agent: AgentState):

    if importe_superado(agent) or es_queja_formal(agent) or es_no_resolvible(agent):
        print ("llamar a humano:")
        
        # TODO 