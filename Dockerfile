FROM python:3.11-slim

# Prevent Python from writing pyc files and enable real-time logs.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container.
WORKDIR /app

# Copy dependency file first to improve Docker layer caching.
COPY requirements.txt /app/

# Install Python dependencies.
RUN pip install --upgrade pip \
    && pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --timeout 100

# Copy project files.
COPY . /app/

# Make entrypoint executable.
RUN chmod +x /app/entrypoint.sh

# Expose Django port.
EXPOSE 8000

# Run the entrypoint script.
CMD ["/app/entrypoint.sh"]