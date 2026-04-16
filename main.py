import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from config import BOT_TOKEN
from handlers import start_handler, buy_handler

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register Handlers
    dp.message.register(start_handler, F.text.in_({"/start", ".start"}))
    dp.message.register(buy_handler, lambda m: m.text and m.text.startswith((".", "/")) and "buy" in m.text.lower())

    print("🚀 PUBG Voucher Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
