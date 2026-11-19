from dotenv import load_dotenv
import truststore
from pydantic import BaseModel, Field
from typing import Literal, Optional
from langchain.agents import create_agent
from src.state import AgentState
import json
from src.llm.llm import llm 
from langchain.messages import SystemMessage, HumanMessage


from src.prompts.prompts  import ROUTER_SYSTEM_PROMPT,INTENT_DESCRIPTION,QUEJA_FORMAL_DESCRIPTION,DOCUMENTACION_INSUFICIENTE_DESCRIPTION


#ToolMessage muestra las salidas de las ejecuciones de las Tools 
from langchain.messages import ToolMessage

from src.tools.tools import consultar_poliza,consultar_siniestro,buscar_en_documentacion,abrir_siniestro    

truststore.inject_into_ssl()
load_dotenv()


#Structured output
class Answer(BaseModel):
    """Clasificación de la consulta del cliente, para dirigir el flujo del agente."""

    intent: Literal[
        "dentro_dominio",
        "fuera_dominio",
    ] = Field(
        description=(
              INTENT_DESCRIPTION
        )
    )
    product_type: Optional[Literal["auto", "hogar", "salud"]] = Field(
        default=None,
        description=(
            "Seguro al que se refiere la consulta. "
            "Déjalo vacío si el cliente no lo indica o si es fuera de dominio."
        ),
    )
    queja_formal: Optional[str] = Field (
        default = None,
        description = (
                QUEJA_FORMAL_DESCRIPTION
        )
    )
    documentacion_insuficiente: Optional [bool]= Field(
        default = None,
        description = (
                DOCUMENTACION_INSUFICIENTE_DESCRIPTION
        )
    )


#------------------ Usar LLM con create Agents ------------------
agent = create_agent(
    model="google_genai:gemini-3.5-flash-lite",
    tools=[consultar_siniestro,consultar_poliza,buscar_en_documentacion,abrir_siniestro], #falta añadir abrir siniestro que no esta implementado
    system_prompt= ROUTER_SYSTEM_PROMPT,
    response_format=Answer
)


# ------------------ Usar LLM con bind tools ------------------
tools = [consultar_siniestro,consultar_poliza,buscar_en_documentacion,abrir_siniestro]
tools_por_nombre = {t.name: t for t in tools}
#usamos bind tools para pasarle las tools que necesita el llm
llm_con_tools = llm.bind_tools(tools= tools)
#creamos un clasificador para que posteriormente nos saque la salida estructurada de la llm despues de invocarla 
clasificador = llm.with_structured_output(Answer)
# Numero maximo de vueltas que se da para el LLM con las tools 
MAX_VUELTAS = 5 




def nodo_router (estado: AgentState) -> dict:

    # # ------------------ Con create agent ---------------------------
    # query = estado["messages"][-1].content #solicitud/consulta del usuario
    # #ejecuta las tools si es que las necesita y devuelve dentro o fuera de dominio
    # result =  agent.invoke ({"messages": [{"role": "user", "content": query}]})
    
    # # answer = result["structured_response"].intent #devuelve dentro_dominio o fuera_dominio
    # # estado["intent"] = result["structured_response"].intent

    # # por hacer : tenemos la salida del agente pero 
    # # se la tenemos que pasar al estado para usarlo despues en el grafo
    # tool_results = {}
    # for m in result["messages"]:
    #     if m.type == "tool":
    #         try:
    #             tool_results[m.name] = json.loads(m.content)
    #         except (json.JSONDecodeError, TypeError):
    #             tool_results[m.name] = m.content
    
    # intent = "dentro_dominio" if tool_results else result["structured_response"].intent

    # #en caso de que no se pueda responder a la consulta del usuario con la documentacion
    # answer = result["structured_response"]

    # documentacion_insuficiente = (
    #     answer.documentacion_insuficiente
    #     if "buscar_en_documentacion" in tool_results
    #     else None
    # )

    #------------------ haciendo un bucle con bind tools ------------------
    query = estado["messages"][-1].content #solicitud/consulta del usuario

    mensajes = [SystemMessage(content= ROUTER_SYSTEM_PROMPT), HumanMessage(content= query)]
    #Diccionario para guardar la salida de las tools
    tool_results = {}

    #vuelta manual
    for vuelta in range(MAX_VUELTAS ):

        respuesta_con_bindtools = llm_con_tools.invoke(mensajes)
        mensajes.append(respuesta_con_bindtools)          # ← la línea que faltaba

        #si no se llama a ninguna tool acaba el bucle
        if not respuesta_con_bindtools.tool_calls:
            #print(f"Vuelta {vuelta}: respuesta final")  --------- lo comento para que la terminal no se pete de mensajes
            break

        for llamada in respuesta_con_bindtools.tool_calls:
            tool = tools_por_nombre[llamada["name"]]
            resultado = tool.invoke(llamada["args"])
            #Guarda el contenido de los resultados dentro del campo de toolsresults 
            tool_results[llamada["name"]] = resultado   
            
            #Mensajes para que la LLM lea y vea los resultados 
            mensajes.append(ToolMessage(                # para el LLM (texto)
            content=json.dumps(resultado, ensure_ascii=False),
            tool_call_id=llamada["id"],
            name=llamada["name"],
            ))

    mensajes.append (HumanMessage(content="Con todo lo anterior, clasifica la consulta" \
    " del cliente según el formato indicado."))

    #devuelve la salida directamente con el formato de answer
    respuesta_clasificada = clasificador.invoke (mensajes)

    intent = "dentro_dominio" if tool_results else respuesta_clasificada.intent
    
    documentacion_insuficiente = (
            respuesta_clasificada.documentacion_insuficiente
            if "buscar_en_documentacion" in tool_results
            else None
        )

    return {
        "intent": intent,
        #"product_type": result["structured_response"].product_type,
        "product_type": respuesta_clasificada.product_type,
        "tool_results": tool_results,
        #"queja_formal": result["structured_response"].queja_formal,
        "queja_formal": respuesta_clasificada.queja_formal,
        "documentacion_insuficiente": documentacion_insuficiente
    }


