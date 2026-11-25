import asyncio
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from app.config import get_settings

SYSTEM = ("You are a polite support agent. Use tools to look up real data. Never guess. "
          "For refund requests, find the order with get_orders, then call refund_order.")
RISKY_TOOLS = {"refund_order"}

settings = get_settings()
llm = ChatOpenAI(model=settings.llm_model, api_key=settings.groq_api_key,
                 base_url="https://api.groq.com/openai/v1", temperature=0)

mcp_client = MultiServerMCPClient({
    "support": {"command": "python", "args": ["-m", "app.mcp_server.server"], "transport": "stdio"}
})


async def build_agent():
    tools = await mcp_client.get_tools()
    return create_react_agent(llm, tools, prompt=SYSTEM,
                              checkpointer=InMemorySaver(), interrupt_before=["tools"])


def ask_human(calls) -> bool:
    for call in calls:
        print(f"\n⚠️  Agent wants to run {call['name']} with {call['args']}")
    return input("Approve? (y/n): ").strip().lower() == "y"


async def chat(agent, text: str, thread_id: str = "demo") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    await agent.ainvoke({"messages": [("user", text)]}, config)

    while (state := await agent.aget_state(config)).next:
        calls = state.values["messages"][-1].tool_calls
        risky = [c for c in calls if c["name"] in RISKY_TOOLS]
        if risky and not ask_human(risky):
            rejected = [ToolMessage(content="Rejected by a human reviewer.", tool_call_id=c["id"])
                        for c in calls]
            await agent.aupdate_state(config, {"messages": rejected}, as_node="tools")
        await agent.ainvoke(None, config)

    return state.values["messages"][-1].content


async def main():
    agent = await build_agent()
    question = ("I'm aarav.shah@example.com. My Wireless Earbuds stopped working, "
                "please refund that order.")
    print(await chat(agent, question))


if __name__ == "__main__":
    asyncio.run(main())