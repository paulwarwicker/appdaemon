#!/usr/bin/env bash

export PYTHONPATH=/root/.pyenv/versions/3.8.19/lib/python3.8/site-packages:/config/apps/
pytest ./test_alarms.py --verbose --showlocals $*
#pytest ./test_utils.py --verbose --showlocals $* && pytest ./test_announcer.py --verbose --showlocals $*
#pytest ./test_automation.py --verbose --showlocals $*
