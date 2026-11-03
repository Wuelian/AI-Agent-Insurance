from langgraph.graph import StateGraph, START, END
from state import AgentState
from typing import Callable


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
    texto = input("Tú: ")

    grafo_trivial = init(trivial_response)

    estado_inicial_trivial = {
        "messages": [{"role": "user", "content": texto}],
    }
    ##usamos invoke para ejecutar el grafo de estados con el estado inicial
    resultado = grafo_trivial.invoke(estado_inicial_trivial)
    for mensaje in resultado["messages"]:
        print(f"{mensaje['role']}: {mensaje['content']}")



    grafo_echo = init(echo)
    estado_inicial_echo = {
        "messages": [{"role": "user", "content": texto}],
    }
    resultado_echo = grafo_echo.invoke(estado_inicial_echo)    
    for mensaje in resultado_echo["messages"]:
        print(f"{mensaje['role']}: {mensaje['content']}")





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

    