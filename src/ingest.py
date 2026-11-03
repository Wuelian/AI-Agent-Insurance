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
#base de datos vectorial 
import chromadb
#Nos dice de separar por secciones, asi que usamos la siguiente libreria 
from langchain_text_splitters import MarkdownHeaderTextSplitter



#Base de datos vectorial ChromaDB
chroma_client = chromadb.Client()
#creacion de una colleccion de embeddings en la base de datos vectorial ChromaDB
collection = chroma_client.create_collection(name="embeddings_collection")

#ruta de los documentos en formato markdown
RUTA_DOCS = "./data/docs/*.md"

#modelo que usaremos para generar embeddings de los documentos
Model_embeding = "hf.co/Qwen/Qwen3-Embedding-0.6B-GGUF:latest"

#Headers que nos indican que seccion del documento es
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on,strip_headers=False)

#to-do markdown splitter se hace con la documentacion que
# tenemos guardada en formato markdown 
md_header_splits = markdown_splitter.split_text(markdown_document)
md_header_splits