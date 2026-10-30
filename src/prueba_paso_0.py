import langgraph
import langchain
import langchain_core
import chromadb
import langchain_chroma
import pydantic
import dotenv 
import glob


files_dot_md = glob.glob("./data/docs/*.md")
for doc in files_dot_md:
    print(f"Found markdown file: {doc}")
    with open(doc, "r", encoding="utf-8") as f:
        contenido = f.read()
        print(contenido)
        print ("----------------------------------------")
        
files_json = glob.glob("./data/db/*.json")
for doc in files_json:
    print(f"Found JSON file: {doc}")
    with open(doc, "r", encoding="utf-8") as f:
            contenido = f.read()
    
            print(contenido)
            print ("----------------------------------------")


print("All modules imported successfully!")