# Base image with Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all local files
COPY vertex_pipeline_runner.py /app/vertex_pipeline_runner.py
COPY requirements.txt /app/requirements.txt



# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables (if needed)
ENV PYTHONUNBUFFERED=1

# Default run command
CMD ["python", "vertex_pipeline_runner.py"]
