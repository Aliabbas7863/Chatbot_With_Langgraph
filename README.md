# Basic LangGraph Chatbot

A small Python chatbot application powered by LangGraph, LangChain, and
OpenRouter. The project provides two interfaces:

- A browser-based chat interface built with Streamlit.
- An interactive command-line interface for terminal use.

The chatbot sends messages to the OpenRouter API through
`langchain-openrouter` and maintains conversation state with LangGraph's
in-memory checkpointer.

## Features

- Chat with an OpenRouter-hosted language model.
- Streamlit chat interface with user and assistant message history.
- Command-line chat interface.
- LangGraph state management.
- In-memory conversation checkpointing.
- Configurable model and API key through environment variables.
- Separate frontend and backend responsibilities.

## Project Structure

```text
chatbot/
├── Basic_chabot.py          # Chatbot backend and command-line interface
├── streamlit_frontend.py    # Streamlit browser interface
├── requirements.txt         # Python dependencies
├── .env                     # Local environment variables; do not commit
├── .vscode/
│   └── settings.json        # Workspace Python interpreter configuration
├── venv/                    # Local virtual environment
└── README.md                # Project documentation
```

> The `venv/` directory is generated locally and should not be copied between
> machines. Create a new virtual environment when setting up the project on a
> different computer.

## Architecture

```text
User
 │
 ├── Streamlit browser UI
 │       │
 │       └── streamlit_frontend.py
 │                   │
 └── Terminal CLI ───┘
                     │
                     ▼
             Basic_chabot.py
                     │
                     ▼
                 LangGraph
                     │
                     ▼
              ChatOpenRouter
                     │
                     ▼
                OpenRouter API
```

### Backend flow

1. `Basic_chabot.py` loads environment variables from `.env`.
2. It creates a `ChatOpenRouter` model client.
3. A LangGraph state graph receives the conversation messages.
4. The `chat_model` node sends the messages to the configured model.
5. The model response is added to the graph state.
6. `MemorySaver` stores state in memory for the configured thread.

### Frontend flow

1. Streamlit imports the compiled `chatbot` graph.
2. The frontend stores displayed messages in `st.session_state`.
3. The user submits a message through `st.chat_input`.
4. The message is sent to the backend graph using the `streamlit` thread.
5. The assistant response is displayed in the chat window.

## Requirements

- Python 3.10 or newer is recommended.
- An OpenRouter account and API key.
- Internet access for requests to OpenRouter.
- The dependencies listed in `requirements.txt`.

The project has been configured to use a local virtual environment at
`venv/`. The exact Python version can depend on the machine and environment
manager being used.

## Installation

### 1. Open the project directory

```bash
cd /home/ali-abbas/Desktop/chatbot
```

For another machine, replace the path with the directory where the project was
downloaded.

### 2. Create a virtual environment

Linux and macOS:

```bash
python3 -m venv venv
```

Windows PowerShell:

```powershell
py -m venv venv
```

### 3. Activate the virtual environment

Linux and macOS:

```bash
source venv/bin/activate
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install streamlit
```

If Streamlit is added to `requirements.txt` in the future, the final command
is not necessary. It is currently shown separately because the checked-in
requirements file contains the LangChain and LangGraph dependencies only.

## Configuration

Create a `.env` file in the project root. Do not share this file or commit it
to source control.

Recommended configuration:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini
```

### Environment variables

| Variable | Required | Default | Description |
|---|---:|---|---|
| `OPENROUTER_API_KEY` | Yes | None | API key used to authenticate with OpenRouter. |
| `OPENROUTER_MODEL` | No | `openai/gpt-4o-mini` | OpenRouter model identifier. |

The backend also accepts the legacy variable name
`open_Router_API_Key`, but `OPENROUTER_API_KEY` is recommended because it is
consistent with common environment-variable conventions.

### API key security

- Never place an API key directly in Python source code.
- Never commit `.env` to a public or shared repository.
- If an API key has been exposed, revoke it and create a replacement key.
- Restrict API key permissions and spending limits in the OpenRouter dashboard
  when possible.

## Running the Streamlit Application

From the project directory, with the virtual environment activated, run:

```bash
streamlit run streamlit_frontend.py
```

Or use the project environment directly without activating it:

```bash
/home/ali-abbas/Desktop/chatbot/venv/bin/streamlit run \
  /home/ali-abbas/Desktop/chatbot/streamlit_frontend.py
