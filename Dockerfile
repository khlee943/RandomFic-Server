FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt ./

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# root certificate
COPY path/to/local/root.crt /root/.postgresql/root.crt

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

# Run the application with Gunicorn for better performance and scalability
CMD ["gunicorn", "run:app"]