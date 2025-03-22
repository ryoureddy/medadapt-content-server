FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for database
RUN mkdir -p /data
VOLUME /data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/data/medadapt_content.db

# Expose port if needed for future API server functionality
EXPOSE 8080

# Command to run the server
CMD ["python", "content_server.py"] 