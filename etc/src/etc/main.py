import threading

from etc.config import (
    INPUT_DIR,
    DONE_DIR,
    DRAFT_DIR,
    INTERIM_TASK_DIR,
    FOLLOWUP_INPUT_DIR,
    FOLLOWUP_DONE_DIR,
    RESULT_DIR,
    POLL_INTERVAL,
    STABLE_WAIT,
    SKIP_EXISTING_ON_START,
)
from etc.file_utils import ensure_dir
from etc.initial_watcher import EtcInitialWatcher
from etc.followup_watcher import EtcFollowupWatcher


def main():
    ensure_dir(INPUT_DIR)
    ensure_dir(DONE_DIR)
    ensure_dir(DRAFT_DIR)
    ensure_dir(INTERIM_TASK_DIR)
    ensure_dir(FOLLOWUP_INPUT_DIR)
    ensure_dir(FOLLOWUP_DONE_DIR)
    ensure_dir(RESULT_DIR)

    print()
    print("=" * 60)
    print("[INFO] etc 패키지 시작")
    print("[INFO] etc 입력 폴더: {}".format(INPUT_DIR))
    print("[INFO] etc 초안 폴더: {}".format(DRAFT_DIR))
    print("[INFO] interim task 폴더: {}".format(INTERIM_TASK_DIR))
    print("[INFO] followup 입력 폴더: {}".format(FOLLOWUP_INPUT_DIR))
    print("[INFO] 최종 결과 폴더: {}".format(RESULT_DIR))
    print("=" * 60)

    initial_watcher = EtcInitialWatcher(
        input_dir=INPUT_DIR,
        done_dir=DONE_DIR,
        draft_dir=DRAFT_DIR,
        interim_task_dir=INTERIM_TASK_DIR,
        poll_interval=POLL_INTERVAL,
        stable_wait=STABLE_WAIT,
        skip_existing_on_start=SKIP_EXISTING_ON_START,
    )

    followup_watcher = EtcFollowupWatcher(
        followup_input_dir=FOLLOWUP_INPUT_DIR,
        followup_done_dir=FOLLOWUP_DONE_DIR,
        draft_dir=DRAFT_DIR,
        result_dir=RESULT_DIR,
        poll_interval=POLL_INTERVAL,
        stable_wait=STABLE_WAIT,
        skip_existing_on_start=SKIP_EXISTING_ON_START,
    )

    t1 = threading.Thread(target=initial_watcher.run, daemon=True)
    t2 = threading.Thread(target=followup_watcher.run, daemon=True)

    t1.start()
    t2.start()

    try:
        while True:
            t1.join(timeout=1.0)
            t2.join(timeout=1.0)
    except KeyboardInterrupt:
        print("\n[INFO] etc 패키지 종료")


if __name__ == "__main__":
    main()
