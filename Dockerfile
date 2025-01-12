# Use the official Python image as the base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app

# Expose port 8000 for the app
EXPOSE 8000

# Run the app using Chainlit and bind it to port 8000
CMD ["chainlit", "run", "--port", "8000"]

