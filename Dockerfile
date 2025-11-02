# Dockerfile for Monarch Money MCP Server HTTP mode
# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/
COPY login_setup.py ./

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8080

# Environment variables for authentication (set these when running the container)
# ENV MONARCH_EMAIL=your-email@example.com
# ENV MONARCH_PASSWORD=your-password
# Or use MONARCH_TOKEN for direct token authentication

# Run the HTTP server
CMD ["python", "-m", "monarch_mcp_server.server", "--transport", "http", "--host", "0.0.0.0", "--port", "8080", "--path", "/mcp"]
