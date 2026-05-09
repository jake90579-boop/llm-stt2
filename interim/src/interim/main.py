from interim.config import (
    INPUT_DIR,
    DONE_DIR,
    PENDING_DIR,
    POLL_INTERVAL,
    STABLE_WAIT,
    SKIP_EXISTING_ON_START,
)
from interim.file_utils import ensure_dir
from interim.watcher import InterimWatcher


def main() -> None:
    ensure_dir(INPUT_DIR)
    ensure_dir(DONE_DIR)
    ensure_dir(PENDING_DIR)

    print()
    print("=" * 60)
    print("[INFO] interim 패키지 시작")
    print(f"[INFO] 감시 폴더: {INPUT_DIR}")
    print("=" * 60)

    watcher = InterimWatcher(
        input_dir=INPUT_DIR,
        done_dir=DONE_DIR,
        pending_dir=PENDING_DIR,
        poll_interval=POLL_INTERVAL,
        stable_wait=STABLE_WAIT,
        skip_existing_on_start=SKIP_EXISTING_ON_START,
    )
    watcher.run()


if __name__ == "__main__":
    main()
