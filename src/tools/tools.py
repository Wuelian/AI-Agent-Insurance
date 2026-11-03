
import glob
import json

ruta_polizas = "./data/db/polizas_clientes.json"
ruta_siniestros = "./data/db/siniestros_historico.json"

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



if __name__ == "__main__":
    print(consultar_poliza("P-10023"))
    print(consultar_poliza("P-10399"))
    print (consultar_poliza("123"))

    print("--------------------------------")

    print(consultar_siniestro("S-5001"))
    print(consultar_siniestro("S-5005"))
    print(consultar_siniestro("456"))

