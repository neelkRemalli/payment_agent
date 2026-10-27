"""Make provider-independent chat requests through the OpenAI-compatible API."""

import base64
from pathlib import Path

from config import AIConfig, load_ai_config
from image_service import validate_image


_IMAGE_MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def request_ai_response(
    prompt: str,
    config: AIConfig | None = None,
    image_path: str | Path | None = None,
) -> str:
    """Send a text prompt, optionally with a validated image, and return text.

    The OpenAI SDK supports compatible endpoints through ``base_url``, so the
    provider can be changed through configuration without changing this code.
    """
    request_input = prompt
    if image_path is not None:
        validation = validate_image(image_path)
        if not validation.valid:
            raise ValueError(validation.message)

        path = Path(image_path)
        media_type = _IMAGE_MEDIA_TYPES[path.suffix.lower()]
        encoded_image = base64.b64encode(path.read_bytes()).decode("ascii")
        request_input = [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{media_type};base64,{encoded_image}",
                    },
                ],
            }
        ]

    ai_config = config if config is not None else load_ai_config()
    from openai import APIError, OpenAI

    client = OpenAI(
        api_key=ai_config.api_key,
        base_url=ai_config.base_url,
        timeout=ai_config.timeout_seconds,
    )
    try:
        response = client.responses.create(
            model=ai_config.model,
            input=request_input,
        )
    except APIError as exc:
        raise RuntimeError(f"AI API request failed: {exc}") from exc
    output_text = response.output_text
    if output_text is None or not output_text.strip():
        raise RuntimeError("AI API returned an empty response")
    return output_text
