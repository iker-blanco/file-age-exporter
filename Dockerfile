FROM python:3.11-slim

USER root
# Set the working directory
WORKDIR /app

# Copy the Python script and configuration file
COPY exporter.py .

# Install required Python packages
RUN pip install prometheus_client boto3 PyYAML

CMD [ "python3" , "./exporter.py" ]