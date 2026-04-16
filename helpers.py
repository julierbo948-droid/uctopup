from config import OWNER_ID
from aiogram import Bot

async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

async def notify_admin(bot: Bot, message: str):
    try:
        await bot.send_message(OWNER_ID, f"📢 <b>Admin Notification:</b>\n{message}", parse_mode="HTML")
    except Exception as e:
        print(f"Failed to notify admin: {e}")
