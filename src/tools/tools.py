#las funciones de esta clase son funciones a las que el agente de 
#IA podrá acceder posteriormente 
import glob
import json
import chromadb
from langchain.tools import tool


ruta_polizas = "./data/db/polizas_clientes.json"
ruta_siniestros = "./data/db/siniestros_historico.json"
#Como ya existe la base de datos persistente, cargamos el cliente aqui
collection = chromadb.PersistentClient(path="chroma_db/").get_collection(name="embeddings_collection")

@tool(parse_docstring=True)
def consultar_poliza(numero_poliza: str) -> dict:
    """Consulta los datos de una póliza concreta de un cliente: titular,
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
    with open(ruta_polizas, "r", encoding="utf-8") as f:
        polizas = json.load(f)
    for poliza in polizas:
        if poliza["numero_poliza"] == numero_poliza:
            return poliza
    return {
        "error": "poliza_no_encontrada",
        "mensaje": f"No existe ninguna póliza con el número {numero_poliza}.",
    }


@tool(parse_docstring=True)
def consultar_siniestro(numero_siniestro: str) -> dict:
    """Consulta el estado y los datos de un siniestro ya abierto.

    Úsala cuando el cliente pregunte cómo va un siniestro existente y
    proporcione su número. No la uses para abrir un siniestro nuevo.

    Args:
        numero_siniestro: Número de siniestro tal como lo indica el cliente,
            con el formato "S-" seguido de cifras (por ejemplo, "S-5001").

    Returns:
        Los datos del siniestro, o un diccionario con la clave "error" si no
        existe ningún siniestro con ese número.
    """
    with open(ruta_siniestros, "r", encoding="utf-8") as f:
        siniestros = json.load(f)
    for siniestro in siniestros:
        if siniestro["numero_siniestro"] == numero_siniestro:
            return siniestro
    return {
        "error": "siniestro_no_encontrado",
        "mensaje": f"No existe ningún siniestro con el número {numero_siniestro}.",
    }


@tool(parse_docstring=True)
def buscar_en_documentacion(query: str, producto: Optional[str] = None) -> list[str]:
    """Busca en la documentación oficial de Seguros Horizonte (condiciones
    generales y preguntas frecuentes) los fragmentos que responden a una
    duda sobre coberturas, exclusiones, carencias, franquicias, plazos o
    trámites.

    Úsala para preguntas generales sobre qué cubre o no cubre un seguro, o
    sobre cómo hacer un trámite. No la uses para consultar los datos de
    una póliza o un siniestro concretos.

    Args:
        query: Lo esencial de la duda del cliente, en pocas palabras
            (por ejemplo, "rotura de lunas" o "cirugía estética").
        producto: Seguro al que se refiere la pregunta: "auto", "hogar" o
            "salud". Déjalo vacío si el cliente no indica de qué seguro habla.

    Returns:
        Lista de fragmentos de la documentación relacionados con la consulta.
    """
    argumentos = {"query_texts": [query], "n_results": 5}
    if producto is not None:
        argumentos["where"] = {"producto": producto}

    resultado = collection.query(**argumentos)
    return resultado["documents"][0]
@tool
def abrir_siniestro ():
     return "abrir siniestro (To-Do)"




#Pruebas ------------------------------------------------------------------
#ctrl k + ctrl u para quitar comentarios 

if __name__ == "__main__":
    print(consultar_poliza("P-10023"))
    print(consultar_poliza("P-10399"))
    print (consultar_poliza("123"))

    print("--------------------------------")

    print(consultar_siniestro("S-5001"))
    print(consultar_siniestro("S-5005"))
    print(consultar_siniestro("456"))
