#las funciones de esta clase son funciones a las que el agente de 
#IA podrá acceder posteriormente 
import glob
import json
import chromadb

ruta_polizas = "./data/db/polizas_clientes.json"
ruta_siniestros = "./data/db/siniestros_historico.json"
#Como ya existe la base de datos persistente, cargamos el cliente aqui
collection = chromadb.PersistentClient(path="chroma_db/").get_collection(name="embeddings_collection")

def consultar_poliza(numero_poliza: str) -> dict:
        with open(ruta_polizas, "r", encoding="utf-8") as f:
            polizas = json.load(f)
        for poliza in polizas:
            if (poliza["numero_poliza"] == numero_poliza):
                return poliza
        return {
                "error": "poliza_no_encontrada",
                "mensaje": f"No existe ninguna póliza con el número {numero_poliza}.",
                }

def consultar_siniestro(numero_sinestro: str) -> dict:
    with open(ruta_siniestros, "r", encoding="utf-8") as f:
            siniestros = json.load(f)
    for siniestro in siniestros:
            if (siniestro["numero_siniestro"] == numero_sinestro):
                return siniestro
    return {
                "error": "siniestro_no_encontrado",
                "mensaje": f"No existe ningún siniestro con el número {numero_sinestro}.",
                }

def buscar_en_documentacion (query: str, producto: str) -> list[str]:
    resultado = collection.query(
        #Hace el embeding de la query
        #Hay otra opcion que es pasarle el embedding de la query, esto es interesante si queremos reutilizar 
        # la query en varias busquedas, ya que no tendria que volver a hacer el embedding de la query
        query_texts=[query], #le pasamos la lista de preguntas (en este caso solo hay una)       
        n_results=5,
        where={"producto": producto}
    )
    #Devuelve la respuesta a la query, como solo tenemos una solo devuelve la primera respuesta
    return resultado["documents"][0]

def abrir_siniestro ():
     return "abrir siniestro (To-Do)"


def marcar_fuera_de_dominio ():
    return "fuera_de_dominio"



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
