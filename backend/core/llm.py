from typing import Awaitable, Callable, List
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk

MODEL_GPT_4_VISION = "gpt-4-vision-preview"
MODEL_GPT_4 = "gpt-4-1106-preview"
MODEL_GPT_4o = "gpt-4o-2024-05-13"
MODEL_GPT_4_TURBO = "gpt-4-turbo-2024-04-09"

async def stream_openai_response(
    messages: List[ChatCompletionMessageParam],
    api_key: str,
    temperature: float,
    functions: List[dict] | None,
    base_url: str | None,
    callback: Callable[[str], Awaitable[None]],
    model: str | None = None,
) -> str:
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    if model is None:
        model = MODEL_GPT_4

    # Base parameters
    params = {"model": model, "messages": messages, "stream": True, "timeout": 600, "temperature": temperature}

    # Add 'max_tokens' only if the model is a GPT4 vision model
    if model == MODEL_GPT_4_VISION:
        params["max_tokens"] = 4096
    
    # Add function calling
    if functions is not None:
        params["functions"] = functions
        params["function_call"] = {"name": functions[0]["name"]}

    stream = await client.chat.completions.create(**params)  # type: ignore
    full_response = ""
    async for chunk in stream:  # type: ignore
        assert isinstance(chunk, ChatCompletionChunk)
        if functions is not None:
            if chunk.choices[0].delta.function_call:
                content = chunk.choices[0].delta.function_call.arguments or ""
            else:
                content = ""
        else:
            content = chunk.choices[0].delta.content or ""
        full_response += content
        # print(content)
        await callback(content)

    await client.close()

    return full_response