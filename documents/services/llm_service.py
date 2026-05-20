from django.conf import settings


class LLMConfigurationError(Exception):
    """
    Raised when the LLM configuration is missing or invalid.
    """


def build_messages(question: str, context: str):
    """
    Build standard chat messages for the configured LLM provider.
    """
    system_prompt = (
        "You are a helpful document question-answering assistant. "
        "Answer the user's question only based on the provided document context. "
        "Answer in the same language as the user's question. "
        "If the answer is not available in the context, say: "
        "'The provided documents do not contain enough information to answer this question.' "
        "Do not invent information."
    )

    user_prompt = (
        f"Document context:\n{context}\n\n"
        f"User question:\n{question}\n\n"
        "Answer:"
    )

    return [
        ("system", system_prompt),
        ("user", user_prompt),
    ]


def generate_answer_from_context(question: str, context: str) -> str:
    """
    Generate an answer using the configured LLM provider.
    """
    provider = settings.LLM_PROVIDER

    if provider == "mock":
        return generate_answer_with_mock(question, context)

    if provider == "ollama":
        return generate_answer_with_ollama(question, context)

    if provider == "openrouter":
        return generate_answer_with_openrouter(question, context)

    raise LLMConfigurationError(
        f"Unsupported LLM provider: {provider}. Use 'mock', 'ollama', or 'openrouter'."
    )


def generate_answer_with_mock(question: str, context: str) -> str:
    """
    Generate a development-only answer without calling a real LLM.
    """
    if not context.strip():
        return "The provided documents do not contain enough information to answer this question."

    context_preview = context[:1200].strip()

    return (
        "Development mock answer: A real LLM provider is not configured yet. "
        "The system successfully retrieved relevant document context, and this answer is generated "
        "only for development testing.\n\n"
        "Retrieved context preview:\n"
        f"{context_preview}"
    )


def generate_answer_with_ollama(question: str, context: str) -> str:
    """
    Generate an answer using a local Ollama model.
    """
    try:
        from langchain_ollama import ChatOllama
    except ImportError as exc:
        raise LLMConfigurationError(
            "langchain-ollama is not installed. Install it with: pip install langchain-ollama"
        ) from exc

    if not settings.OLLAMA_MODEL:
        raise LLMConfigurationError(
            "OLLAMA_MODEL is missing. Please set OLLAMA_MODEL in the .env file."
        )

    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.2,
    )

    response = llm.invoke(build_messages(question, context))

    return response.content.strip()


def generate_answer_with_openrouter(question: str, context: str) -> str:
    """
    Generate an answer using OpenRouter.
    """
    try:
        from langchain_openrouter import ChatOpenRouter
    except ImportError as exc:
        raise LLMConfigurationError(
            "langchain-openrouter is not installed. Install it with: pip install langchain-openrouter"
        ) from exc

    if not settings.OPENROUTER_API_KEY:
        raise LLMConfigurationError(
            "OpenRouter API key is missing. Please set OPENROUTER_API_KEY in the .env file."
        )

    llm = ChatOpenRouter(
        api_key=settings.OPENROUTER_API_KEY,
        model=settings.OPENROUTER_MODEL,
        temperature=0.2,
        max_tokens=700,
    )

    response = llm.invoke(build_messages(question, context))

    return response.content.strip()