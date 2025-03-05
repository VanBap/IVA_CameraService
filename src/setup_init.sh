#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR

python manage.py sync_attribute_config
python manage.py create_index_event
python manage.py create_super_admin
