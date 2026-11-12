from dotenv import load_dotenv
import truststore
from pydantic import BaseModel, Field
from typing import Literal, Optional
from langchain.agents import create_agent
from src.state import AgentState
import json


#ToolMessage muestra las salidas de las ejecuciones de las Tools 
from langchain.messages import ToolMessage

from src.tools.tools import consultar_poliza,consultar_siniestro,buscar_en_documentacion    

truststore.inject_into_ssl()
load_dotenv()


SYSTEM_PROMPT = """Eres AsegurIA, el asistente virtual de Seguros Horizonte.
Atiendes consultas de clientes sobre sus seguros de auto, hogar y salud.

Tu tarea es entender qué necesita el cliente y obtener la información
necesaria con las herramientas disponibles:
- Para dudas sobre coberturas, exclusiones, carencias, franquicias, plazos
  o trámites, usa buscar_en_documentacion.
- Para los datos o el estado de una póliza concreta, usa consultar_poliza.
- Para el estado de un siniestro ya abierto, usa consultar_siniestro.

Reglas:
1. No inventes datos de pólizas, siniestros, coberturas, importes ni plazos.
   Toda la información debe salir de las herramientas.
2. Si para usar una herramienta te falta un dato (por ejemplo, el número de
   póliza o de siniestro), no lo supongas: pídeselo al cliente.
3. Si una herramienta devuelve un error (por ejemplo, una póliza que no
   existe), no lo ocultes ni lo sustituyas por datos inventados.
4. Si la consulta no tiene relación con seguros, no uses ninguna herramienta.
5. Al terminar, clasifica la consulta del cliente según el formato de
   respuesta indicado.
"""

#Structured output
class Answer(BaseModel):
    """Clasificación de la consulta del cliente, para dirigir el flujo del agente."""

    intent: Literal[
        "dentro_dominio",
        "fuera_dominio",
    ] = Field(
        description=(
            "Clasifica el mensaje del cliente según su TEMA, no según si has usado "
        "herramientas.\n"
        "REGLA PRINCIPAL: si el mensaje contiene varias consultas y AL MENOS UNA "
        "trata de seguros, clasifícalo como dentro_dominio, aunque el resto no "
        "tenga relación con seguros.\n"
        "\n"
        "- dentro_dominio: alguna parte del mensaje trata de:\n"
        "  1. Dudas generales sobre qué cubre o no un seguro: coberturas, "
        "exclusiones, carencias, franquicias, plazos o trámites.\n"
        "  2. Los datos o el estado de una póliza concreta del cliente.\n"
        "  3. El estado de un siniestro que ya existe.\n"
        "  4. Un daño o incidente que el cliente ha sufrido y quiere declarar, "
        "aunque también pregunte qué hacer o si está cubierto.\n"
        "  También es dentro_dominio si es una consulta de seguros a la que le "
        "falta un dato (por ejemplo, el número de póliza), o un saludo o "
        "agradecimiento.\n"
        "\n"
        "- fuera_dominio: NINGUNA parte del mensaje trata de seguros "
        "(por ejemplo, solo pregunta por el tiempo, deportes o recetas).\n"
        "\n"
        "Ejemplo: 'Quiero abrir un siniestro por un accidente. ¿Qué tiempo hace "
        "hoy?' es dentro_dominio."    
        )
    )
    product_type: Optional[Literal["auto", "hogar", "salud"]] = Field(
        default=None,
        description=(
            "Seguro al que se refiere la consulta. "
            "Déjalo vacío si el cliente no lo indica o si es fuera de dominio."
        ),
    )


agent = create_agent(
    model="google_genai:gemini-3.5-flash-lite",
    tools=[consultar_siniestro,consultar_poliza,buscar_en_documentacion], #falta añadir abrir siniestro que no esta implementado
    system_prompt= SYSTEM_PROMPT,
    response_format=Answer
)

def nodo_router (estado: AgentState) -> dict:
    query = estado["messages"][-1].content #solicitud/consulta del usuario
    #ejecuta las tools si es que las necesita y devuelve dentro o fuera de dominio
    result =  agent.invoke ({"messages": [{"role": "user", "content": query}]})
    answer = result["structured_response"].intent #devuelve dentro_dominio o fuera_dominio
    estado["intent"] = result["structured_response"].intent

    # por hacer : tenemos la salida del agente pero 
    # se la tenemos que pasar al estado para usarlo despues en el grafo

    tool_results = {}
    for m in result["messages"]:
        if m.type == "tool":
            try:
                tool_results[m.name] = json.loads(m.content)
            except (json.JSONDecodeError, TypeError):
                tool_results[m.name] = m.content
    
    intent = "dentro_dominio" if tool_results else result["structured_response"].intent

    return {
        "intent": intent,
        "product_type": result["structured_response"].product_type,
        "tool_results": tool_results,
    }


if __name__ == "__main__":
    user_history_2 = "Quiero saber el estado de mi póliza P-10023" #Devuelve datos del dataset 
    user_history_6 = "¿qué tiempo hace hoy?" #fuera de domino, el agente indica que no puede ayudar     
    #prueba simple historia de usuario 1 y 2
    #result =  agent.invoke ({"messages": [{"role": "user", "content": "¿Mi seguro de auto cubre lunas? Ademas Quiero saber el estado de mi póliza P-10023 "}]})
    
    #prueba simple historia de usuario 2 y 6
    result =  agent.invoke ({"messages": [{"role": "user", "content": user_history_2}]})
    
    for m in result["messages"]:
        if m.type == "tool":
            print(m.name, "→", m.content)

    print (result["structured_response"].intent)




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
