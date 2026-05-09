#!/bin/bash

cd /home/pc415-28/llm_package/interim || exit 1

if [ ! -d ".venv" ]; then
  python3 -m venv .venv || exit 1
fi

source .venv/bin/activate || exit 1

python -m pip install -U pip setuptools || exit 1
python -m pip install -e . || exit 1

python -m interim.main
