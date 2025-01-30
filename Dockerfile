FROM python:3.11-slim

# Tells Python not to write .pyc (keeps container clean and consistent)
ENV PYTHONDONTWRITEBYTECODE 1
# Tells Python to flush the stdout and stderr streams after each write. (latest messages will be in the logs for debugging)
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Update system dependencies and install PostgreSQL client
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry as it is used in the project to manage dependencies
RUN pip install poetry

# Copy poetry dependencies
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create virtual environment as in the container no need to create virtual environment.s
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy project
COPY . .

# Run gunicorn
CMD ["poetry", "run", "gunicorn", "portfolio.wsgi:application", "--bind", "0.0.0.0:8000"]
