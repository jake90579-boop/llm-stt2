import re
from difflib import SequenceMatcher
from typing import List


LOCATION_TERMS = [
    "화장실",
    "원무과",
    "엘리베이터",
    "응급실",
    "정형외과",
    "내과",
    "외과",
    "소아과",
    "이비인후과",
    "가정의학과",
    "접수처",
    "수납처",
    "약국",
    "주사실",
    "진료실",
]

SYMPTOM_TERMS = [
    "복통",
    "두통",
    "발열",
    "기침",
    "어지럼",
    "호흡곤란",
    "구토",
    "설사",
    "흉통",
    "인후통",
]

DOMAIN_TERMS = LOCATION_TERMS + SYMPTOM_TERMS


def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def find_best_match(token: str, dictionary: List[str], threshold: float = 0.72) -> str:
    best_word = token
    best_score = 0.0

    for word in dictionary:
        score = similarity(token, word)
        if score > best_score:
            best_score = score
            best_word = word

    if best_score >= threshold:
        return best_word

    return token


def correct_joined_text(text: str) -> str:
    """
    문장 전체에서 공백 제거 형태까지 같이 비교해서
    '화장 실', '엘리 베이터' 같은 오인식을 교정하기 위한 함수.
    """
    compact = re.sub(r"\s+", "", text)

    best_word = compact
    best_score = 0.0

    for word in DOMAIN_TERMS:
        score = similarity(compact, word)
        if score > best_score:
            best_score = score
            best_word = word

    if best_score >= 0.78:
        return best_word

    return text


def correct_token_level(text: str) -> str:
    """
    공백 기준으로 나눈 뒤 각 토큰을 사전과 비교해서 교정.
    """
    tokens = text.split()
    corrected = [find_best_match(tok, DOMAIN_TERMS) for tok in tokens]
    return " ".join(corrected)


def postprocess_stt_text(text: str) -> str:
    text = normalize_text(text)

    if not text:
        return text

    # 1차: 전체 문장을 붙여서 병원 단어 하나로 인식 가능한지 확인
    corrected_whole = correct_joined_text(text)

    # 문장 전체가 하나의 도메인 단어에 매우 가까우면 바로 반환
    if corrected_whole in DOMAIN_TERMS:
        return corrected_whole

    # 2차: 토큰 단위 보정
    corrected_token = correct_token_level(text)
    return corrected_token
