#!/bin/bash
mkdir -p ../logs
python manage.py migrate
python manage.py sync_permission

python manage.py create_index_event
gunicorn --conf ./conf/gunicorn.conf.py api.wsgi
