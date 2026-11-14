#las funciones de esta clase son funciones a las que el agente de 
#IA podrá acceder posteriormente 
import json
import chromadb
from langchain.tools import tool
from typing import Optional,Literal
from datetime import date
from src.prompts.prompts  import BUSCAR_EN_DOCUMENTACION_DOCSTRING,CONSULTAR_POLIZA_DOCSTRING,CONSULTAR_SINIESTRO_DOCSTRING,ABRIR_SINIESTRO_DOCSTRING



ruta_polizas = "./data/db/polizas_clientes.json"
ruta_siniestros = "./data/db/siniestros_historico.json"
#Como ya existe la base de datos persistente, cargamos el cliente aqui
collection = chromadb.PersistentClient(path="chroma_db/").get_collection(name="embeddings_collection")

#@tool(parse_docstring=True) Como ya no usamos el literal dentro de la funcion se la pasamos de la siguiente forma
@tool(description=CONSULTAR_POLIZA_DOCSTRING)
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



@tool(description=CONSULTAR_SINIESTRO_DOCSTRING)
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


@tool(description=BUSCAR_EN_DOCUMENTACION_DOCSTRING)
def buscar_en_documentacion(query: str, producto: Optional[Literal["auto", "hogar", "salud","general"]] = None) -> list[str]:

    argumentos = {"query_texts": [query], "n_results": 5}
    if producto is not None:
        argumentos["where"] = {"producto": producto}

    resultado = collection.query(**argumentos)
    return resultado["documents"][0]

@tool(description=ABRIR_SINIESTRO_DOCSTRING)
def abrir_siniestro (numero_poliza: str, descripcion: str, fecha: str, importe_estimado: float) -> dict:

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











#Pruebas ------------------------------------------------------------------
#ctrl k + ctrl u para quitar comentarios 

if __name__ == "__main__":

    print ("Pruebas tools")
    # print(consultar_poliza("P-10023"))
    # print(consultar_poliza("P-10399"))
    # print (consultar_poliza("123"))

    # print("--------------------------------")

    # print(consultar_siniestro("S-5001"))
    # print(consultar_siniestro("S-5005"))
    # print(consultar_siniestro("456"))
