FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt ./

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 4000 to allow communication to/from the container
EXPOSE 4000

# Set environment variables
ENV FLASK_APP=app.py

# Run the application
CMD ["python", "app.py"]