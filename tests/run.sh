#!/usr/bin/env bash

#export PYTHONPATH=/root/.pyenv/versions/3.8.19/lib/python3.8/site-packages:/config/apps/
#export PYTHONPATH=/root/venv3.12/lib/python3.12/site-packages:/config/appdaemon/apps:/root/appdaemon/appdaemon
#export PYTHONPATH=/root/venv3.12/lib/python3.12/site-packages:/config/appdaemon/apps:/root/appdaemon/appdaemon/tmp:/root/appdaemon/appdaemon/plugins/hass
#export PYTHONPATH=/addon_configs/a0d7b954_appdaemon/apps:/root/appdaemon/appdaemon/tmp:/root/appdaemon/appdaemon/plugins/hass

ad_dir='/root/appdaemon/appdaemon'

if [[ ! -d $ad_dir ]]; then
	mkdir $ad_dir/tmp
fi

cp $ad_dir/adapi.py $ad_dir/tmp

export PYTHONPATH=/addon_configs/a0d7b954_appdaemon/apps:$ad_dir/tmp:/root/appdaemon/appdaemon/plugins/hass
export PYTEST_ASYNCIO_DEFAULT_FIXTURE_LOOP_SCOPE=function

find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# pytest ./test_automation.py --verbose --showlocals $*
# sleep 5
#pytest ./test_alarms.py --verbose --showlocals $*
# sleep 5
# pytest ./test_announcer.py --verbose --showlocals $*

pytest ./test_test.py --verbose --showlocals $*

