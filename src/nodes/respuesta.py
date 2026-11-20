from src.tools.tools import generar_respuesta
from src.state import AgentState
from langchain_core.messages import AIMessage,SystemMessage,HumanMessage
from src.llm.llm import llm 
import truststore
from dotenv import load_dotenv
import json

truststore.inject_into_ssl()
load_dotenv()


llm_con_tools = llm.bind_tools(tools=[generar_respuesta])


def nodo_respuesta (estado: AgentState):
    query = estado["messages"][-1].content   # último mensaje = pregunta del cliente
    tool_results = estado.get("tool_results") or {}

    mensajes = [
        SystemMessage(content=(
            "Llama a la herramienta generar_respuesta con la consulta del cliente y los "
            "resultados de las herramientas, copiándolos exactamente, sin resumir ni modificar nada."
        )),
        HumanMessage(content=(
            f"Consulta del cliente:\n{query}\n\n"
            f"Resultados de las herramientas:\n{json.dumps(tool_results, ensure_ascii=False, indent=2)}"
        )),
    ]

    respuesta = llm_con_tools.invoke(mensajes)

    if respuesta.tool_calls:
        args = respuesta.tool_calls[0]["args"]      # argumentos que ha escrito el LLM
        texto = generar_respuesta.invoke(args)
    else:
        texto = respuesta.text                      # por si aun así no llama a la tool

    return {"messages": [AIMessage(content=texto)]}