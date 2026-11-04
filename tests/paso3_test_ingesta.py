import os
from pathlib import Path

import chromadb
import pytest
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

RAIZ = Path(__file__).resolve().parents[1]
RUTA_CHROMA = RAIZ / "chroma_db"
NOMBRE_COLECCION = "embeddings_collection"
MODELO_EMBEDDINGS = os.getenv("EMBEDDING_MODEL", "qwen3-embedding:0.6b")


@pytest.fixture(scope="module")
def coleccion():
    """Abre la colección ya existente en disco, sin volver a ingerir."""
    cliente = chromadb.PersistentClient(path=str(RUTA_CHROMA))
    embedding_function = OllamaEmbeddingFunction(
        url="http://localhost:11434",
        model_name=MODELO_EMBEDDINGS,
    )
    return cliente.get_collection(
        name=NOMBRE_COLECCION,
        embedding_function=embedding_function,
    )


def test_indice_persistido_en_disco(coleccion):
    assert coleccion.count() > 0, "La colección está vacía: ejecuta antes src/ingest.py"


def test_busqueda_lunas_devuelve_chunk_de_auto(coleccion):
    resultado = coleccion.query(query_texts=["lunas"], n_results=3)

    texto = resultado["documents"][0][0]
    metadatos = resultado["metadatas"][0][0]

    assert metadatos["producto"] == "auto"
    assert "luna" in texto.lower()
    assert "seccion" in metadatos