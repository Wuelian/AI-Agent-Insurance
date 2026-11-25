CONSULTAR_POLIZA_DOCSTRING =  """Consulta los datos de una póliza concreta de un cliente: titular,
producto contratado, coberturas, vigencia y estado.

Úsala cuando el cliente pregunte por el estado o los datos de SU póliza
y proporcione su número. No la uses para dudas generales sobre qué
cubre un tipo de seguro: para eso está buscar_en_documentacion.

Args:
    numero_poliza: Número de póliza tal como lo indica el cliente,
        con el formato "P-" seguido de cifras (por ejemplo, "P-10023").

Returns:
    Los datos de la póliza, o un diccionario con la clave "error" si no
    existe ninguna póliza con ese número.
""" 

CONSULTAR_SINIESTRO_DOCSTRING = """Consulta el estado y los datos de un siniestro ya abierto.

Úsala cuando el cliente pregunte cómo va un siniestro existente y
proporcione su número. No la uses para abrir un siniestro nuevo.

Args:
    numero_siniestro: Número de siniestro tal como lo indica el cliente,
        con el formato "S-" seguido de cifras (por ejemplo, "S-5001").

Returns:
    Los datos del siniestro, o un diccionario con la clave "error" si no
    existe ningún siniestro con ese número.
"""
BUSCAR_EN_DOCUMENTACION_DOCSTRING ="""Busca en la documentación oficial de Seguros Horizonte (condiciones
generales y preguntas frecuentes) los fragmentos que responden a una
duda sobre coberturas, exclusiones, carencias, franquicias, plazos o
trámites.

Úsala para preguntas generales sobre qué cubre o no cubre un seguro, o
sobre cómo hacer un trámite. No la uses para consultar los datos de
una póliza o un siniestro concretos.
Si los fragmentos no contienen la información necesaria para responder,
no la deduzcas ni la completes con conocimiento general. Di claramente
que no lo encuentras en la documentación disponible.


Args:
    query: Lo esencial de la duda del cliente, en pocas palabras
        (por ejemplo, "rotura de lunas" o "cirugía estética").
    producto: Seguro al que se refiere la pregunta: "auto", "hogar" o
        "salud". Déjalo vacío si el cliente no indica de qué seguro habla.

Returns:
    Lista de fragmentos de la documentación relacionados con la consulta.
"""


ABRIR_SINIESTRO_DOCSTRING = """Valida y prepara la apertura de un siniestro nuevo.

Úsala en cuanto el cliente quiera declarar un daño o incidente, aunque
todavía no haya dado todos los datos. Pasa solo los datos que el cliente
haya proporcionado explícitamente y deja vacíos los demás: nunca inventes
ni supongas un valor. La herramienta indicará qué datos faltan o no son
válidos para que se los pidas al cliente.

El siniestro debe estar ligado a una póliza existente y vigente, y la
fecha en la que ocurrió no puede ser futura.

No la uses para consultar un siniestro que ya existe: para eso está
consultar_siniestro.

Args:
    numero_poliza: Número de póliza tal como lo indica el cliente, con el
        formato "P-" seguido de cifras (por ejemplo, "P-10023").
    descripcion: Descripción breve de lo ocurrido, con las palabras del
        cliente (por ejemplo, "rotura de una tubería en la cocina").
    fecha: Fecha en la que ocurrió el siniestro (no la fecha de hoy), en
        formato AAAA-MM-DD. Si el cliente la indica de otra forma,
        conviértela a este formato solo si no hay ambigüedad; si la hay,
        déjala vacía.
    importe_estimado: Importe estimado de los daños en euros, como número
        (por ejemplo, 8000.0).

Returns:
    Si todos los datos están completos y son válidos, un borrador del
    siniestro pendiente de revisión (todavía no queda registrado). Si
    falta algún dato, un diccionario con la clave "error" y la lista de
    datos que faltan en "faltan". Si algún dato no es válido (por ejemplo,
    una póliza inexistente o no vigente, o una fecha futura), un
    diccionario con la clave "error" y el motivo de cada dato no válido.
"""

#Integracion del MCP 
from mcp.server.fastmcp import FastMCP
from datetime import date
from typing import Optional,Literal
import json
import chromadb
import os
from pathlib import Path
import os 

# Carpeta donde está este fichero: .../agente-seguros/mcp_servers/policy_server
CARPETA_ACTUAL = Path(__file__).resolve().parent

