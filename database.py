from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client['pubg_vouch_db']
users_col = db['users']

async def get_user(user_id):
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        user = {"user_id": user_id, "balance": 0.0}
        await users_col.insert_one(user)
    return user

async def update_balance(user_id, amount):
    await users_col.update_one(
        {"user_id": user_id}, 
        {"$inc": {"balance": round(amount, 2)}}, 
        upsert=True
    )

# database.py ထဲမှာ ထပ်ဖြည့်ပါ
settings_col = db['settings']

async def set_smile_cookie(cookie_string):
    await settings_col.update_one(
        {"id": "smile_config"},
        {"$set": {"cookie": cookie_string}},
        upsert=True
    )

async def get_smile_cookie():
    data = await settings_col.find_one({"id": "smile_config"})
    return data['cookie'] if data else ""

# database.py ထဲတွင်
admins_col = db['admins'] # Admin စာရင်းသိမ်းမည့်နေရာ

async def add_admin(user_id: int):
    await admins_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

async def is_authorized(user_id: int):
    from config import OWNER_ID
    # Owner ဆိုရင် အမြဲတမ်း Authorized ဖြစ်တယ်
    if user_id == OWNER_ID:
        return True
    # DB ထဲမှာ Admin ရှိမရှိ စစ်တယ်
    admin = await admins_col.find_one({"user_id": user_id})
    return admin is not None

# database.py ထဲတွင်
async def add_balance(user_id: int, amount: float):
    """User ၏ balance ကို တိုးပေးရန် (မရှိသေးလျှင် အသစ်ဆောက်ပေးမည်)"""
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True
    )
    # နောက်ဆုံး လက်ကျန်ငွေကို ပြန်ယူရန်
    user = await users_col.find_one({"user_id": user_id})
    return user['balance']