if __name__ == "__main__":

    user_history_2 = "Quiero saber el estado de mi póliza P-10023" #Devuelve datos del dataset 
    user_history_6 = "¿qué tiempo hace hoy?" #fuera de domino, el agente indica que no puede ayudar     
    #prueba simple historia de usuario 1 y 2
    #result =  agent.invoke ({"messages": [{"role": "user", "content": "¿Mi seguro de auto cubre lunas? Ademas Quiero saber el estado de mi póliza P-10023 "}]})
    
    #prueba simple historia de usuario 2 y 6
    # result =  agent.invoke ({"messages": [{"role": "user", "content": user_history_2}]})
    
    # for m in result["messages"]:
    #     if m.type == "tool":
    #         print(m.name, "→", m.content)

    # print (result["structured_response"].intent)

    
    estado_inicial_prueba = {
        "messages": [HumanMessage(content="Quiero saber el estado de mi póliza P-10023")],
    }
    prueba = nodo_router(estado_inicial_prueba)
    print (prueba)






















#APUNTES

# asi se hace a mano 

# tools = [consulta_cobertura_tool,consultar_poliza_tool,consultar_siniestro_tool,abrir_siniestro_tool]
# intent = ["consulta_cobertura", "consulta_poliza", "consulta_siniestro", "abrir_siniestro", "fuera_dominio"]
# consulta_cobertura_tool = {
# "type": "function",
#     "name": "nodo_rag",
#     "description": (
#         """Devuelve una respuesta despues de hacer una consulta en el RAG 
#         a partir del mensaje del usuario que será una consulta con respecto a la cobertura de sus seguros"""
#     ),
#     "parameters": {
#         "type": "AgentState",
#         "properties": {
#             "estado": {
#                 "type": "number",
#                 "description": (
#                     """recibe el estado del agente, que contiene la informacion de la conversacion y el contexto del usuario,
#                     contiene la consulta del usuario y en base a eso se determina el tipo de producto que esta clasificado en :
#                     "product_type": Optional[str]    # "auto" | "hogar" | "salud" | "general
#                     """
                    
#                 ),
#             },
          
#         },
#         "required": ["estado"],
#     },

# }
# consultar_poliza_tool = {
# "type": "function",
#     "name": "consultar_poliza",
#     "description": (
#         """Devuelve la poliza del cliente con su informacion recibiendo un numero de poliza como parametro de entrada,
#         en caso de que ese numero de poliza sea erroneo o no exista dentro de la base de datos devolvera un mensaje de error
#         """
#     ),
#     "parameters": {
#         "type": "str",
#         "properties": {
#             "numero_poliza": {
#                 "type": "str",
#                 "description": (
#                     """recibe el numero de poliza del cliente que esta guardado en el archivo json correspondiente"""
                    
#                 ),
#             },
          
#         },
#         "required": ["numero_poliza"],
#     },


# }
# consultar_siniestro_tool = {
# "type": "function",
#     "name": "consultar_siniestro",
#     "description": (
#         """Devuelve el siniestro con su informacion recibiendo un numero de siniestro como parametro de entrada,
#         en caso de que ese numero de siniestro sea erroneo o no exista dentro de la base de datos devolvera un mensaje de error
#         """
#     ),
#     "parameters": {
#         "type": "str",
#         "properties": {
#             "numero_siniestro": {
#                 "type": "str",
#                 "description": (
#                     """recibe el numero de siniestro que esta guardado en el archivo json correspondiente"""
                    
#                 ),
#             },
          
#         },
#         "required": ["numero_siniestro"],
#     },

# }
# abrir_siniestro_tool = {
# "type": "function",
#     "name": "abrir_siniestro",
#     "description": (
#         #To-Do
#         """Abre un siniestro"""
#     ),

# }


# Function calling Con Gemini 

# def get_chatbot_response_gemini(mensaje_usuario: str) -> str:

#     interaction = client.interactions.create(
#         model="gemini-3.5-flash-lite",
#         store=False,
#         system_instruction=SYSTEM_PROMPT,
#         input=mensaje_usuario,
#         tools = tools
#     )
    
#     return interaction.steps[-1].content[0].text
