from src.prompts.prompts  import VALIDAR_RESPUESTA_PROMPT
import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
from src.llm.llm import llm

def nodo_guardrails(estado: AgentState):
    # Respuesta generada por nodo_respuesta (último AIMessage)
    respuesta = next(m.content for m in reversed(estado["messages"]) if m.type == "ai")

    # Consulta del cliente (último HumanMessage)
    query = next(m.content for m in reversed(estado["messages"]) if m.type == "human")

    # Resultados de las tools como texto JSON
    tool_results = json.dumps(estado.get("tool_results") or {}, ensure_ascii=False, indent=2)

    mensajes = [
        SystemMessage(content=(
           VALIDAR_RESPUESTA_PROMPT
        )),
        HumanMessage(content=(
            f"Consulta del cliente:\n{query}\n\n"
            f"Resultados de las herramientas:\n{tool_results}\n\n"
            f"Respuesta generada:\n{respuesta}"
        )),
    ]

    validacion = llm.invoke(mensajes)

    return {"validacion_respuesta": validacion.text }


