import time
from pathlib import Path
from typing import Set

from location.engine import LocationEngine
from location.file_utils import (
    is_file_stable,
    read_text_file,
    read_json_file,
    write_text_file,
    write_json_file,
    move_file,
)


class LocationFollowupWatcher:
    def __init__(
        self,
        followup_input_dir,
        followup_done_dir,
        draft_dir,
        result_dir,
        pending_followup_dir,
        poll_interval=0.5,
        stable_wait=0.2,
        skip_existing_on_start=True,
    ):
        self.followup_input_dir = followup_input_dir
        self.followup_done_dir = followup_done_dir
        self.draft_dir = draft_dir
        self.result_dir = result_dir
        self.pending_followup_dir = pending_followup_dir
        self.poll_interval = poll_interval
        self.stable_wait = stable_wait
        self.engine = LocationEngine()
        self.seen: Set[str] = set()

        if skip_existing_on_start:
            for path in self.followup_input_dir.glob("*.txt"):
                self.seen.add(path.name)

    def _print_block(self, filename, followup_answer, final_answer):
        print()
        print("=" * 60)
        print("[LOCATION-FOLLOWUP] 새 후속 답변 감지: {}".format(filename))
        print()
        print("[FOLLOWUP ANSWER]")
        print(followup_answer if followup_answer else "(빈 답변)")
        print()
        print("[FINAL ANSWER]")
        print(final_answer)
        print("=" * 60)

    def process_file(self, file_path: Path):
        if not is_file_stable(file_path, self.stable_wait):
            return

        try:
            followup_answer = read_text_file(file_path)

            draft_path = self.draft_dir / (file_path.stem + ".json")
            if not draft_path.exists():
                raise RuntimeError("대응되는 draft 파일이 없습니다: {}".format(draft_path.name))

            draft_data = read_json_file(draft_path)

            final_answer = self.engine.finalize(
                original_user_text=draft_data["original_user_text"],
                draft_answer=draft_data["draft_answer"],
                followup_answer=followup_answer,
            )

            place_name = self.engine.get_confirmed_place_name(
                draft_data["original_user_text"]
            )

            if place_name:
                final_answer = final_answer.rstrip()
                if not final_answer.endswith(("?", "요.", "니다.", "습니다.")):
                    final_answer += "."
                final_answer += "\n해당 위치로 안내해드릴까요?"

                pending_path = self.pending_followup_dir / "current.json"
                write_json_file(
                    pending_path,
                    {
                        "category": "location",
                        "session_id": file_path.stem,
                        "filename": file_path.stem + ".txt",
                        "mode": "nav_confirm",
                        "place_name": place_name,
                    },
                )

            result_path = self.result_dir / (file_path.stem + ".txt")
            write_text_file(result_path, final_answer)

            move_file(file_path, self.followup_done_dir)

            self._print_block(
                filename=file_path.name,
                followup_answer=followup_answer,
                final_answer=final_answer,
            )

        except Exception as e:
            print()
            print("=" * 60)
            print("[ERROR] location followup 처리 실패: {}".format(file_path.name))
            print(e)
            print("=" * 60)

    def run(self):
        while True:
            try:
                txt_files = sorted(self.followup_input_dir.glob("*.txt"))

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
