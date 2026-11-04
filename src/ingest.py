from glob import glob
import os 
import json
import numpy as np
from google import genai
from dotenv import load_dotenv
#modelo de lenguaje local
import ollama
#configuracion de certificados SSL para poder usar la API de Ollama y Gemini en Windows
import truststore
truststore.inject_into_ssl()
#Nos dice de separar por secciones, asi que usamos la siguiente libreria 
from langchain_text_splitters import MarkdownHeaderTextSplitter

#base de datos vectorial 
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction



#ruta de los documentos en formato markdown
RUTA_DOCS = "./data/docs/*.md"

#modelo que usaremos para generar embeddings de los documentos
Model_embeding = "qwen3-embedding:0.6b" 
# Model_embeding = "hf.co/Qwen/Qwen3-Embedding-0.6B-GGUF:latest"

#Base de datos vectorial ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db/")
#creacion de una colleccion de embeddings en la base de datos vectorial ChromaDB
collection = chroma_client.create_collection(
    name="embeddings_collection",
    embedding_function = OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name=Model_embeding,
        )
    )

#Headers que nos indican que seccion del documento es
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "seccion"),
    ("###", "Header 3"),
]
tipo_producto = ["auto", "hogar", "salud", "general"]
    

def get_metadato_producto(nombre_archivo):
    # Extraer el nombre del archivo sin la ruta y la extensión
    nombre_archivo_sin_extension = os.path.splitext(os.path.basename(nombre_archivo))[0]
    archivo_sin_prefix = nombre_archivo_sin_extension.removeprefix("condiciones_generales_")
    if archivo_sin_prefix in tipo_producto:
        return archivo_sin_prefix
    else: 
        return "general"


def add_documents_to_chroma_db(chunks):
    #añadir los elementos a la base de datos vectorial ChromaDB
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    documents = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    #se le pasan las listas de datos a bbdd vectorial ChromaDB para que los guarde
    collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on,strip_headers=False)

#to-do markdown splitter se hace con la documentacion que
# tenemos guardada en formato markdown 

files_dot_md = glob("./data/docs/*.md")

chunks = []
if collection.count() == 0 :
    for markdown_document in files_dot_md:
        with open(markdown_document, "r", encoding="utf-8") as f:
            contenido = f.read()
            md_header_splits = markdown_splitter.split_text(contenido)
            #guardar metadato producto 
            metadato = get_metadato_producto(markdown_document)
            for i in range(len(md_header_splits)):
                md_header_splits[i].metadata["producto"] = metadato
            
            #aniade 1 a 1 los elementos dentro de la lista
            chunks.extend(md_header_splits)

    #introducir los elementos dentro de la base de datos 
    add_documents_to_chroma_db(chunks)

# --- Comprobación rápida de la ingesta ---
print("Total de chunks:", collection.count())

resultado = collection.query(query_texts=["lunas"], n_results=3)

for texto, metadatos, distancia in zip(
    resultado["documents"][0],
    resultado["metadatas"][0],
    resultado["distances"][0],
):
    print("=" * 60)
    print("Distancia:", round(distancia, 3))
    print("Metadatos:", metadatos)
    print(texto)