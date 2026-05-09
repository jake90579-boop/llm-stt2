from datetime import datetime
from pathlib import Path


def make_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_text(text: str, out_dir: Path) -> Path:
    ensure_dir(out_dir)

    filename = f"stt_{make_timestamp()}.txt"
    txt_path = out_dir / filename

    txt_path.write_text(text, encoding="utf-8")

    return txt_path
