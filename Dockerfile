# Use a minimal base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose the port (Flask default or Gunicorn)
EXPOSE 8000

# Command to run the app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi:app"]
