FROM python:3.11-slim

# Prevent Python from writing pyc files and keep logs visible.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy dependency file first for better Docker cache usage.
COPY requirements.txt /app/

# Install project dependencies using a stable mirror.
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --timeout 100 \
    --retries 10

# Copy project files.
COPY . /app/

# Make entrypoint executable.
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]