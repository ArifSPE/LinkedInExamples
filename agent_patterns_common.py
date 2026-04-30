from __future__ import annotations

import json
import time
from typing import Any, Iterable, Sequence

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

MODEL_NAME = "llama3.1:latest"
DEFAULT_RETRIES = 3


def get_local_llm(model: str = MODEL_NAME, temperature: float = 0) -> ChatOllama:
    return ChatOllama(model=model, temperature=temperature)


def build_checkpointer() -> MemorySaver:
    return MemorySaver()


def log_event(level: str, event_type: str, **metadata: Any) -> None:
    payload = {"level": level.upper(), "event_type": event_type, **metadata}
    print(json.dumps(payload, default=str))


def invoke_with_retry(llm: ChatOllama, prompt: str, retries: int = DEFAULT_RETRIES, delay: float = 1.0) -> str:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            log_event("info", "llm_invoke_start", attempt=attempt, prompt_preview=prompt[:80])
            response = llm.invoke(prompt)
            content = getattr(response, "content", response)
            log_event("info", "llm_invoke_success", attempt=attempt)
            return str(content)
        except Exception as error:  # noqa: BLE001
            last_error = error
            log_event("warning", "llm_invoke_retry", attempt=attempt, error=str(error))
            if attempt < retries:
                time.sleep(delay)
    assert last_error is not None
    raise last_error


def append_history(history: Sequence[str] | None, message: str) -> list[str]:
    items = list(history or [])
    items.append(message)
    return items


def parse_lines(raw_text: str) -> list[str]:
    items = []
    for line in raw_text.splitlines():
        cleaned = line.strip().lstrip("- ")
        if ". " in cleaned:
            cleaned = cleaned.split(". ", 1)[1]
        if cleaned:
            items.append(cleaned)
    return items


def choose_label(raw_label: str, valid_labels: Iterable[str], default: str) -> str:
    lowered = raw_label.strip().lower()
    for label in valid_labels:
        if label in lowered:
            return label
    return default


def render_state_graph(graph: Any, title: str = "State Graph") -> None:
    try:
        from IPython.display import Image, Markdown, display
    except Exception:  # noqa: BLE001
        Image = None
        Markdown = None
        display = None

    try:
        graph_obj = graph.get_graph()
    except Exception as error:  # noqa: BLE001
        log_event("warning", "state_graph_unavailable", error=str(error))
        print("State graph is unavailable for rendering.")
        return

    if display and Markdown:
        display(Markdown(f"### {title}"))

    if display and Image:
        try:
            png = graph_obj.draw_mermaid_png()
            display(Image(data=png))
            return
        except Exception as error:  # noqa: BLE001
            log_event("warning", "state_graph_png_fallback", error=str(error))

    try:
        mermaid = graph_obj.draw_mermaid()
        if display and Markdown:
            display(Markdown(f"```mermaid\n{mermaid}\n```"))
        else:
            print(mermaid)
        return
    except Exception as error:  # noqa: BLE001
        log_event("warning", "state_graph_mermaid_fallback", error=str(error))

    try:
        print(graph_obj.draw_ascii())
    except Exception as error:  # noqa: BLE001
        log_event("warning", "state_graph_ascii_failed", error=str(error))
