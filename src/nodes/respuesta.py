from src.prompts.prompts  import GENERAR_RESPUESTA_PROMPT
from src.state import AgentState
from langchain_core.messages import AIMessage,SystemMessage,HumanMessage ,AnyMessage
from src.llm.llm import llm 
import json


def nodo_respuesta (estado: AgentState):
    query = estado["messages"][-1].content   # último mensaje = pregunta del cliente
    tool_results = estado.get("tool_results") or {}

    # Historial en texto, sin el último mensaje (la pregunta actual ya va en "Consulta del cliente")
    historial = "\n".join(
        f"{'Cliente' if m.type == 'human' else 'AsegurIA'}: {m.content}"
        for m in estado["messages"][:-1]
    ) or "(sin mensajes anteriores)"

    mensajes = [
        SystemMessage(content=(
            GENERAR_RESPUESTA_PROMPT
        )),
        HumanMessage(content=(
           # f"Historial de la conversación:\n{historial}\n\n"
            f"Clasificación de la consulta: {estado.get('intent')}\n"
            f"Consulta del cliente:\n{query}\n\n"
            f"Resultados de las herramientas:\n{json.dumps(tool_results, ensure_ascii=False, indent=2)}"
        ))
    ]

    respuesta = llm.invoke(mensajes)

    return {"messages": [AIMessage(content=respuesta.text)]}

