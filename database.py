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
