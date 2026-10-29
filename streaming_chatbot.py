import os
import warnings
from typing import Annotated, Iterator, TypedDict

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.",
    category=UserWarning,
)

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("open_Router_API_Key")
if not api_key:
    st.error("Set OPENROUTER_API_KEY or open_Router_API_Key in the .env file.")
    st.stop()


class ChatState(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]


llm = ChatOpenRouter(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    api_key=api_key,
    streaming=True,
)


def chat_model(state: ChatState) -> ChatState:
    response = llm.invoke(state["message"])
    return {"message": [response]}


graph = StateGraph(ChatState)
graph.add_node("chat", chat_model)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)
chatbot = graph.compile(checkpointer=MemorySaver())


def stream_response(user_input: str) -> Iterator[str]:
    config = {"configurable": {"thread_id": "streamlit"}}
    for message_chunk, metadata in chatbot.stream(
        {"message": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode="messages",
    ):
        if metadata.get("langgraph_node") != "chat":
            continue
        if isinstance(message_chunk.content, str) and message_chunk.content:
            yield message_chunk.content


st.title("AI Chatbot with Streaming")

if "message_history" not in st.session_state:
    st.session_state.message_history = []

for message in st.session_state.message_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message here...")
if user_input:
    st.session_state.message_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = st.write_stream(stream_response(user_input))

    st.session_state.message_history.append(
        {"role": "assistant", "content": response}
    )
