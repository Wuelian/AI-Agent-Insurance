from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import interrupt
from src.state import AgentState

# Nombres legibles para el cliente de los campos de abrir_siniestro
NOMBRES_CAMPOS = {
    "numero_poliza": "el número de póliza",
    "descripcion": "una descripción de lo ocurrido",
    "fecha": "la fecha del siniestro (DD/MM/AAAA)",
    "importe_estimado": "el importe estimado de los daños (en €)",
}


def nodo_pedir_datos(estado: AgentState):
    """Pide al cliente los datos que faltan para abrir el siniestro y vuelve al router con su respuesta."""
    siniestro = (estado.get("tool_results") or {}).get("abrir_siniestro") or {}
    faltan = siniestro.get("faltan", [])

    pregunta = "Para abrir el siniestro necesito que me indiques: " + \
               ", ".join(NOMBRES_CAMPOS.get(campo, campo) for campo in faltan) + "."

    # Se para el grafo. El main muestra la pregunta y reanuda con lo que escriba el cliente.
    respuesta_cliente = interrupt({
        "tipo": "pedir_datos",
        "pregunta": pregunta,
        "faltan": faltan,
    })

    # Tras el resume: la pregunta y la respuesta quedan en el historial para que el router las vea
    return {
        "messages": [
            AIMessage(content=pregunta),
            HumanMessage(content=respuesta_cliente),
        ]
    }