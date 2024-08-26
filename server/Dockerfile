# Use the official Python image from the Docker Hub
FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 

# Set the working directory
WORKDIR /app

RUN pip install --upgrade setuptools
RUN pip install --upgrade pip

# Copy the requirements file
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "main.py"]