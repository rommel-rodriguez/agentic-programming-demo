import json
import re

exp = re.compile(r"```json(.*)```", flags=re.DOTALL | re.IGNORECASE)


def ai_json_string_to_dict(ai_output: str) -> dict:
    if ai_output is None:
        raise ValueError("ai_output is required")

    match = exp.search(ai_output)
    payload = match.group(1) if match else ai_output
    return json.loads(payload.strip())


def ai_json_string_strip_tags(ai_output: str) -> str:
    if ai_output is None:
        raise ValueError("ai_output is required")

    match = exp.search(ai_output)
    payload = match.group(1) if match else ai_output
    return payload.strip()
