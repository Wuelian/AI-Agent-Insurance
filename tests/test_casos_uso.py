# tests/test_casos_uso.py
import uuid
import pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from src.graph import init_grafo_paso_8
from src.tools.tools import _buscar_poliza


# ---------------------------------------------------------------- utilidades
@pytest.fixture(scope="module")
def grafo():
    # InMemorySaver: cada ejecución de los tests empieza limpia (sin arrastrar estado de SQLite)
    return init_grafo_paso_8(InMemorySaver())


def ejecutar(grafo, mensaje, resume="derivado"):
    """Ejecuta un turno completo. Si hay interrupt, simula al humano y reanuda.
    Devuelve (resultado_primer_invoke, resultado_final, se_pauso)."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}   # hilo nuevo por test
    primero = grafo.invoke({"messages": [HumanMessage(content=mensaje)]}, config)
    pausado = "__interrupt__" in primero
    final = grafo.invoke(Command(resume=resume), config) if pausado else primero
    return primero, final, pausado


def texto_respuesta(resultado):
    return resultado["messages"][-1].content.lower()


# ---------------------------------------------------------------- historias de usuario
def test_us1_cobertura_lunas_auto(grafo):
    _, final, pausado = ejecutar(grafo, "¿Mi seguro de auto cubre lunas?")
    respuesta = texto_respuesta(final)

    assert not pausado
    assert final["intent"] == "dentro_dominio"
    assert final["product_type"] == "auto"
    assert "buscar_en_documentacion" in final["tool_results"]     # ha usado el RAG
    assert "luna" in respuesta
    assert "secci" in respuesta                                    # cita la fuente (sección)


def test_us2_estado_poliza(grafo):
    _, final, pausado = ejecutar(grafo, "Quiero saber el estado de mi póliza P-10023")
    datos_tool = final["tool_results"].get("consultar_poliza")

    assert not pausado
    assert final["intent"] == "dentro_dominio"
    assert datos_tool == _buscar_poliza("P-10023")                 # datos reales del dataset
    assert "p-10023" in texto_respuesta(final)


def test_us3_tuberia_rota_flujo_guiado(grafo):
    _, final, pausado = ejecutar(grafo, "Se me ha roto una tubería en casa, ¿qué hago?")
    respuesta = texto_respuesta(final)
    siniestro = final["tool_results"].get("abrir_siniestro")

    assert not pausado
    assert final["product_type"] == "hogar"
    assert "buscar_en_documentacion" in final["tool_results"]     # RAG
    # Inicio del flujo guiado: o la tool detecta datos incompletos, o la respuesta los pide
    assert (siniestro is not None and siniestro.get("error") == "datos_incompletos") \
        or "póliza" in respuesta
    assert "pendiente_de_revision" not in str(final["tool_results"])   # no abre nada sin datos


def test_us4_siniestro_8000_deriva_a_humano(grafo):
    mensaje = ("Quiero declarar un siniestro. El 10 de noviembre de 2026 tuve un accidente con el coche: "
               "choqué contra un muro al aparcar y se ha destrozado todo el frontal. Mi póliza es la "
               "P-10023 y el taller calcula unos 8.000 € de reparación.")
    primero, final, pausado = ejecutar(grafo, mensaje)
    siniestro = final["tool_results"].get("abrir_siniestro")

    assert pausado                                                 # human-in-the-loop
    assert primero["__interrupt__"][0].value                       # lleva el motivo
    assert final["requires_human"] is True
    assert "importe" in final["interrupt_reason"].lower()
    assert siniestro["estado"] == "pendiente_de_revision"
    assert siniestro["importe_estimado"] == 8000


def test_us5_cirugia_estetica_exclusion(grafo):
    _, final, pausado = ejecutar(grafo, "¿Cubre mi seguro de salud una cirugía estética?")
    respuesta = texto_respuesta(final)

    assert not pausado
    assert final["product_type"] == "salud"
    assert "buscar_en_documentacion" in final["tool_results"]
    assert any(p in respuesta for p in ("exclu", "no cubre", "no está cubierta", "no está cubierto"))


def test_us6_fuera_de_dominio(grafo):
    _, final, pausado = ejecutar(grafo, "¿qué tiempo hace hoy?")

    assert not pausado
    assert final["intent"] == "fuera_dominio"
    assert not final["tool_results"]                               # no consulta nada
    assert not final.get("requires_human")                         # no pasa por las reglas
    assert "fuera de mi dominio" in texto_respuesta(final)


def test_us7_datos_insuficientes_siniestro(grafo):
    _, final, pausado = ejecutar(grafo, "Quiero abrir un siniestro, ayer tuve un accidente con el coche.")
    respuesta = texto_respuesta(final)
    siniestro = final["tool_results"].get("abrir_siniestro")

    assert not pausado
    # No asume valores: o la tool devuelve datos_incompletos, o no se llama
    assert siniestro is None or siniestro.get("error") == "datos_incompletos"
    assert "pendiente_de_revision" not in str(final["tool_results"])
    assert any(p in respuesta for p in ("póliza", "importe", "fecha"))   # pregunta por lo que falta