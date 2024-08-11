#!/usr/bin/env bash

export PYTHONPATH=/root/.pyenv/versions/3.8.19/lib/python3.8/site-packages:/config/apps/

pytest ./test_automation.py --verbose --showlocals $*
sleep 5
pytest ./test_alarms.py --verbose --showlocals $*
sleep 5
pytest ./test_announcer.py --verbose --showlocals $*
