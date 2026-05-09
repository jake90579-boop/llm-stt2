from pathlib import Path

MODEL_NAME = "gpt-4o-mini"

INPUT_DIR = Path("/home/pc415-28/llm_package/bus/mixed")
DONE_DIR = Path("/home/pc415-28/llm_package/bus/mixed_done")

DRAFT_DIR = Path("/home/pc415-28/llm_package/bus/mixed_draft")
INTERIM_TASK_DIR = Path("/home/pc415-28/llm_package/bus/interim_task")

FOLLOWUP_INPUT_DIR = Path("/home/pc415-28/llm_package/bus/mixed_followup")
FOLLOWUP_DONE_DIR = Path("/home/pc415-28/llm_package/bus/mixed_followup_done")
RESULT_DIR = Path("/home/pc415-28/llm_package/bus/mixed_result")
MAP_JSON_PATH = Path("/home/pc415-28/llm_package/knowledge/hospital_1f_map.json")
PENDING_FOLLOWUP_DIR = Path("/home/pc415-28/llm_package/bus/pending_followup")

POLL_INTERVAL = 0.5
STABLE_WAIT = 0.2
SKIP_EXISTING_ON_START = True

MAX_WORKERS = 5
WORKER_TIMEOUT = 60

ORCHESTRATOR_PROMPT = """
너는 병원 안내 시스템의 mixed 오케스트레이터다.

입력 문장은 action, location, symptom 중 두 가지 이상 의도가 섞인 복합 요청이다.
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
- tasks 개수는 2개 이상 {max_workers}개 이하
- 서로 다른 의도를 분리해서 다룰 수 있도록 작업을 설계할 것
- 질문이 복합적이어도 불필요하게 세분화하지 말 것
- 각 instruction은 서로 겹치지 않게 작성
- 설명 문장, 마크다운, 코드블록 없이 JSON만 출력
"""

WORKER_PROMPT = """
너는 병원 안내 시스템의 mixed 워커다.

사용자 원문:
{user_text}

맵 검색 결과:
{map_context}

너에게 주어진 작업:
제목: {title}
지시: {instruction}

규칙:
- 네 작업 범위 안에서만 답하라
- 짧고 명확하게 작성하라
- 맵 검색 결과가 있으면 그것을 우선 참고하라
- 병원 내부의 구체 정보는 모르면 지어내지 말라
- 의학적 진단을 단정하지 말라
- 일반적인 행동 안내, 위치 확인 방법, 증상 관련 안전 안내 중심으로 작성하라
- 3~5문장 이내로 작성하라
"""

AGGREGATOR_PROMPT = """
너는 병원 안내 시스템의 mixed 애그리게이터다.

사용자 원문:
{user_text}

맵 검색 결과:
{map_context}

아래는 여러 워커의 결과이다.
이 내용을 종합해서 mixed 응답 초안을 작성하라.

워커 결과:
{worker_outputs}

규칙:
- 응답은 자연스러운 한국어로 작성
- 맵 검색 결과가 있으면 그것을 우선 반영하라
- 복합 질문이면 한 번에 이해하기 쉽게 순서 있게 정리할 것
- 위치를 단정할 수 없으면 안내 데스크 확인처럼 안전하게 표현
- 의학적 진단처럼 단정하지 말 것
- 행동/위치/증상 안내가 함께 들어가도 읽기 쉽게 정리할 것
- 너무 길지 않게 작성
- 응답 초안만 출력
"""

FINALIZER_PROMPT = """
너는 병원 안내 시스템의 mixed 최종 응답 정리기다.

사용자 1차 질문:
{original_user_text}

맵 검색 결과:
{map_context}

시스템이 만든 1차 응답 초안:
{draft_answer}

사용자의 추가 답변:
{followup_answer}

너의 역할:
- 1차 질문, 맵 검색 결과, 초안, 추가 답변을 함께 반영해 더 정확한 최종 응답을 만든다.

규칙:
- 최종 응답은 자연스러운 한국어로 작성
- 맵 검색 결과가 있으면 그것을 우선 반영하라
- 추가 답변 내용을 적극 반영
- 행동/위치/증상 정보가 섞여 있어도 읽기 쉽게 정리
- 위치나 진단은 단정하지 말 것
- 너무 길지 않게 작성
- 최종 응답만 출력
"""
