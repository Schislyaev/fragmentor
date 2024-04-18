#!/bin/sh

mkdir logs
export PYTHONPATH="${PYTHONPATH}:/opt/app"
python3.10 -m debugpy --listen 0.0.0.0:5678 --wait-for-client tg/main.py