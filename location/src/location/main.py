import threading

from location.config import (
    INPUT_DIR,
    DONE_DIR,
    DRAFT_DIR,
    INTERIM_TASK_DIR,
    FOLLOWUP_INPUT_DIR,
    FOLLOWUP_DONE_DIR,
    RESULT_DIR,
    PENDING_FOLLOWUP_DIR,
    POLL_INTERVAL,
    STABLE_WAIT,
    SKIP_EXISTING_ON_START,
)
from location.file_utils import ensure_dir
from location.initial_watcher import LocationInitialWatcher
from location.followup_watcher import LocationFollowupWatcher


def main():
    ensure_dir(INPUT_DIR)
    ensure_dir(DONE_DIR)
    ensure_dir(DRAFT_DIR)
    ensure_dir(INTERIM_TASK_DIR)
    ensure_dir(FOLLOWUP_INPUT_DIR)
    ensure_dir(FOLLOWUP_DONE_DIR)
    ensure_dir(RESULT_DIR)
    ensure_dir(PENDING_FOLLOWUP_DIR)

    print()
    print("=" * 60)
    print("[INFO] location 패키지 시작")
    print("[INFO] location 입력 폴더: {}".format(INPUT_DIR))
    print("[INFO] location 초안 폴더: {}".format(DRAFT_DIR))
    print("[INFO] interim task 폴더: {}".format(INTERIM_TASK_DIR))
    print("[INFO] followup 입력 폴더: {}".format(FOLLOWUP_INPUT_DIR))
    print("[INFO] 최종 결과 폴더: {}".format(RESULT_DIR))
    print("[INFO] pending followup 폴더: {}".format(PENDING_FOLLOWUP_DIR))
    print("=" * 60)

    initial_watcher = LocationInitialWatcher(
        input_dir=INPUT_DIR,
        done_dir=DONE_DIR,
        draft_dir=DRAFT_DIR,
        interim_task_dir=INTERIM_TASK_DIR,
        poll_interval=POLL_INTERVAL,
        stable_wait=STABLE_WAIT,
        skip_existing_on_start=SKIP_EXISTING_ON_START,
    )

    followup_watcher = LocationFollowupWatcher(
        followup_input_dir=FOLLOWUP_INPUT_DIR,
        followup_done_dir=FOLLOWUP_DONE_DIR,
        draft_dir=DRAFT_DIR,
        result_dir=RESULT_DIR,
        pending_followup_dir=PENDING_FOLLOWUP_DIR,
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
        print("\n[INFO] location 패키지 종료")


if __name__ == "__main__":
    main()
