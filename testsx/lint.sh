#!/usr/bin/env bash

PYTHONPATH=/root/.pyenv/versions/3.8.19/lib/python3.8/site-packages

pylint test_automation.py --disable W0621,E0401
