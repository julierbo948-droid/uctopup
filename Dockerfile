# Python 3.10-slim version ကို သုံးပါမယ် (Image size သေးအောင်လို့ပါ)
FROM python:3.10-slim

# လုပ်ငန်းခွင် directory ကို သတ်မှတ်မယ်
WORKDIR /app

# လိုအပ်တဲ့ system tools အချို့ကို install လုပ်မယ်
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt ကို အရင် copy ကူးပြီး library တွေ install လုပ်မယ်
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ကျန်တဲ့ code ဖိုင်အားလုံးကို copy ကူးမယ်
COPY . .

# Bot ကို စတင် run မယ့် command
CMD ["python", "main.py"]
