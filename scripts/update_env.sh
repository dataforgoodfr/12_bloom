#!/bin/bash
export APP_ENV=$1
export PATH_ENV=$2
/venv/bin/python3 -c "from bloom.config import settings"
export $(cat $2 | grep -v "#" | xargs -d '\r');