```

Streamlit normally opens the application automatically. If it does not, open:

```text
http://localhost:8501
```

To run on a different port:

```bash
streamlit run streamlit_frontend.py --server.port 8502
```

To run without opening a browser:

```bash
streamlit run streamlit_frontend.py --server.headless true
```

## Running the Command-Line Interface

Run the backend directly:

```bash
python Basic_chabot.py
```

The terminal displays a prompt:

```text
type your message:
```

Enter a message to receive a response. Enter `exit` or `quit` to stop the
program.

## Using the Application

1. Configure a valid OpenRouter API key.
2. Start the Streamlit application.
3. Enter a message in the chat box.
4. Press Enter to submit it.
5. Continue the conversation using the same browser session.

The displayed message history is stored in Streamlit session state. The
LangGraph checkpointer is in-memory, so conversation data is lost when the
application process restarts.

## Dependency Overview

The main dependencies are:

| Package | Purpose |
|---|---|
| `langgraph` | Builds and executes the chatbot state graph. |
| `langchain-core` | Provides message types and core LangChain abstractions. |
| `langchain-openrouter` | Connects LangChain to OpenRouter-hosted models. |
| `python-dotenv` | Loads configuration from the `.env` file. |
| `streamlit` | Provides the browser-based chat interface. |

## Backend API in This Project

The backend exposes the compiled graph as the module-level variable
`chatbot`. The frontend invokes it with a LangChain human message:

```python
from langchain_core.messages import HumanMessage
from Basic_chabot import chatbot

response = chatbot.invoke(
    {"message": [HumanMessage(content="Hello")]},
    config={"configurable": {"thread_id": "streamlit"}},
)

assistant_text = response["message"][-1].content
```

The graph state is defined as:

```python
class ChatState(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]
```

The `thread_id` identifies a conversation checkpoint. The current application
uses `streamlit` for the web interface and `cli` for the terminal interface.

## Troubleshooting

### `ModuleNotFoundError: No module named 'streamlit'`

Install Streamlit in the same environment used to run the application:

```bash
python -m pip install streamlit
```

If the project uses its local environment:

```bash
/home/ali-abbas/Desktop/chatbot/venv/bin/python -m pip install streamlit
```

### `ModuleNotFoundError: No module named 'Basic_chatbot'`

The backend file is named `Basic_chabot.py` (with `chabot`, not `chatbot`).
Run Streamlit from the project root so Python can import the backend:

```bash
cd /home/ali-abbas/Desktop/chatbot
streamlit run streamlit_frontend.py
```

### `Set OPENROUTER_API_KEY ... in the .env file`

Create or update `.env` in the project root:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
```

Restart Streamlit after changing environment variables.

### OpenRouter authentication or request errors

Check the following:

- The API key is valid and has not been revoked.
- The account has sufficient credits or an available payment method.
- The model name is supported by OpenRouter.
- The machine has internet access.
- The `.env` file has no extra quotes or accidental spaces.

You can select a different model with:

```dotenv
OPENROUTER_MODEL=your-provider/your-model
```

### Port `8501` is already in use

Start Streamlit on another port:

```bash
streamlit run streamlit_frontend.py --server.port 8502
```

Then open `http://localhost:8502`.

### Conversation history disappears

This project uses in-memory storage. History is cleared when the Streamlit
session or Python process restarts. Persistent history would require a
database or another durable LangGraph checkpointer.

### Python or dependency compatibility warnings

Use the project's virtual environment and reinstall dependencies:

```bash
python -m pip install --upgrade -r requirements.txt
```

If dependency resolution fails, use a supported Python version such as Python
3.11 or Python 3.12 and create a fresh virtual environment.

## Development Checks

Check Python syntax before running the application:

```bash
python -m py_compile Basic_chabot.py streamlit_frontend.py
```

Verify that the backend can be imported without starting the terminal loop:

```bash
python -c "import Basic_chabot; print('backend import ok')"
```

Start Streamlit and confirm that it responds at `http://localhost:8501`.

## Limitations and Future Improvements

The current project is intentionally minimal. Possible future improvements
include:

- Add `streamlit` to `requirements.txt`.
- Add a `.gitignore` for `.env`, `venv/`, caches, and local files.
- Add user-selectable models and generation settings.
- Add explicit error messages for failed API requests.
- Add a clear-chat button.
- Use a unique thread ID per browser session.
- Persist conversations in a database or durable LangGraph checkpointer.
- Add automated tests for graph invocation and frontend integration.
- Add streaming token responses for a more interactive experience.
- Add input validation, rate limiting, and usage monitoring for deployment.
- Add deployment instructions for Streamlit Community Cloud or another host.

## License

No license has been specified for this project. Add a license file before
distributing the project or publishing it as open source.
