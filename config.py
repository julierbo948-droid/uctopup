import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
OWNER_ID = int(os.getenv("OWNER_ID"))
GOOGLE_EMAIL = os.getenv("GOOGLE_EMAIL")
GOOGLE_PASS = os.getenv("GOOGLE_PASS")

# Smile One PUBG Product ID
PUBG_PRODUCT_ID = "617"
