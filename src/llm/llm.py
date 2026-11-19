from langchain_google_genai import ChatGoogleGenerativeAI
import truststore
truststore.inject_into_ssl()
from dotenv import load_dotenv

load_dotenv()

#llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0) La temperatura se ignora en este modelo 
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")