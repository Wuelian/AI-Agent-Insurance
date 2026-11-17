from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from typing import Callable
from src.nodes.rag import rag_response
from src.nodes.router import nodo_router
from src.nodes.business_rules import necesita_humano
from langgraph.types import Command, interrupt



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

def init_grafo_pruebas():
    graph = StateGraph(AgentState) #Creamos un grafo de estados con el tipo AgentState
    graph.add_node("router",nodo_router)
    
    graph.add_node("nodoNegocio",necesita_humano)
    graph.add_edge(START, "router")
    graph.add_edge("router", "nodoNegocio")
    graph.add_edge("nodoNegocio", END)
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
    # grafo_router = init(nodo_router)
    # user_history_2 = "Quiero saber el estado de mi póliza P-10023" #Devuelve datos del dataset 
    # user_history_6 = "¿qué tiempo hace hoy?" #fuera de domino, el agente indica que no puede ayudar     
    # estado_inicial_router = {
    #     "messages": [{"role": "user", "content": user_history_2}],
    # }
    # resultado_router = grafo_router.invoke(estado_inicial_router)
    # for mensaje in resultado_router["messages"]:
    #     mensaje.pretty_print()
    # print("intent:", resultado_router.get("intent"))
    # print("tool_results:", resultado_router.get("tool_results"))

    
    # print(grafo_router.get_graph().draw_mermaid())

    # Paso 7 --------------------------------------------------------

    #Probar que funciona bien el nodo de negocio
    # grafo_nodoNegocio = init (necesita_humano)
    # estado_inicial_nodoNegocio = {
    #     "messages": [{"role": "user", "content": "Quiero abrir un siniestro: ayer se me rompió una tubería en la cocina, "
    #                    "mi póliza es la P-10023 y calculo unos 8.000 € de daños."}],
    #         }
    # resultado_nodoNegocio = grafo_nodoNegocio.invoke(estado_inicial_nodoNegocio)
    # print("requires_human:", resultado_nodoNegocio ["requires_human"])
    # print("motivo:", resultado_nodoNegocio ["interrupt_reason"])

    #Conectar nodos router y nodo negocio

    caso_documentacion_insuficiente = "Se me ha caído la televisión y se ha roto la pantalla, ¿me la cubre?"
    caso_queja_formal = "quiero presentar una queja formal"
    caso_importe_superado = "Quiero declarar un siniestro. El 10 de noviembre de 2026 tuve un accidente con el coche: " \
    "choqué contra un muro al aparcar y se ha destrozado todo el frontal. Mi póliza es la P-10023 y el taller calcula " \
    "unos 8.000 € de reparación"

    grafo_prueba = init_grafo_pruebas()
    estado_inicial_prueba = {
        "messages": [{"role": "user", "content": caso_importe_superado }],
            }
    resultado_nodo_prueba = grafo_prueba.invoke(estado_inicial_prueba)




    print("requires_human:", resultado_nodo_prueba ["requires_human"])
    print("motivo:", resultado_nodo_prueba ["interrupt_reason"])
    print("intent:", resultado_nodo_prueba.get("intent"))
    print("tool_results:", resultado_nodo_prueba.get("tool_results"))
    print("queja_formal:", resultado_nodo_prueba.get("queja_formal"))
    print("documentacion_insuficiente:", resultado_nodo_prueba.get("documentacion_insuficiente"))      




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

    