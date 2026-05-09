from concurrent.futures import ThreadPoolExecutor, as_completed

from mixed.config import (
    MAX_WORKERS,
    MAP_JSON_PATH,
    ORCHESTRATOR_PROMPT,
    WORKER_PROMPT,
    AGGREGATOR_PROMPT,
    FINALIZER_PROMPT,
)
from mixed.llm_client import LLMClient
from mixed.map_rag import HospitalMapRAG


class MixedEngine:
    def __init__(self):
        self.client = LLMClient()
        self.map_rag = HospitalMapRAG(MAP_JSON_PATH)

    def make_plan(self, user_text):
        system_prompt = ORCHESTRATOR_PROMPT.format(max_workers=MAX_WORKERS)
        default_obj = {
            "tasks": [
                {
                    "title": "행동 관점 정리",
                    "instruction": "사용자가 무엇을 해야 하는지 행동 관점에서 핵심을 정리하라"
                },
                {
                    "title": "위치/증상 관점 정리",
                    "instruction": "질문에 포함된 위치 또는 증상 요소를 따로 정리해 안내하라"
                }
            ]
        }

        plan = self.client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_text,
            default_obj=default_obj,
        )

        tasks = plan.get("tasks", [])
        if not isinstance(tasks, list) or len(tasks) < 2:
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

        if len(cleaned) < 2:
            cleaned = default_obj["tasks"]

        return cleaned

    def build_map_context(self, user_text: str) -> str:
        return self.map_rag.build_map_context(user_text)

    def run_worker(self, user_text, task, map_context):
        worker_prompt = WORKER_PROMPT.format(
            user_text=user_text,
            map_context=map_context,
            title=task["title"],
            instruction=task["instruction"],
        )

        result = self.client.generate_text(
            system_prompt="너는 mixed 워커다.",
            user_prompt=worker_prompt,
            max_output_tokens=300,
        )

        return {
            "title": task["title"],
            "result": result.strip(),
        }

    def run_workers(self, user_text, tasks, map_context):
        worker_results = []
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = [
                executor.submit(self.run_worker, user_text, task, map_context)
                for task in tasks
            ]

            for future in as_completed(futures):
                worker_results.append(future.result())

        return worker_results

    def aggregate(self, user_text, worker_results, map_context):
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
            map_context=map_context,
            worker_outputs=worker_outputs,
        )

        draft_answer = self.client.generate_text(
            system_prompt="너는 mixed 애그리게이터다.",
            user_prompt=aggregator_prompt,
            max_output_tokens=500,
        )

        return draft_answer.strip()

    def process_with_tasks(self, user_text, tasks):
        map_context = self.build_map_context(user_text)
        worker_results = self.run_workers(user_text, tasks, map_context)
        draft_answer = self.aggregate(user_text, worker_results, map_context)

        return {
            "tasks": tasks,
            "worker_results": worker_results,
            "draft_answer": draft_answer,
            "map_context": map_context,
        }

    def finalize(self, original_user_text, draft_answer, followup_answer):
        map_context = self.build_map_context(original_user_text)

        prompt = FINALIZER_PROMPT.format(
            original_user_text=original_user_text,
            map_context=map_context,
            draft_answer=draft_answer,
            followup_answer=followup_answer,
        )

        final_answer = self.client.generate_text(
            system_prompt="너는 mixed 최종 응답 정리기다.",
            user_prompt=prompt,
            max_output_tokens=500,
        )

        return final_answer.strip()

    def process(self, user_text):
        tasks = self.make_plan(user_text)
        return self.process_with_tasks(user_text, tasks)
        
    def get_confirmed_place_name(self, user_text: str) -> str:
        return self.map_rag.get_matched_place_name(user_text)
