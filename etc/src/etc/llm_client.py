import json
import os
import requests

from etc.config import MODEL_NAME


class LLMClient:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

        self.url = "https://api.openai.com/v1/responses"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key),
        }

    def generate_text(self, system_prompt, user_prompt, max_output_tokens=500):
        payload = {
            "model": MODEL_NAME,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_output_tokens": max_output_tokens,
        }

        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        raw = data.get("output_text", "").strip()

        if raw:
            return raw

        output = data.get("output", [])
        parts = []
        for item in output:
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    parts.append(content.get("text", ""))

        return "".join(parts).strip()

    def generate_json(self, system_prompt, user_prompt, default_obj):
        raw = self.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_output_tokens=700,
        )

        try:
            return json.loads(raw)
        except Exception:
            return default_obj
