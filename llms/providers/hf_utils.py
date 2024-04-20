from text_generation import Client  # type: ignore
import os


def generate_from_huggingface_completion(
    prompt: str,
    model_endpoint: str,
    temperature: float,
    top_p: float,
    max_new_tokens: int,
    stop_sequences: list[str] | None = None,
) -> str:
    client = Client(model_endpoint, timeout=60)
    generation: str = client.generate(
        prompt=prompt,
        temperature=temperature,
        top_p=top_p,
        max_new_tokens=max_new_tokens,
        stop_sequences=stop_sequences,
    ).generated_text

    return generation


def generate_from_huggingface_chat_completion(
    prompt: list[dict[str, str]],
    model_endpoint: str,
    temperature: float,
    top_p: float,
    max_new_tokens: int,
    stop_sequences: list[str] | None = None,
) -> str:
    for message in prompt:
        message["content"] = message["content"].replace(
            "The information in this tab has been changed. This tab contains invalid data. Please resolve this before saving. Loading... ",
            "",
        )

    client = Client(
        model_endpoint,
        timeout=60,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ.get('HF_TOKEN', '')}",
            "Content-Type": "application/json",
        },
    )
    generation: str = (
        client.chat(
            messages=prompt,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_new_tokens,
        )
        .choices[0]
        .message.content
    )

    return generation
