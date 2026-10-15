"""Local LLM calls via Ollama.

Everything here runs on your machine and costs nothing. Results are cached in the
corpus database by the calling stage, so a paper is never screened or extracted
twice.
"""
from __future__ import annotations

import json
import re
from typing import Any

import requests


class Ollama:
    def __init__(self, host: str = "http://localhost:11434",
                 model: str = "qwen2.5:7b-instruct",
                 num_ctx: int = 8192, temperature: float = 0.0,
                 timeout: int = 600) -> None:
        self.host = host.rstrip("/")
        self.model = model
        self.num_ctx = num_ctx
        self.temperature = temperature
        self.timeout = timeout

    def available(self) -> tuple[bool, str]:
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=5)
        except requests.RequestException as exc:
            return False, f"cannot reach Ollama at {self.host} ({exc.__class__.__name__})"
        if r.status_code != 200:
            return False, f"Ollama returned HTTP {r.status_code}"
        models = [m.get("name", "") for m in r.json().get("models", [])]
        if self.model not in models and self.model.split(":")[0] not in [
            m.split(":")[0] for m in models
        ]:
            return False, (f"model '{self.model}' not installed. Have: "
                           f"{', '.join(models) or 'none'}. Run: ollama pull {self.model}")
        return True, "ok"

    def generate(self, prompt: str, system: str = "", json_mode: bool = False) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_ctx": self.num_ctx, "temperature": self.temperature},
        }
        if system:
            payload["system"] = system
        if json_mode:
            payload["format"] = "json"
        r = requests.post(f"{self.host}/api/generate", json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json().get("response", "")

    def json(self, prompt: str, system: str = "") -> dict[str, Any] | None:
        raw = self.generate(prompt, system=system, json_mode=True)
        return parse_json(raw)


def parse_json(raw: str) -> dict[str, Any] | None:
    """Small models sometimes wrap JSON in prose or fences. Dig it out."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        out = json.loads(raw)
        return out if isinstance(out, dict) else {"value": out}
    except ValueError:
        pass
    fenced = re.search(r"```(?:json)?\s*(.+?)```", raw, re.S)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except ValueError:
            pass
    brace = re.search(r"\{.*\}", raw, re.S)
    if brace:
        try:
            return json.loads(brace.group(0))
        except ValueError:
            return None
    return None
