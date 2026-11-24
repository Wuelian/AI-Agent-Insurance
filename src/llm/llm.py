from langchain_google_genai import ChatGoogleGenerativeAI
import truststore
truststore.inject_into_ssl()
from dotenv import load_dotenv

load_dotenv()

#llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0) La temperatura se ignora en este modelo 
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")# gemini-3.5-flash-lite
 
#Abajo para limitar las peticiones y la IA no salte  
# from langchain_core.rate_limiters import InMemoryRateLimiter

# limitador = InMemoryRateLimiter(
#     requests_per_second=0.2,     # 12 peticiones por minuto, por debajo de las 15 permitidas
#     check_every_n_seconds=0.1,
#     max_bucket_size=1,
# )

# llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", rate_limiter=limitador)