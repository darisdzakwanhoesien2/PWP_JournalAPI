FROM python:3.13-alpine
WORKDIR /opt/journalapi
COPY . .
RUN pip install -r requirements.txt && \
    mkdir /opt/journalapi/instance && \
    chgrp -R root /opt/journalapi && \
    chmod -R g=u /opt/journalapi
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "journalapi:create_app()"]