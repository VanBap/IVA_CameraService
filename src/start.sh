#!/bin/bash
echo ___________________Start___________________
mkdir -p ../logs
python manage.py create_index_event
python manage.py runserver 0.0.0.0:10026
