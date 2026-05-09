import time
from pathlib import Path
from typing import Set

from action.engine import ActionEngine
from action.file_utils import (
    is_file_stable,
    read_text_file,
    write_text_file,
    write_json_file,
    move_file,
)


class ActionWatcher:
    def __init__(
        self,
        input_dir,
        done_dir,
        draft_dir,
        interim_task_dir,
        poll_interval=0.5,
        stable_wait=0.2,
        skip_existing_on_start=True,
    ):
        self.input_dir = input_dir
        self.done_dir = done_dir
        self.draft_dir = draft_dir
        self.interim_task_dir = interim_task_dir
        self.poll_interval = poll_interval
        self.stable_wait = stable_wait
        self.engine = ActionEngine()
        self.seen: Set[str] = set()

        if skip_existing_on_start:
            for path in self.input_dir.glob("*.txt"):
                self.seen.add(path.name)

    def _print_block(self, filename, user_text, task_count, draft_answer):
        print()
        print("=" * 60)
        print("[ACTION] 새 파일 감지: {}".format(filename))
        print()
        print("[TEXT]")
        print(user_text if user_text else "(빈 파일)")
        print()
        print("[WORKERS] {}".format(task_count))
        print()
        print("[DRAFT]")
        print(draft_answer)
        print("=" * 60)

    def process_file(self, file_path: Path):
        if not is_file_stable(file_path, self.stable_wait):
            return

        try:
            user_text = read_text_file(file_path)

            tasks = self.engine.make_plan(user_text)

            interim_task_path = self.interim_task_dir / (file_path.stem + ".json")
            write_json_file(
                interim_task_path,
                {
                    "category": "action",
                    "filename": file_path.name,
                    "user_text": user_text,
                    "tasks": tasks,
                },
            )

            result = self.engine.process_with_tasks(user_text, tasks)

            draft_path = self.draft_dir / file_path.name
            write_text_file(draft_path, result["final_answer"])

            move_file(file_path, self.done_dir)

            self._print_block(
                filename=file_path.name,
                user_text=user_text,
                task_count=len(result["tasks"]),
                draft_answer=result["final_answer"],
            )

        except Exception as e:
            print()
            print("=" * 60)
            print("[ERROR] action 처리 실패: {}".format(file_path.name))
            print(e)
            print("=" * 60)

    def run(self):
        while True:
            try:
                txt_files = sorted(self.input_dir.glob("*.txt"))

                for file_path in txt_files:
                    if file_path.name in self.seen:
                        continue

                    self.seen.add(file_path.name)
                    self.process_file(file_path)

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(self.poll_interval)
