from langchain.mcp import MCPAdapter

from pathlib import Path

import asyncio
from src.llm.llm import llm 

# A script path is launched over stdio, one subprocess per adapter.
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_SERVIDOR = RAIZ_PROYECTO / "mcp_servers" / "policy_server" / "server.py"
stdio = MCPAdapter(Path(RUTA_SERVIDOR))


async def get_mcp_tools():
    async with stdio as adapter:
        tools = await adapter.list_tools()
        return  tools

tools = asyncio.run(get_mcp_tools())



async def probar():
    tools = await get_mcp_tools()
    print("Tools disponibles:", [t.name for t in tools])

    tools_por_nombre = {t.name: t for t in tools}
    tool = tools_por_nombre["consultar_poliza"]

    # Igual que hará el router: ainvoke con el diccionario de argumentos
    resultado = await tool.ainvoke({"numero_poliza": "P-10023"})

    print("Tipo:", type(resultado))
    print("Contenido:", resultado)


if __name__ == "__main__":
    asyncio.run(probar())