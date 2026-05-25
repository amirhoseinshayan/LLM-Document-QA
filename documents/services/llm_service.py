from dataclasses import dataclass

import httpx
from django.conf import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


class LLMServiceError(Exception):
    """
    Raised when the configured LLM provider cannot generate an answer.
    """


class LLMConfigurationError(LLMServiceError):
    """
    Backward-compatible error used by older API views.
    """


@dataclass
class LLMGenerationResult:
    """
    Result returned by the LLM service.
    """

    answer: str
    provider: str
    model: str
    used_fallback: bool = False


def build_system_prompt() -> str:
    """
    Build the system prompt used for document-grounded question answering.
    """
    return (
        "You are a careful document question-answering assistant. "
        "You must answer only using the provided document context. "
        "Answer in the same language as the user's question. "
        "If the user asks for something that is not clearly supported by the context, "
        "say that the provided documents do not contain enough information to answer. "
        "Do not recommend products, books, resources, or external information unless they are explicitly mentioned in the context. "
        "Do not invent facts. "
        "Keep the answer clear, concise, and grounded in the retrieved context."
    )


def build_user_prompt(question: str, context: str) -> str:
    """
    Build the user prompt with retrieved context and user question.
    """
    max_context_chars = settings.LLM_MAX_CONTEXT_CHARS
    trimmed_context = context[:max_context_chars]

    return (
        "Document context:\n"
        f"{trimmed_context}\n\n"
        "User question:\n"
        f"{question}\n\n"
        "Answer:"
    )


def build_langchain_prompt():
    """
    Build a LangChain chat prompt template for the RAG answer generation flow.
    """
    return ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}"),
        ]
    )


def get_unique_urls(urls: list[str]) -> list[str]:
    """
    Return unique URLs while preserving order.
    """
    unique_urls = []

    for url in urls:
        clean_url = url.rstrip("/")

        if clean_url and clean_url not in unique_urls:
            unique_urls.append(clean_url)

    return unique_urls


def get_ollama_candidate_urls() -> list[str]:
    """
    Return possible Ollama base URLs for local and Docker environments.
    """
    return get_unique_urls(
        [
            settings.OLLAMA_BASE_URL,
            "http://localhost:11434",
            "http://host.docker.internal:11434",
            "http://ollama:11434",
        ]
    )


def get_ollama_tags(base_url: str) -> dict:
    """
    Fetch available Ollama models from a specific base URL.
    """
    response = httpx.get(
        f"{base_url.rstrip('/')}/api/tags",
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def find_available_ollama_base_url() -> str | None:
    """
    Find the first reachable Ollama base URL.
    """
    for base_url in get_ollama_candidate_urls():
        try:
            get_ollama_tags(base_url)
            return base_url
        except httpx.HTTPError:
            continue

    return None


def is_ollama_model_available(tags_data: dict, model_name: str) -> bool:
    """
    Check whether the configured Ollama model exists.
    """
    models = tags_data.get("models", [])

    for model in models:
        if model.get("name") == model_name:
            return True

    return False


def generate_mock_answer(question: str, context: str, error_message: str = "") -> str:
    """
    Generate a safe fallback answer for development or unavailable LLM providers.
    """
    base_message = (
        "Development fallback answer: The system retrieved relevant document context, "
        "but the configured LLM provider is currently unavailable or failed to generate an answer. "
        "Please make sure Ollama is running and the selected model is available."
    )

    if error_message:
        return f"{base_message}\n\nTechnical details: {error_message}"

    if not context.strip():
        return (
            "Development fallback answer: No relevant document context was found, "
            "and the configured LLM provider is currently unavailable or failed to generate an answer."
        )

    return base_message


def generate_answer_with_ollama(question: str, context: str) -> str:
    """
    Generate an answer using Ollama through LangChain.
    """
    base_url = find_available_ollama_base_url()

    if not base_url:
        raise LLMServiceError("Ollama is not reachable from the current environment.")

    prompt = build_langchain_prompt()

    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=base_url,
        temperature=0.2,
        timeout=settings.LLM_TIMEOUT_SECONDS,
    )

    chain = prompt | llm

    try:
        response = chain.invoke(
            {
                "system_prompt": build_system_prompt(),
                "user_prompt": build_user_prompt(question, context),
            }
        )
    except Exception as exc:
        raise LLMServiceError(f"LangChain Ollama request failed: {exc}") from exc

    answer = getattr(response, "content", "").strip()

    if not answer:
        raise LLMServiceError("LangChain Ollama returned an empty answer.")

    return answer


