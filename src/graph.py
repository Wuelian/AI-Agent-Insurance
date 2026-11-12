from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from typing import Callable
from src.nodes.rag import rag_response
from src.nodes.router import nodo_router


def trivial_response(estado: AgentState):
    respuesta = {"role": "assistant", "content": "mensaje trivial"}
    return {"messages": [respuesta]}

def echo(estado: AgentState):
    ultimo = estado["messages"][-1]["content"]
    return {"messages": [{"role": "assistant", "content": f"Has dicho: {ultimo}"}]}

def init (nodo : Callable):
    nombre_nodo = nodo.__name__
    graph = StateGraph(AgentState) #Creamos un grafo de estados con el tipo AgentState
    graph.add_node(nodo) #Agregamos un nodo inicial
    graph.add_edge(START, nombre_nodo) #Agregamos un estado inicial que responde con un mensaje trivial
    graph.add_edge( nombre_nodo, END) #Agregamos un estado final que responde con un mensaje trivial
    graph = graph.compile() #Compilamos el grafo de estados
    
    return graph

    
if __name__ == "__main__":
    
    # Paso 1 --------------------------------------------------------

    # texto = input("Tú: ")

    # grafo_trivial = init(trivial_response)

    # estado_inicial_trivial = {
    #     "messages": [{"role": "user", "content": texto}],
    # }
    # ##usamos invoke para ejecutar el grafo de estados con el estado inicial
    # resultado = grafo_trivial.invoke(estado_inicial_trivial)
    # for mensaje in resultado["messages"]:
    #     print(f"{mensaje['role']}: {mensaje['content']}")



    # grafo_echo = init(echo)
    # estado_inicial_echo = {
    #     "messages": [{"role": "user", "content": texto}],
    # }
    # resultado_echo = grafo_echo.invoke(estado_inicial_echo)    
    # for mensaje in resultado_echo["messages"]:
    #     print(f"{mensaje['role']}: {mensaje['content']}")


    # Paso 4 --------------------------------------------------------
    # grafo_rag = init(rag_response)
    # pregunta_user_story1 = "¿Mi seguro de auto cubre lunas?"
    # pregunta_user_story5 = "¿Cubre mi seguro de salud una cirugía estética?"
    # estado_inicial_rag = {
    #     "messages": [{"role": "user", "content": pregunta_user_story1}],
    #     "product_type": "auto",
    # }
    # resultado_rag = grafo_rag.invoke(estado_inicial_rag)
    # for mensaje in resultado_rag["messages"]:
    #     print(f"{mensaje['role']}: {mensaje['content']}")

    # Paso 5 --------------------------------------------------------
    grafo_router = init(nodo_router)
    user_history_2 = "Quiero saber el estado de mi póliza P-10023" #Devuelve datos del dataset 
    user_history_6 = "¿qué tiempo hace hoy?" #fuera de domino, el agente indica que no puede ayudar     
    estado_inicial_router = {
        "messages": [{"role": "user", "content": user_history_2}],
    }
    resultado_router = grafo_router.invoke(estado_inicial_router)
    for mensaje in resultado_router["messages"]:
        mensaje.pretty_print()
    print("intent:", resultado_router.get("intent"))
    print("tool_results:", resultado_router.get("tool_results"))
    


# def init_trivial_response():
#     graph = StateGraph(AgentState) #Creamos un grafo de estados con el tipo AgentState
#     graph.add_node(trivial_response) #Agregamos un nodo inicial
#     graph.add_edge(START, "trivial_response") #Agregamos un estado inicial que responde con un mensaje trivial
#     graph.add_edge( "trivial_response", END) #Agregamos un estado final que responde con un mensaje trivial
#     graph = graph.compile() #Compilamos el grafo de estados

#     return graph

# def init_echo():
#     graph = StateGraph(AgentState) #Creamos un grafo de estados con el tipo AgentState
#     graph.add_node(echo) #Agregamos un nodo inicial
#     graph.add_edge(START, "echo") #Agregamos un estado inicial que responde con un mensaje trivial
#     graph.add_edge( "echo", END) #Agregamos un estado final que responde con un mensaje trivial
#     graph = graph.compile() #Compilamos el grafo de estados

#     return graph

    