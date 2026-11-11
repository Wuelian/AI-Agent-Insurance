from dotenv import load_dotenv
from google import genai
import truststore
from pydantic import BaseModel, Field
from typing import Literal, Optional
from langchain.agents import create_agent



truststore.inject_into_ssl()
load_dotenv()
client = genai.Client()

intent = ["consulta_cobertura", "consulta_poliza", "consulta_siniestro", "abrir_siniestro", "fuera_de_dominio"]

SYSTEM_PROMPT = f"Eres AsegurIA, el asistente virtual de Seguros Horizonte." \
"En funcion del mensaje que recibas vas a clasificar la intencion del cliente en una de las siguientes categorias: " \
"{intet}, y devolveras una respuesta estructurada para hacer function calling" \



consulta_cobertura_tool = {
"type": "function",
    "name": "nodo_rag",
    "description": (
        """Devuelve una respuesta despues de hacer una consulta en el RAG 
        a partir del mensaje del usuario que será una consulta con respecto a la cobertura de sus seguros"""
    ),
    "parameters": {
        "type": "AgentState",
        "properties": {
            "estado": {
                "type": "number",
                "description": (
                    """recibe el estado del agente, que contiene la informacion de la conversacion y el contexto del usuario,
                    contiene la consulta del usuario y en base a eso se determina el tipo de producto que esta clasificado en :
                    "product_type": Optional[str]    # "auto" | "hogar" | "salud" | "general
                    """
                    
                ),
            },
          
        },
        "required": ["estado"],
    },

}
consultar_poliza_tool = {
"type": "function",
    "name": "consultar_poliza",
    "description": (
        """Devuelve la poliza del cliente con su informacion recibiendo un numero de poliza como parametro de entrada,
        en caso de que ese numero de poliza sea erroneo o no exista dentro de la base de datos devolvera un mensaje de error
        """
    ),
    "parameters": {
        "type": "str",
        "properties": {
            "numero_poliza": {
                "type": "str",
                "description": (
                    """recibe el numero de poliza del cliente que esta guardado en el archivo json correspondiente"""
                    
                ),
            },
          
        },
        "required": ["numero_poliza"],
    },


}
consultar_siniestro_tool = {
"type": "function",
    "name": "consultar_siniestro",
    "description": (
        """Devuelve el siniestro con su informacion recibiendo un numero de siniestro como parametro de entrada,
        en caso de que ese numero de siniestro sea erroneo o no exista dentro de la base de datos devolvera un mensaje de error
        """
    ),
    "parameters": {
        "type": "str",
        "properties": {
            "numero_siniestro": {
                "type": "str",
                "description": (
                    """recibe el numero de siniestro que esta guardado en el archivo json correspondiente"""
                    
                ),
            },
          
        },
        "required": ["numero_siniestro"],
    },

}
abrir_siniestro_tool = {
"type": "function",
    "name": "abrir_siniestro",
    "description": (
        #To-Do
        """Abre un siniestro"""
    ),

}
marcar_fuera_de_dominio_tool = {
"type": "function",
    "name": "marcar_fuera_de_dominio",
    "description": (
        """devuelve el literal 'fuera_de_dominio' cuando no se usa ninguna de las otras tools"""
    ),

}

tools = [consulta_cobertura_tool,consultar_poliza_tool,consultar_siniestro_tool,abrir_siniestro_tool,marcar_fuera_de_dominio_tool]


agent = create_agent(
    model="gemini-3.5-flash-lite",
    tools=tools,
    system_prompt= SYSTEM_PROMPT,
)

agent_con_tools = agent.bind_tools(tools)

def decidir_tool (mensaje : str):
    agent_con_tools.invoke (mensaje)
    





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
