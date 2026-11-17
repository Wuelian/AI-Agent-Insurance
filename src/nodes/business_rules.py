# Esta clase es para definir las reglas de negocio
from src.state import AgentState

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

    # TODO Paso 7: si requires_human es True, pausar con interrupt

    return {
        "requires_human": bool(motivos),
        "interrupt_reason": " ".join(motivos) if motivos else None,
    }



if __name__ == "__main__":

    prueba1 = "a"
    
