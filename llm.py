import requests
from typing import List, Dict



OLLAMA_HOST = "http://localhost:11434"
MODEL       = "mistral:7b"
TIMEOUT_S   = 120
TEMPERATURE = 0.69


def _payload(messages: List[Dict[str, str]]) -> Dict:
    """Build the JSON payload for Ollama /api/chat."""
    return {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": TEMPERATURE},
    }


def chat(prompt: str, system_prompt: str | None = None) -> str:
    """
    Send a single-shot conversation to the model and return the reply string.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    url = f"{OLLAMA_HOST.rstrip('/')}/api/chat"
    resp = requests.post(url, json=_payload(messages), timeout=TIMEOUT_S)
    resp.raise_for_status()

    return resp.json()["message"]["content"].strip()





if __name__ == "__main__":
    print(chat("Say hi in exactly five words."))
