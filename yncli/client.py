import json
import requests
from typing import List, Dict, Any, Generator, Optional, Callable


class LLMClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream"
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Fetches the list of available models from the endpoint (supports OpenAI, OpenRouter, Google Gemini).
        """
        # Google Gemini models endpoint
        if "generativelanguage.googleapis.com" in self.base_url:
            url = f"https://generativelanguage.googleapis.com/v1beta/openai/models"
            try:
                resp = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    models = []
                    for m in data.get("data", []):
                        mid = m.get("id", "").replace("models/", "")
                        # Filter to modern fast and coding models
                        if any(k in mid for k in ["flash", "pro", "gemma"]) and "embedding" not in mid and "tts" not in mid and "image" not in mid:
                            models.append({"id": mid})
                    return models
            except Exception:
                pass

        url = f"{self.base_url}/models"
        try:
            resp = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])
        except Exception:
            return []

    def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 16384,
        on_thinking: Optional[Callable[[str], None]] = None,
        on_content: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Streams chat completions from the OpenAI-compatible endpoint.
        Guarantees strict UTF-8 stream decoding to prevent ISO-8859-1 mojibake.
        Uses resilient timeout (connect=15s, read=180s) to support heavy code generation.
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        # Resilient timeout: (connect_timeout=15s, read_timeout=180s)
        resp = requests.post(url, headers=self._get_headers(), json=payload, stream=True, timeout=(15, 180))
        resp.encoding = "utf-8"

        if resp.status_code != 200:
            err_text = resp.text
            raise RuntimeError(f"API Error ({resp.status_code}): {err_text}")

        accumulated_thinking = []
        accumulated_content = []
        accumulated_tools: Dict[int, Dict[str, Any]] = {}
        finish_reason = None

        # Read raw byte lines and explicitly decode as UTF-8
        for line_bytes in resp.iter_lines(decode_unicode=False):
            if not line_bytes:
                continue

            try:
                line = line_bytes.decode("utf-8", errors="replace").strip()
            except Exception:
                continue

            if not line:
                continue

            if line.startswith("data: "):
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except Exception:
                    continue

                choices = chunk.get("choices", [])
                if not choices:
                    continue

                choice = choices[0]
                delta = choice.get("delta", {})
                finish = choice.get("finish_reason")
                if finish:
                    finish_reason = finish

                # 1. Check reasoning / thinking content
                reasoning_chunk = delta.get("reasoning_content") or delta.get("reasoning")
                if reasoning_chunk:
                    accumulated_thinking.append(reasoning_chunk)
                    if on_thinking:
                        on_thinking(reasoning_chunk)

                # 2. Check main response content
                content_chunk = delta.get("content")
                if content_chunk:
                    accumulated_content.append(content_chunk)
                    if on_content:
                        on_content(content_chunk)

                # 3. Check tool calls
                tool_calls = delta.get("tool_calls")
                if tool_calls:
                    for tc in tool_calls:
                        idx = tc.get("index", 0)
                        if idx not in accumulated_tools:
                            accumulated_tools[idx] = {
                                "id": tc.get("id", f"call_{idx}"),
                                "type": "function",
                                "function": {
                                    "name": tc.get("function", {}).get("name", ""),
                                    "arguments": tc.get("function", {}).get("arguments", "")
                                }
                            }
                        else:
                            fn = tc.get("function", {})
                            if fn.get("name"):
                                accumulated_tools[idx]["function"]["name"] += fn["name"]
                            if fn.get("arguments"):
                                accumulated_tools[idx]["function"]["arguments"] += fn["arguments"]
                            if tc.get("id"):
                                accumulated_tools[idx]["id"] = tc["id"]

        final_tool_calls = list(accumulated_tools.values())
        return {
            "role": "assistant",
            "thinking": "".join(accumulated_thinking),
            "content": "".join(accumulated_content),
            "tool_calls": final_tool_calls if final_tool_calls else None,
            "finish_reason": finish_reason
        }
