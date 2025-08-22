# Use an official Python runtime as a parent image
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# --- Final Stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy the application code
COPY ./app ./app

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application using uvicorn
# Gunicorn is often used as a production-grade process manager
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]