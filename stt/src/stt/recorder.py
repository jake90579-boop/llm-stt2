import threading
import numpy as np
import sounddevice as sd
from dataclasses import dataclass


@dataclass
class RecordConfig:
    sample_rate: int = 16000
    channels: int = 1
    dtype: str = "int16"


def _wait_for_enter(stop_event: threading.Event) -> None:
    input()
    stop_event.set()


def record_enter_to_start_stop(cfg: RecordConfig) -> np.ndarray:
    print("Enter를 누르면 녹음을 시작합니다.")
    print()
    input()

    print("녹음 중입니다. 종료하려면 Enter를 누르세요.")
    print()

    recorded_frames = []
    stop_event = threading.Event()

    def callback(indata, frames, time, status):
        recorded_frames.append(indata.copy())
        if stop_event.is_set():
            raise sd.CallbackStop()

    enter_thread = threading.Thread(
        target=_wait_for_enter,
        args=(stop_event,),
        daemon=True
    )
    enter_thread.start()

    try:
        with sd.InputStream(
            samplerate=cfg.sample_rate,
            channels=cfg.channels,
            dtype=cfg.dtype,
            callback=callback
        ):
            while not stop_event.is_set():
                sd.sleep(100)
    except sd.CallbackStop:
        pass

    print("녹음이 종료되었습니다.")
    print()

    if not recorded_frames:
        return np.array([], dtype=np.int16)

    audio = np.concatenate(recorded_frames, axis=0).flatten()
    return audio
