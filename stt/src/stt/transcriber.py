from pathlib import Path
import tempfile
import wave

import numpy as np
import requests


def run_whisper_server(
    server_url: str,
    audio: np.ndarray,
    sample_rate: int,
    language: str = "ko",
) -> str:
    audio_int16 = np.asarray(audio, dtype=np.int16)

    with tempfile.TemporaryDirectory(prefix="stt_") as tmpdir:
        tmpdir_path = Path(tmpdir)
        wav_path = tmpdir_path / "input.wav"

        with wave.open(str(wav_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())

        with open(wav_path, "rb") as f:
            files = {
                "file": ("input.wav", f, "audio/wav")
            }
            data = {
                "language": language
            }

            response = requests.post(
                server_url,
                files=files,
                data=data,
                timeout=120,
            )

        if response.status_code != 200:
            raise RuntimeError(
                "whisper-server 요청 실패\n"
                f"status={response.status_code}\n"
                f"body={response.text}"
            )

        data = response.json()
        return data.get("text", "").strip()
