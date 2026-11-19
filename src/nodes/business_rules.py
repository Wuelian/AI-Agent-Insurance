# Esta clase es para definir las reglas de negocio
from src.state import AgentState
from langgraph.types import interrupt


UMBRAL = 3000


#TODO 
def importe_superado (estado: AgentState):
    tool_results = estado.get("tool_results") or {}
    borrador = tool_results.get("abrir_siniestro")

    # solo hay importe si se llamó a abrir_siniestro y devolvió un borrador válido
    if not isinstance(borrador, dict) or "error" in borrador:
        return None

    importe = borrador.get("importe_estimado")
    if importe is not None and importe > UMBRAL:
        return f"Importe estimado del siniestro superior al umbral: {importe} € (umbral: {UMBRAL} €)."
    return None

#Por consultar con Javi, en teoria estos dos casos  
def es_queja_formal(estado):
    queja = estado.get("queja_formal")
    if queja:
        return f"Queja formal del cliente: {queja}"
    return None

        
def documentacion_insuficiente (estado: AgentState):
    if estado.get("documentacion_insuficiente"):
        return "La consulta no puede resolverse con la documentación disponible."
    return None


def intervencion_humano ():
    
    approved = interrupt("necesita humano")
    #--- Da control al humano conectando otro sistema externo
    return approved




def necesita_humano(estado: AgentState):
    motivos = [

        
        motivo
        for motivo in (
            importe_superado(estado),
            es_queja_formal(estado),
            documentacion_insuficiente(estado),
        )
        if motivo is not None
    ]
    requiresHuman= bool(motivos) # si existen motivos entonces es true
    # TODO Paso 7: si requires_human es True, pausar con interrupt
    if requiresHuman:
      intervencion_humano()




    return {
        "requires_human": requiresHuman ,
        "interrupt_reason": " ".join(motivos) if motivos else None,
    }



if __name__ == "__main__":

    prueba1 = "a"
    
