import json
import time
import shutil
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def is_file_stable(file_path: Path, wait_sec: float = 0.2) -> bool:
    if not file_path.exists() or not file_path.is_file():
        return False

    try:
        size1 = file_path.stat().st_size
        time.sleep(wait_sec)
        size2 = file_path.stat().st_size
        return size1 == size2
    except FileNotFoundError:
        return False


def read_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore").strip()


def write_text_file(file_path: Path, text: str) -> None:
    file_path.write_text(text, encoding="utf-8")


def read_json_file(file_path: Path) -> dict:
    return json.loads(file_path.read_text(encoding="utf-8"))


def write_json_file(file_path: Path, data: dict) -> None:
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def move_file(file_path: Path, target_dir: Path) -> Path:
    ensure_dir(target_dir)
    target_path = target_dir / file_path.name

    if target_path.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        target_path = target_dir / f"{stem}_{timestamp}{suffix}"

    shutil.move(str(file_path), str(target_path))
    return target_path
