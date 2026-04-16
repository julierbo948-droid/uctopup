FROM python:3.10-slim

# Playwright အတွက် လိုအပ်တဲ့ dependencies တွေ install လုပ်ခြင်း
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxext6 \
    libxfixes3 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright Browser ကို Download ဆွဲခြင်း
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .
CMD ["python", "main.py"]
