# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables for non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages (MySQL client for Python)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && pip install paho-mqtt mysql-connector-python \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./recorder /app

# Run the Python script when the container launches
CMD ["python", "owntracks_mqtt_to_mysql.py"]
