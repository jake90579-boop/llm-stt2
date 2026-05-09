import argparse
from pathlib import Path

from stt.config import STTConfig
from stt.postprocess import postprocess_stt_text
from stt.recorder import RecordConfig, record_enter_to_start_stop
from stt.transcriber import run_whisper_server
from stt.writer import save_text


LINE = "=" * 60


def main():
    parser = argparse.ArgumentParser(
        prog="stt",
        description="Microphone STT package using whisper.cpp server"
    )

    parser.add_argument(
        "--server-url",
        default="http://127.0.0.1:8080/inference",
        help="whisper-server 요청 주소"
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="변환된 txt 파일 저장 폴더"
    )
    parser.add_argument(
        "--lang",
        default="ko",
        help="인식 언어"
    )

    args = parser.parse_args()

    config = STTConfig(
        output_dir=Path(args.output_dir),
        language=args.lang,
        server_url=args.server_url,
    )

    rcfg = RecordConfig(
        sample_rate=config.sample_rate,
    )

    while True:
        print()
        print(LINE)
        print()

        audio = record_enter_to_start_stop(rcfg)

        if len(audio) == 0:
            print()
            print("파일 생성: ")
            print()
            print(LINE)
            print()
            continue

        text = run_whisper_server(
            server_url=config.server_url,
            audio=audio,
            sample_rate=config.sample_rate,
            language=config.language,
        ).replace("[끝]", "").strip()

        corrected_text = postprocess_stt_text(text)

        save_text(
            text=corrected_text,
            out_dir=config.output_dir,
        )

        print()
        print(f"원본 인식: {text}")
        print()
        print()
        print(f"파일 생성: {corrected_text}")
        print()
        print(LINE)
        print()


if __name__ == "__main__":
    main()
