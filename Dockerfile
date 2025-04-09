# Dockerfile
FROM python:3.9-slim

# Prevent .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire repository into the container
COPY . /app/

# Ensure the instance folder exists
RUN mkdir -p /app/instance

EXPOSE 5000

# Run Gunicorn using wsgi.py as the entry point
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
