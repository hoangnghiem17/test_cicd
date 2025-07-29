# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
RUN poetry install

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["poetry", "run", "python", "app.py"] 