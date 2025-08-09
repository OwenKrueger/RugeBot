# Use the official Python 3.12.10 image
# (built from Debian‑slim; you can pick alpine if you want an even smaller image)
FROM python:3.12.10-slim-bookworm AS base

# Create a non‑root user to run the app
RUN addgroup --gid 1000 appgroup && \
    adduser --uid 1000 --gid 1000 --disabled-password appuser

# Set work‑dir
WORKDIR /app

# Copy only the dependency files first
COPY requirements.txt .

# Copy dev env file
COPY live.env .

# Install dependencies in a virtualenv (optional but nice)
ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv "$VIRTUAL_ENV" && \
    . "$VIRTUAL_ENV/bin/activate" && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    # Clean up cache
    rm -rf /root/.cache

# Copy the rest of the code
COPY . .

# Use the virtualenv's Python
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Switch to the non‑root user
USER appuser

# Expose port if your app listens on one
# EXPOSE 8080   # Uncomment if you expose a port

# Default command
CMD ["python", "main.py"]