def generate_answer_with_openrouter(question: str, context: str) -> str:
    """
    Generate an answer using OpenRouter if configured.

    This provider is kept as an optional future provider.
    """
    if not settings.OPENROUTER_API_KEY:
        raise LLMServiceError("OpenRouter API key is not configured.")

    url = "https://openrouter.ai/api/v1/chat/completions"

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": build_system_prompt(),
            },
            {
                "role": "user",
                "content": build_user_prompt(question, context),
            },
        ],
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMServiceError(f"OpenRouter request failed: {exc}") from exc

    data = response.json()
    choices = data.get("choices", [])

    if not choices:
        raise LLMServiceError("OpenRouter returned no choices.")

    answer = choices[0].get("message", {}).get("content", "").strip()

    if not answer:
        raise LLMServiceError("OpenRouter returned an empty answer.")

    return answer


def generate_answer(question: str, context: str) -> LLMGenerationResult:
    """
    Generate an answer using the configured LLM provider.
    """
    provider = settings.LLM_PROVIDER

    try:
        if provider == "ollama":
            answer = generate_answer_with_ollama(question, context)

            return LLMGenerationResult(
                answer=answer,
                provider="ollama-langchain",
                model=settings.OLLAMA_MODEL,
                used_fallback=False,
            )

        if provider == "openrouter":
            answer = generate_answer_with_openrouter(question, context)

            return LLMGenerationResult(
                answer=answer,
                provider="openrouter",
                model=settings.OPENROUTER_MODEL,
                used_fallback=False,
            )

        if provider == "mock":
            answer = generate_mock_answer(question, context)

            return LLMGenerationResult(
                answer=answer,
                provider="mock",
                model="mock",
                used_fallback=True,
            )

        raise LLMServiceError(f"Unsupported LLM provider: {provider}")

    except LLMServiceError as exc:
        if settings.LLM_FALLBACK_TO_MOCK:
            fallback_answer = generate_mock_answer(
                question=question,
                context=context,
                error_message=str(exc),
            )

            return LLMGenerationResult(
                answer=fallback_answer,
                provider="mock",
                model="mock-fallback",
                used_fallback=True,
            )

        raise


def get_llm_status() -> dict:
    """
    Check the current LLM provider status for display in the UI.
    """
    provider = settings.LLM_PROVIDER

    if provider == "mock":
        return {
            "provider": "mock",
            "model": "mock",
            "is_available": True,
            "message": "Mock provider is enabled.",
        }

    if provider == "ollama":
        for base_url in get_ollama_candidate_urls():
            try:
                tags_data = get_ollama_tags(base_url)
                model_available = is_ollama_model_available(
                    tags_data=tags_data,
                    model_name=settings.OLLAMA_MODEL,
                )

                if not model_available:
                    return {
                        "provider": "ollama-langchain",
                        "model": settings.OLLAMA_MODEL,
                        "is_available": False,
                        "message": f"Ollama is reachable at {base_url}, but the model is not installed.",
                    }

                return {
                    "provider": "ollama-langchain",
                    "model": settings.OLLAMA_MODEL,
                    "is_available": True,
                    "message": f"Ollama is available at {base_url}. LangChain is used for prompt flow and model calls.",
                }

            except httpx.HTTPError:
                continue

        return {
            "provider": "ollama-langchain",
            "model": settings.OLLAMA_MODEL,
            "is_available": False,
            "message": "Ollama is not available from the current environment.",
        }

    if provider == "openrouter":
        return {
            "provider": "openrouter",
            "model": settings.OPENROUTER_MODEL,
            "is_available": bool(settings.OPENROUTER_API_KEY),
            "message": "OpenRouter API key is configured."
            if settings.OPENROUTER_API_KEY
            else "OpenRouter API key is missing.",
        }

    return {
        "provider": provider,
        "model": "",
        "is_available": False,
        "message": "Unknown LLM provider.",
    }