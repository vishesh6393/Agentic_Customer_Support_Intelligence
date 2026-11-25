import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from app.config import get_settings

SYSTEM = "You are a polite support agent. Use tools to look up real data. Never guess."

settings = get_settings()
llm = ChatOpenAI(model=settings.llm_model, api_key=settings.groq_api_key,
                 base_url="https://api.groq.com/openai/v1", temperature=0)

mcp_client = MultiServerMCPClient({
    "support": {"command": "python", "args": ["-m", "app.mcp_server.server"], "transport": "stdio"}
})


async def build_agent():
    tools = await mcp_client.get_tools()
    return create_react_agent(llm, tools, prompt=SYSTEM)


async def main():
    agent = await build_agent()
    question = "Hi, my email is aarav.shah@example.com. I want to cancel my order wireless earbuds and want refund?"
    result = await agent.ainvoke({"messages": [("user", question)]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())