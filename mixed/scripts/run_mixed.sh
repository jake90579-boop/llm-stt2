#!/bin/bash

cd /home/pc415-28/llm_package/mixed || exit 1

if [ ! -d ".venv" ]; then
  python3 -m venv .venv || exit 1
fi

source .venv/bin/activate || exit 1

python -m pip install -U pip setuptools || exit 1
python -m pip install -e . || exit 1

if [ -z "$OPENAI_API_KEY" ]; then
  echo "[ERROR] OPENAI_API_KEY 환경변수가 설정되지 않았습니다."
  echo "예: export OPENAI_API_KEY=\"네_API_키\""
  exit 1
fi

python -m mixed.main
