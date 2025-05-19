#!/bin/sh
     cd /opt/journalapi
     . /opt/journalapi/venv/bin/activate
     exec gunicorn -w 3 -b 0.0.0.0:8000 "journalapi:create_app()"