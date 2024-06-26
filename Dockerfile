FROM python:3.9-slim

# Set environment variables here "ENV ...=..."

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt ./

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# COPY root.crt /root/.postgresql/root.crt

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=8080
# did dev on port 5000 changed from port 8080

# Expose the port the app runs on
EXPOSE 8080


# Run on localhost for now, for dev:
#CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
# Run the application with Gunicorn for better performance and scalability. for production
CMD ["gunicorn", "run:app", "--timeout", "300", "-w", "4"]