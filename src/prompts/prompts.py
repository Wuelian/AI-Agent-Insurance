
#------------------------------ Prompts para el nodo Router ------------------------------

ROUTER_SYSTEM_PROMPT = """Eres AsegurIA, el asistente virtual de Seguros Horizonte.
Atiendes consultas de clientes sobre sus seguros de auto, hogar y salud.

Tu tarea es entender qué necesita el cliente y obtener la información
necesaria con las herramientas disponibles:
- Para dudas sobre coberturas, exclusiones, carencias, franquicias, plazos
  o trámites, usa buscar_en_documentacion.
- Para los datos o el estado de una póliza concreta, usa consultar_poliza.
- Para el estado de un siniestro ya abierto, usa consultar_siniestro.

Reglas:
1. No inventes datos de pólizas, siniestros, coberturas, importes ni plazos.
   Toda la información debe salir de las herramientas.
2. Si para usar una herramienta te falta un dato (por ejemplo, el número de
   póliza o de siniestro), no lo supongas: pídeselo al cliente.
3. Si una herramienta devuelve un error (por ejemplo, una póliza que no
   existe), no lo ocultes ni lo sustituyas por datos inventados.
4. Si la consulta no tiene relación con seguros, no uses ninguna herramienta.
5. Al terminar, clasifica la consulta del cliente según el formato de
   respuesta indicado.
"""

INTENT_DESCRIPTION = """Clasifica el mensaje del cliente según su TEMA, no según si has usado herramientas.
REGLA PRINCIPAL: si el mensaje contiene varias consultas y AL MENOS UNA trata de seguros, clasifícalo como dentro_dominio, aunque el resto no tenga relación con seguros.

- dentro_dominio: alguna parte del mensaje trata de:
  1. Dudas generales sobre qué cubre o no un seguro: coberturas, exclusiones, carencias, franquicias, plazos o trámites.
  2. Los datos o el estado de una póliza concreta del cliente.
  3. El estado de un siniestro que ya existe.
  4. Un daño o incidente que el cliente ha sufrido y quiere declarar, aunque también pregunte qué hacer o si está cubierto.
  También es dentro_dominio si es una consulta de seguros a la que le falta un dato (por ejemplo, el número de póliza), o un saludo o agradecimiento.

- fuera_dominio: NINGUNA parte del mensaje trata de seguros (por ejemplo, solo pregunta por el tiempo, deportes o recetas).

Ejemplo: 'Quiero abrir un siniestro por un accidente. ¿Qué tiempo hace hoy?' es dentro_dominio."""


#------------------------------ Prompts para la clase tools ------------------------------

CONSULTAR_POLIZA_DOCSTRING =  """Consulta los datos de una póliza concreta de un cliente: titular,
producto contratado, coberturas, vigencia y estado.

Úsala cuando el cliente pregunte por el estado o los datos de SU póliza
y proporcione su número. No la uses para dudas generales sobre qué
cubre un tipo de seguro: para eso está buscar_en_documentacion.

Args:
    numero_poliza: Número de póliza tal como lo indica el cliente,
        con el formato "P-" seguido de cifras (por ejemplo, "P-10023").

Returns:
    Los datos de la póliza, o un diccionario con la clave "error" si no
    existe ninguna póliza con ese número.
""" 

CONSULTAR_SINIESTRO_DOCSTRING = """Consulta el estado y los datos de un siniestro ya abierto.

Úsala cuando el cliente pregunte cómo va un siniestro existente y
proporcione su número. No la uses para abrir un siniestro nuevo.

Args:
    numero_siniestro: Número de siniestro tal como lo indica el cliente,
        con el formato "S-" seguido de cifras (por ejemplo, "S-5001").

Returns:
    Los datos del siniestro, o un diccionario con la clave "error" si no
    existe ningún siniestro con ese número.
"""
BUSCAR_EN_DOCUMENTACION_DOCSTRING ="""Busca en la documentación oficial de Seguros Horizonte (condiciones
generales y preguntas frecuentes) los fragmentos que responden a una
duda sobre coberturas, exclusiones, carencias, franquicias, plazos o
trámites.

Úsala para preguntas generales sobre qué cubre o no cubre un seguro, o
sobre cómo hacer un trámite. No la uses para consultar los datos de
una póliza o un siniestro concretos.

Args:
    query: Lo esencial de la duda del cliente, en pocas palabras
        (por ejemplo, "rotura de lunas" o "cirugía estética").
    producto: Seguro al que se refiere la pregunta: "auto", "hogar" o
        "salud". Déjalo vacío si el cliente no indica de qué seguro habla.

Returns:
    Lista de fragmentos de la documentación relacionados con la consulta.
"""


ABRIR_SINIESTRO_DOCSTRING = """Valida y prepara la apertura de un siniestro nuevo.

Úsala en cuanto el cliente quiera declarar un daño o incidente, aunque
todavía no haya dado todos los datos. Pasa solo los datos que el cliente
haya proporcionado explícitamente y deja vacíos los demás: nunca inventes
ni supongas un valor. La herramienta indicará qué datos faltan o no son
válidos para que se los pidas al cliente.

El siniestro debe estar ligado a una póliza existente y vigente, y la
fecha en la que ocurrió no puede ser futura.

No la uses para consultar un siniestro que ya existe: para eso está
consultar_siniestro.

Args:
    numero_poliza: Número de póliza tal como lo indica el cliente, con el
        formato "P-" seguido de cifras (por ejemplo, "P-10023").
    descripcion: Descripción breve de lo ocurrido, con las palabras del
        cliente (por ejemplo, "rotura de una tubería en la cocina").
    fecha: Fecha en la que ocurrió el siniestro (no la fecha de hoy), en
        formato AAAA-MM-DD. Si el cliente la indica de otra forma,
        conviértela a este formato solo si no hay ambigüedad; si la hay,
        déjala vacía.
    importe_estimado: Importe estimado de los daños en euros, como número
        (por ejemplo, 8000.0).

Returns:
    Si todos los datos están completos y son válidos, un borrador del
    siniestro pendiente de revisión (todavía no queda registrado). Si
    falta algún dato, un diccionario con la clave "error" y la lista de
    datos que faltan en "faltan". Si algún dato no es válido (por ejemplo,
    una póliza inexistente o no vigente, o una fecha futura), un
    diccionario con la clave "error" y el motivo de cada dato no válido.
"""