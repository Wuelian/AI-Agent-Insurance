from src.tools.tools import buscar_en_documentacion 
from google import genai
from dotenv import load_dotenv
from src.state import AgentState
import truststore
truststore.inject_into_ssl()


load_dotenv()
client = genai.Client()

RETRIEVING_PROMPT ="""Eres AsegurIA, el asistente virtual de Seguros Horizonte.
Respondes dudas de clientes sobre las coberturas y condiciones de sus seguros.

Responde ÚNICAMENTE con la información de los FRAGMENTOS de la documentación
oficial que aparecen más abajo. Sigue estas reglas:

1. Cita siempre la fuente: el nombre del documento y la sección o artículo
   de donde sale la información. Por ejemplo:
   "Según las Condiciones Generales de Auto, Art. 2 — Coberturas, ..."
2. Si la respuesta depende de una exclusión, una carencia o una franquicia,
   dilo de forma explícita y cita la cláusula correspondiente.
3. Si los fragmentos no contienen la información necesaria para responder,
   no la deduzcas ni la completes con conocimiento general. Di claramente
   que no lo encuentras en la documentación disponible.
4. No inventes importes, plazos, porcentajes ni condiciones que no aparezcan
   literalmente en los fragmentos.
5. Responde en español, de forma clara y breve, dirigiéndote al cliente.

FRAGMENTOS DE LA DOCUMENTACIÓN:
{fragmentos}

PREGUNTA DEL CLIENTE:
{pregunta}
"""

def respuesta_llm (query: str, producto, search_results) -> str:

    fragmentos = "\n\n".join([f"Fragmento {i+1}: {doc}" for i, doc in enumerate(search_results)])

    inputs = RETRIEVING_PROMPT.format(fragmentos=fragmentos, pregunta=query)

    interaction = client.interactions.create(
             model="gemini-3.5-flash-lite",
             store=False,
             input=inputs,
         )
    print("="*60)
    print("CHUNKS RECUPERADOS")
    print(fragmentos)
    print("="*60)
    return interaction.steps[-1].content[0].text

# def nodo_rag (estado: AgentState) -> str:
#     query = estado["messages"][-1]["content"]
#     producto = estado["product_type"]
#     search_results =  buscar_en_documentacion(query, producto)
#     estado["retrieved_docs"] = search_results
#     #devuelve la respuesta del LLM usando la query, el producto y los resultados de la busqueda en la documentacion
#     return respuesta_llm(query, producto, search_results)

def nodo_rag(estado: AgentState) -> dict:
    query = estado["messages"][-1]["content"]
    producto = estado["product_type"]

    search_results = buscar_en_documentacion(query, producto)
    respuesta = respuesta_llm(query, producto, search_results)

    return {
        "messages": [{"role": "assistant", "content": respuesta}],
        "retrieved_docs": search_results,
    }

# pregunta_user_story1 = "¿Mi seguro de auto cubre lunas?"
# pregunta_user_story5 = "¿Cubre mi seguro de salud una cirugía estética?"

# estado: AgentState  = {
#     "messages": [{"role": "user", "content": pregunta_user_story5}],
#     "product_type": "salud",
#     "requires_human": "false", 
# }


# print(nodo_rag(estado))
