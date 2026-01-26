from openai import OpenAI

client = OpenAI()

def response_text(resp) -> str:
    # Responses API returns output items; easiest way is to use output_text helper if present,
    # otherwise join content parts.
    if hasattr(resp, "output_text"):
        return resp.output_text
    # fallback (conservative)
    out = []
    for item in getattr(resp, "output", []):
        for c in getattr(item, "content", []):
            if getattr(c, "type", "") == "output_text":
                out.append(getattr(c, "text", ""))
    return "\n".join(out).strip()

def create_response(model: str, input_text: str, tools=None, text_format=None):
    kwargs = {"model": model, "input": input_text}
    if tools is not None:
        kwargs["tools"] = tools
    if text_format is not None:
        kwargs["text"] = {"format": text_format}
    return client.responses.create(**kwargs)
