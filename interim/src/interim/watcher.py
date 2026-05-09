import json
import os
import time
from pathlib import Path
from typing import Set

import requests

from interim.config import MODEL_NAME, INTERIM_SYSTEM_PROMPT
from interim.file_utils import is_file_stable, read_json_file, write_json_file, move_file


class InterimWatcher:
    def __init__(
        self,
        input_dir: Path,
        done_dir: Path,
        pending_dir: Path,
        poll_interval: float = 0.5,
        stable_wait: float = 0.2,
        skip_existing_on_start: bool = True,
    ) -> None:
        self.input_dir = input_dir
        self.done_dir = done_dir
        self.pending_dir = pending_dir
        self.poll_interval = poll_interval
        self.stable_wait = stable_wait
        self.seen: Set[str] = set()

        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

        self.url = "https://api.openai.com/v1/responses"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        if skip_existing_on_start:
            for path in self.input_dir.glob("*.json"):
                self.seen.add(path.name)

    def generate_interim(self, payload_dict: dict) -> dict:
        category = payload_dict.get("category", "etc")
        user_text = payload_dict.get("user_text", "")
        tasks = payload_dict.get("tasks", [])

        task_titles = []
        for task in tasks:
            title = str(task.get("title", "")).strip()
            if title:
                task_titles.append(title)

        user_prompt = json.dumps(
            {
                "category": category,
                "user_text": user_text,
                "task_titles": task_titles,
            },
            ensure_ascii=False,
            indent=2,
        )

        payload = {
            "model": MODEL_NAME,
            "input": [
                {"role": "system", "content": INTERIM_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "max_output_tokens": 200,
        }

        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        raw = data.get("output_text", "").strip()

        if not raw:
            output = data.get("output", [])
            parts = []
            for item in output:
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        parts.append(content.get("text", ""))
            raw = "".join(parts).strip()

        try:
            parsed = json.loads(raw)
            status = str(parsed.get("status", "")).strip()
            question = str(parsed.get("question", "")).strip()
        except Exception:
            status = "질문 내용을 바탕으로 필요한 정보를 확인하고 있습니다."
            question = "조금 더 구체적으로 말씀해주실 수 있을까요?"

        if not status:
            status = "질문 내용을 바탕으로 필요한 정보를 확인하고 있습니다."
        if not question:
            question = "조금 더 구체적으로 말씀해주실 수 있을까요?"

        return {
            "status": status,
            "question": question,
        }

    def _print_block(self, filename: str, status: str, question: str) -> None:
        print()
        print("=" * 60)
        print("[INTERIM]")
        print(f"[FILE] {filename}")
        print()
        print(status)
        print()
        print("[QUESTION]")
        print(question)
        print("=" * 60)

    def process_file(self, file_path: Path) -> None:
        if not is_file_stable(file_path, self.stable_wait):
            return

        try:
            payload_dict = read_json_file(file_path)
            generated = self.generate_interim(payload_dict)

            pending_path = self.pending_dir / "current.json"
            write_json_file(
                pending_path,
                {
                    "category": payload_dict.get("category", "etc"),
                    "session_id": payload_dict.get("session_id", file_path.stem),
                    "filename": payload_dict.get("filename", file_path.stem + ".txt"),
                    "question": generated["question"],
                },
            )

            self._print_block(
                file_path.name,
                generated["status"],
                generated["question"],
            )

            move_file(file_path, self.done_dir)

        except Exception as e:
            print()
            print("=" * 60)
            print(f"[ERROR] interim 처리 실패: {file_path.name}")
            print(e)
            print("=" * 60)

    def run(self) -> None:
        while True:
            try:
                json_files = sorted(self.input_dir.glob("*.json"))

                for file_path in json_files:
                    if file_path.name in self.seen:
                        continue

                    self.seen.add(file_path.name)
                    self.process_file(file_path)

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(self.poll_interval)
