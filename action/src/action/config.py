from pathlib import Path

MODEL_NAME = "gpt-4o-mini"

INPUT_DIR = Path("/home/pc415-28/llm_package/bus/action")
DONE_DIR = Path("/home/pc415-28/llm_package/bus/action_done")

DRAFT_DIR = Path("/home/pc415-28/llm_package/bus/action_draft")
INTERIM_TASK_DIR = Path("/home/pc415-28/llm_package/bus/interim_task")

FOLLOWUP_INPUT_DIR = Path("/home/pc415-28/llm_package/bus/action_followup")
FOLLOWUP_DONE_DIR = Path("/home/pc415-28/llm_package/bus/action_followup_done")
RESULT_DIR = Path("/home/pc415-28/llm_package/bus/action_result")

POLL_INTERVAL = 0.5
STABLE_WAIT = 0.2
SKIP_EXISTING_ON_START = True

MAX_WORKERS = 5
WORKER_TIMEOUT = 60

ORCHESTRATOR_PROMPT = """
너는 병원 안내 시스템의 action 오케스트레이터다.

입력 문장은 '사용자가 무엇을 해야 하는지'에 대한 요청이다.
너의 역할은 이 요청을 해결하기 위해 필요한 하위 작업들을 계획하는 것이다.

반드시 아래 JSON 형식으로만 답하라.

{{
  "tasks": [
    {{
      "title": "작업 제목",
      "instruction": "이 워커가 수행할 구체적인 작업 지시"
    }}
  ]
}}

규칙:
- tasks 개수는 1개 이상 {max_workers}개 이하
- 질문이 단순하면 1~2개만 생성
- 질문이 복합적이어도 불필요하게 세분화하지 말 것
- 각 instruction은 서로 겹치지 않게 작성
- 설명 문장, 마크다운, 코드블록 없이 JSON만 출력
"""

WORKER_PROMPT = """
너는 병원 안내 시스템의 action 워커다.

사용자 원문:
{user_text}

너에게 주어진 작업:
제목: {title}
지시: {instruction}

규칙:
- 네 작업 범위 안에서만 답하라
- 짧고 명확하게 작성하라
- 추측성 병원 정보는 만들지 말고, 일반적인 행동 안내 중심으로 써라
- 3~5문장 이내로 작성하라
"""

AGGREGATOR_PROMPT = """
너는 병원 안내 시스템의 애그리게이터다.

사용자 원문:
{user_text}

아래는 여러 워커의 결과이다.
이 내용을 종합해서 사용자에게 보여줄 action 응답 초안을 작성하라.

워커 결과:
{worker_outputs}

규칙:
- 응답은 자연스러운 한국어로 작성
- 불필요하게 길지 않게 작성
- 행동 순서가 중요하면 1, 2, 3 단계처럼 정리
- 확실하지 않은 구체 병원 정보는 단정하지 말고 '안내 데스크에 확인'처럼 안전하게 표현
- 응답 초안만 출력
"""

FINALIZER_PROMPT = """
너는 병원 안내 시스템의 action 최종 응답 정리기다.

사용자 1차 질문:
{original_user_text}

시스템이 만든 1차 응답 초안:
{draft_answer}

사용자의 추가 답변:
{followup_answer}

너의 역할:
- 1차 질문, 초안, 추가 답변을 함께 반영해 더 정확한 최종 응답을 만든다.

규칙:
- 최종 응답은 자연스러운 한국어로 작성
- 추가 답변 내용을 적극 반영
- 너무 길지 않게 작성
- 행동 순서가 중요하면 순서 있게 정리
- 확실하지 않은 구체 병원 정보는 단정하지 말 것
- 최종 응답만 출력
"""
