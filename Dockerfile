FROM python:3.12-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    chromium chromium-driver \
    tesseract-ocr libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Optional: Set environment variables for Chrome (helps with Selenium)
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add your app code
COPY . /app
WORKDIR /app

# Default run command
CMD ["python", "main.py"]
