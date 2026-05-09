from dataclasses import dataclass
from pathlib import Path


@dataclass
class STTConfig:
    output_dir: Path
    language: str = "ko"
    sample_rate: int = 16000
    server_url: str = "http://127.0.0.1:8080/inference"
