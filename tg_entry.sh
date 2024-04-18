#!/bin/sh

mkdir logs
export PYTHONPATH="${PYTHONPATH}:/opt/app"
python3.10 tg/main.py