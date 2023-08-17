from typing import Any, Literal  # pragma: no cover
from litellm import completion as litellm_completion  # pragma: no cover


SUPPORTED_MODELS = Literal[  # pragma: no cover
    # https://docs.litellm.ai/docs/completion/supported#openai-chat-completion-models
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-4",
    # https://docs.litellm.ai/docs/completion/supported#ai21-models
    "j2-ultra",
    # https://docs.litellm.ai/docs/completion/supported#cohere-models
    "command-nightly",
]


def completion(
    model: SUPPORTED_MODELS,  # pragma: no cover
    messages: Any,
    temperature: int = 1,
):
    return litellm_completion(
        model, messages, temperature=temperature
    )  # pragma: no cover
