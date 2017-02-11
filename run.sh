#!/bin/bash
# run main script in virtualenv
mydir=$(dirname $0)
cd "$mydir"
. venv/bin/activate
python manager.py $@
