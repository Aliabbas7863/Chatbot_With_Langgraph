import os
import warnings
from typing import Annotated, TypedDict
from langgraph.checkpoint.memory import MemorySaver


from dotenv import load_dotenv

warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.",
    category=UserWarning,
)

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openrouter import ChatOpenRouter
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("open_Router_API_Key")
if not api_key:
    raise RuntimeError(
        "Set OPENROUTER_API_KEY or open_Router_API_Key in the .env file."
    )

llm = ChatOpenRouter(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    api_key=api_key,
)


class ChatState(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]


def chat_model(state: ChatState) -> ChatState:
    response = llm.invoke(state["message"])
    return {"message": [response]}

checkpointer=MemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat", chat_model)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

chatbot = graph.compile(checkpointer=checkpointer)

def run_cli() -> None:
    config = {"configurable": {"thread_id": "cli"}}

    while True:
        user_message = input("type your message: ")
        if user_message.strip().lower() in ["exit", "quit"]:
            break
        response = chatbot.invoke(
            {"message": [HumanMessage(content=user_message)]},
            config=config,
        )
        print("Ai: ", response["message"][-1].content)


if __name__ == "__main__":
    run_cli()