# Subimos dos niveles: policy_server -> mcp_servers -> agente-seguros
RAIZ_PROYECTO = CARPETA_ACTUAL.parents[1]

# Si existe la variable de entorno se usa; si no, la ruta calculada
DATA_DIR = Path(os.getenv("DATA_DIR", RAIZ_PROYECTO / "data"))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", RAIZ_PROYECTO / "chroma_db"))

# Create an MCP server
mcp = FastMCP("MCP_Service")

collection = chromadb.PersistentClient(path=CHROMA_DIR).get_collection(name="embeddings_collection")
ruta_polizas =  DATA_DIR / "db/polizas_clientes.json"
ruta_siniestros =  DATA_DIR / "db/siniestros_historico.json"



#@tool(parse_docstring=True) Como ya no usamos el literal dentro de la funcion se la pasamos de la siguiente forma
@mcp.tool(description=CONSULTAR_POLIZA_DOCSTRING)
def consultar_poliza(numero_poliza: str) -> dict:

    poliza = _buscar_poliza(numero_poliza) 
    if poliza is None:
        return {
            "error": "poliza_no_encontrada",
            "mensaje": f"No existe ninguna póliza con el número {numero_poliza}.",
        }
    else: 
        return poliza
    
#funcion interna
def _buscar_poliza(numero_poliza: str)-> Optional[dict]:
    with open(ruta_polizas, "r", encoding="utf-8") as f:
        polizas = json.load(f)
    for poliza in polizas:
        if poliza["numero_poliza"] == numero_poliza:
            return poliza
    return None

@mcp.tool(description=CONSULTAR_SINIESTRO_DOCSTRING)
def consultar_siniestro(numero_siniestro: str) -> dict:
  
    with open(ruta_siniestros, "r", encoding="utf-8") as f:
        siniestros = json.load(f)
    for siniestro in siniestros:
        if siniestro["numero_siniestro"] == numero_siniestro:
            return siniestro
    return {
        "error": "siniestro_no_encontrado",
        "mensaje": f"No existe ningún siniestro con el número {numero_siniestro}.",
    }


@mcp.tool(description=BUSCAR_EN_DOCUMENTACION_DOCSTRING)
def buscar_en_documentacion(query: str, producto: Optional[Literal["auto", "hogar", "salud","general"]] = None) -> list[str]:

    argumentos = {"query_texts": [query], "n_results": 3}
    if producto is not None:
        argumentos["where"] = {"producto": producto}

    resultado = collection.query(**argumentos)
    return resultado["documents"][0]



@mcp.tool(description=ABRIR_SINIESTRO_DOCSTRING)
def abrir_siniestro (numero_poliza: str, descripcion:str, fecha:str, importe_estimado:float) -> dict:

    # 1. Datos que faltan: si falta alguno, no se valida nada más
    datos = {
        "numero_poliza": numero_poliza,
        "descripcion": descripcion,
        "fecha": fecha,
        "importe_estimado": importe_estimado,
    }
    faltan = [campo for campo, valor in datos.items() if valor is None or valor == ""]
    if faltan:
        return {
            "error": "datos_incompletos",
            "faltan": faltan,
            "mensaje": "Faltan datos para abrir el siniestro: " + ", ".join(faltan) + ".",
        }

    # 2. Validaciones: se acumulan todos los errores
    errores = {}

    poliza = _buscar_poliza(numero_poliza)
    if poliza is None:
        errores["numero_poliza"] = f"No existe ninguna póliza con el número {numero_poliza}."
    elif poliza.get("estado") != "vigente":
        errores["numero_poliza"] = f"La póliza {numero_poliza} no está vigente."

    try:
        fecha_siniestro = date.fromisoformat(fecha)
        if fecha_siniestro > date.today():
            errores["fecha"] = "La fecha del siniestro no puede ser futura."
    except ValueError:
        errores["fecha"] = "La fecha no tiene un formato válido (AAAA-MM-DD)."

    if importe_estimado <= 0:
        errores["importe_estimado"] = "El importe estimado debe ser mayor que cero."

    if errores:
        return {
            "error": "datos_no_validos",
            "errores": errores,
        }

    # 3. Todo correcto: borrador pendiente de revisión (no se registra todavía)
    return {
        "estado": "pendiente_de_revision",
        "numero_poliza": numero_poliza,
        "producto": poliza.get("producto"),
        "descripcion": descripcion,
        "fecha": fecha,
        "importe_estimado": importe_estimado,
    }



# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")



