FROM python:3.12-slim

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Create a non-root user
RUN groupadd -r mcpclient && useradd -r -g mcpclient mcpclient \
    && chown mcpclient:mcpclient /app

# Copy the project files
COPY --chown=mcpclient:mcpclient . .

# Install the project dependencies
RUN uv pip install --system .

# Switch to the non-root user
USER mcpclient

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "src.main"]
