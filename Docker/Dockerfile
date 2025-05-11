FROM python:3.12-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    chromium chromium-driver \
    tesseract-ocr libtesseract-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Optional: Set environment variables for Chrome (helps with Selenium)
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Setup directories
WORKDIR /code
RUN rm -rf /code/*

# Default run command
CMD ["sh", "-c", "git clone -b $GIT_BRANCH https://github.com/$GIT_REPO.git /code && pip install -r /code/requirements.txt && python main.py"]
