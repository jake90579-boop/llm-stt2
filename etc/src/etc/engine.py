from concurrent.futures import ThreadPoolExecutor, as_completed

from etc.config import (
    MAX_WORKERS,
    ORCHESTRATOR_PROMPT,
    WORKER_PROMPT,
    AGGREGATOR_PROMPT,
    FINALIZER_PROMPT,
)
from etc.llm_client import LLMClient


class EtcEngine:
    def __init__(self):
        self.client = LLMClient()

    def make_plan(self, user_text):
        system_prompt = ORCHESTRATOR_PROMPT.format(max_workers=MAX_WORKERS)
        default_obj = {
            "tasks": [
                {
                    "title": "질문 의미 파악",
                    "instruction": "사용자 질문이 병원 안내 범위에서 어떤 의미인지 간단히 정리하라"
                },
                {
                    "title": "안전한 응답 방향 정리",
                    "instruction": "질문이 애매하거나 범위를 벗어날 때 어떻게 자연스럽게 안내할지 정리하라"
                }
            ]
        }

        plan = self.client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_text,
            default_obj=default_obj,
        )

        tasks = plan.get("tasks", [])
        if not isinstance(tasks, list) or not tasks:
            tasks = default_obj["tasks"]

        cleaned = []
        for task in tasks[:MAX_WORKERS]:
            title = str(task.get("title", "작업")).strip()
            instruction = str(task.get("instruction", "")).strip()

            if not instruction:
                continue

            cleaned.append({
                "title": title or "작업",
                "instruction": instruction,
            })

        if not cleaned:
            cleaned = default_obj["tasks"]

        return cleaned

    def run_worker(self, user_text, task):
        worker_prompt = WORKER_PROMPT.format(
            user_text=user_text,
            title=task["title"],
            instruction=task["instruction"],
        )

        result = self.client.generate_text(
            system_prompt="너는 etc 워커다.",
            user_prompt=worker_prompt,
            max_output_tokens=300,
        )

        return {
            "title": task["title"],
            "result": result.strip(),
        }

    def run_workers(self, user_text, tasks):
        worker_results = []
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = [
                executor.submit(self.run_worker, user_text, task)
                for task in tasks
            ]

            for future in as_completed(futures):
                worker_results.append(future.result())

        return worker_results

    def aggregate(self, user_text, worker_results):
        chunks = []
        for idx, item in enumerate(worker_results, start=1):
            chunks.append(
                "[워커 {} - {}]\n{}".format(
                    idx,
                    item["title"],
                    item["result"],
                )
            )

        worker_outputs = "\n\n".join(chunks)

        aggregator_prompt = AGGREGATOR_PROMPT.format(
            user_text=user_text,
            worker_outputs=worker_outputs,
        )

        draft_answer = self.client.generate_text(
            system_prompt="너는 etc 애그리게이터다.",
            user_prompt=aggregator_prompt,
            max_output_tokens=500,
        )

        return draft_answer.strip()

    def process_with_tasks(self, user_text, tasks):
        worker_results = self.run_workers(user_text, tasks)
        draft_answer = self.aggregate(user_text, worker_results)

        return {
            "tasks": tasks,
            "worker_results": worker_results,
            "draft_answer": draft_answer,
        }

    def finalize(self, original_user_text, draft_answer, followup_answer):
        prompt = FINALIZER_PROMPT.format(
            original_user_text=original_user_text,
            draft_answer=draft_answer,
            followup_answer=followup_answer,
        )

        final_answer = self.client.generate_text(
            system_prompt="너는 etc 최종 응답 정리기다.",
            user_prompt=prompt,
            max_output_tokens=500,
        )

        return final_answer.strip()

    def process(self, user_text):
        tasks = self.make_plan(user_text)
        return self.process_with_tasks(user_text, tasks)
