from text_generation import Client  # type: ignore
from llama_cpp import Llama

llm = Llama(
    model_path="/home/ubuntu/webarena/Meta-Llama-3-8B-Instruct.Q8_0.gguf",
    n_gpu_layers=-1,
    n_ctx=8192,
    verbose=False,
)


# def generate_from_huggingface_completion(
#     prompt: str,
#     model_endpoint: str,
#     temperature: float,
#     top_p: float,
#     max_new_tokens: int,
#     stop_sequences: list[str] | None = None,
# ) -> str:
#     client = Client(model_endpoint, timeout=60)
#     generation: str = client.generate(
#         prompt=prompt,
#         temperature=temperature,
#         top_p=top_p,
#         max_new_tokens=max_new_tokens,
#         stop_sequences=stop_sequences,
#     ).generated_text

#     return generation


def generate_from_huggingface_completion(
    prompt: str,
    model_endpoint: str,
    temperature: float,
    top_p: float,
    max_new_tokens: int,
    stop_sequences: list[str] | None = None,
) -> str:
    prompt = prompt.replace(
        "The information in this tab has been changed. This tab contains invalid data. Please resolve this before saving. Loading... ",
        "",
    )
    output = llm.create_completion(
        prompt=prompt,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_new_tokens,
        stop=stop_sequences,
    )
    generation = output["choices"][0]["text"]
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
    output = llm.create_chat_completion(
        messages=prompt,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_new_tokens,
        stop=stop_sequences,
    )
    generation = output["choices"][0]["message"]["content"]
    return generation
