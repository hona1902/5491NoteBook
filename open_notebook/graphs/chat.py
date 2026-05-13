from typing import Annotated, Optional

from ai_prompter import Prompter
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from open_notebook.ai.provision import provision_langchain_model
from open_notebook.domain.notebook import Notebook
from open_notebook.exceptions import OpenNotebookError
from open_notebook.graphs.checkpoint import get_memory
from open_notebook.utils import clean_thinking_content
from open_notebook.utils.error_classifier import classify_error
from open_notebook.utils.text_utils import extract_text_content


class ThreadState(TypedDict):
    messages: Annotated[list, add_messages]
    notebook: Optional[Notebook]
    context: Optional[str]
    context_config: Optional[dict]
    model_override: Optional[str]


async def acall_model_with_messages(state: ThreadState, config: RunnableConfig) -> dict:
    """Async graph node — provisions AI model and invokes it.

    Runs entirely on FastAPI's main event loop.  No secondary event loops
    or ThreadPoolExecutor hacks are needed.
    """
    try:
        system_prompt = Prompter(prompt_template="chat/system").render(data=state)  # type: ignore[arg-type]
        payload = [SystemMessage(content=system_prompt)] + state.get("messages", [])
        model_id = config.get("configurable", {}).get("model_id") or state.get(
            "model_override"
        )

        # Provision model — already async, just await directly
        model = await provision_langchain_model(
            str(payload), model_id, "chat", max_tokens=8192
        )

        # Use async invoke so the HTTP call to the AI provider doesn't block
        ai_message = await model.ainvoke(payload)

        # Clean thinking content from AI response (e.g., <think>...</think> tags)
        content = extract_text_content(ai_message.content)
        cleaned_content = clean_thinking_content(content)
        cleaned_message = ai_message.model_copy(update={"content": cleaned_content})

        return {"messages": cleaned_message}
    except OpenNotebookError:
        raise
    except Exception as e:
        error_class, user_message = classify_error(e)
        raise error_class(user_message) from e


async def _build_graph():
    """Build and return the compiled graph with async checkpointer."""
    memory = await get_memory()
    agent_state = StateGraph(ThreadState)
    agent_state.add_node("agent", acall_model_with_messages)
    agent_state.add_edge(START, "agent")
    agent_state.add_edge("agent", END)
    return agent_state.compile(checkpointer=memory)


# Lazy singleton — initialised on first await of get_chat_graph()
_graph = None


async def get_chat_graph():
    """Return the compiled chat graph (lazy async init)."""
    global _graph
    if _graph is None:
        _graph = await _build_graph()
    return _graph
