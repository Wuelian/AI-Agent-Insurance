from typing import TypedDict, Optional, List , Annotated

#--- Dejamos de usar operator para pasar a add_messages de langchain en el paso 5
#import operator
#aniadimos Annotated y usamos  
#operator.add para que se vayan aniadiendo los mensajes nuevos del estado

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    #Con reducer para guardar cada mensaje nuevo, add_messages esta hecho solo para mensajes
    messages: Annotated[List[AnyMessage], add_messages]
    intent: Optional[str]          # "consulta_cobertura" | "consulta_poliza" |
                                    # "consulta_siniestro" | "abrir_siniestro" |
                                    # "fuera_dominio" | "dentro_dominio" (sustituye a los anteriores)
    product_type: Optional[str]    # "auto" | "hogar" | "salud"
    policy_number: Optional[str]
    #claim_data: Optional[dict] #se usaba para coger los daton del siniestro, en nuestro caso no lo usamos
    retrieved_docs: Optional[List[str]]
    requires_human: bool
    queja_formal :  Optional[str] #queja formal del usuario
    tool_results: Optional[dict]   # sin reducer: cada turno sustituye al anterior
    interrupt_reason : Optional[str] #razon de la interrupcion
    documentacion_insuficiente : Optional[bool] #documentacion recogida del RAG insuficiente

