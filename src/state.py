from typing import TypedDict, Optional, List , Annotated
import operator
#aniadimos Annotated y usamos  
#operator.add para que se vayan aniadiendo los mensajes nuevos del estado

class AgentState(TypedDict):
    messages: Annotated[List[dict], operator.add] 
    intent: Optional[str]          # "consulta_cobertura" | "consulta_poliza" |
                                    # "consulta_siniestro" | "abrir_siniestro" |
                                    # "fuera_dominio"
    product_type: Optional[str]    # "auto" | "hogar" | "salud"
    policy_number: Optional[str]
    claim_data: Optional[dict]
    retrieved_docs: Optional[List[str]]
    requires_human: bool


