from pathlib import Path

INPUT_DIR = Path("/home/pc415-28/llm_package/bus/interim_task")
DONE_DIR = Path("/home/pc415-28/llm_package/bus/interim_task_done")
PENDING_DIR = Path("/home/pc415-28/llm_package/bus/pending_followup")

POLL_INTERVAL = 0.5
STABLE_WAIT = 0.2
SKIP_EXISTING_ON_START = True

MODEL_NAME = "gpt-4o-mini"

INTERIM_SYSTEM_PROMPT = """
너는 병원 안내 시스템의 중간 질문 생성기다.

입력으로는
- 질문 분류 category
- 사용자 원문
- 오케스트레이터가 만든 task 제목 목록

이 주어진다.

너의 역할:
1. 지금 어떤 내용을 확인 중인지 짧게 한 문장으로 말한다.
2. 사용자가 짧게 대답할 수 있는 추가 질문 한 개를 만든다.

반드시 아래 JSON 형식으로만 답하라.

{
  "status": "짧은 상태 안내 문장",
  "question": "사용자에게 던질 짧은 추가 질문"
}

규칙:
- status는 한 문장
- question도 한 문장
- question은 task 제목과 사용자 질문에 직접 관련되어야 함
- question은 짧고 답하기 쉬워야 함
- 병원 정보를 지어내지 말 것
- 최종 답변을 하지 말 것
- JSON만 출력
"""
