import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.tools.tools import comprobar_formato
from src.state import AgentState
from src.llm.llm import llm

llm_con_tools = llm.bind_tools([comprobar_formato], tool_choice="comprobar_formato")


def nodo_guardrails(estado: AgentState):
    # Respuesta generada por nodo_respuesta (último AIMessage)
    respuesta = next(m.content for m in reversed(estado["messages"]) if m.type == "ai")

    # Consulta del cliente (último HumanMessage)
    query = next(m.content for m in reversed(estado["messages"]) if m.type == "human")

    # Resultados de las tools como texto JSON
    tool_results = json.dumps(estado.get("tool_results") or {}, ensure_ascii=False, indent=2)

    mensajes = [
        SystemMessage(content=(
            "Llama a la herramienta comprobar_formato con la consulta del cliente, los resultados "
            "de las herramientas y la respuesta generada, copiándolos exactamente, sin modificar nada."
        )),
        HumanMessage(content=(
            f"Consulta del cliente:\n{query}\n\n"
            f"Resultados de las herramientas:\n{tool_results}\n\n"
            f"Respuesta generada:\n{respuesta}"
        )),
    ]

    llamada = llm_con_tools.invoke(mensajes)

    if llamada.tool_calls:
        args = llamada.tool_calls[0]["args"]          # query, tool_results, respuesta
        validacion = comprobar_formato.invoke(args)
    else:
        validacion = llamada.text

    print("Guardrails:", validacion)
    return {"validacion_respuesta": validacion}