import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from config import BOT_TOKEN
from handlers import (
    start_handler, 
    buy_handler, 
    set_cookie_handler, 
    topup_handler, 
    add_admin_handler,
    cookie_status_handler,
    help_handler
)

# Logging ကို သတ်မှတ်ခြင်း
logging.basicConfig(level=logging.INFO)

async def main():
    # Bot နှင့် Dispatcher ကို Initialise လုပ်ခြင်း
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # --- Handlers Register လုပ်ခြင်း ---

    # ၁။ Start Command (.start သို့မဟုတ် /start)
    dp.message.register(start_handler, F.text.in_({"/start", ".start"}))

    # ၂။ Admin အသစ်ထည့်သည့် Command (.add)
    dp.message.register(add_admin_handler, lambda m: m.text and m.text.startswith(".add"))

    # ၃။ Cookie သတ်မှတ်သည့် Command (.setcookie)
    dp.message.register(set_cookie_handler, lambda m: m.text and m.text.lower().startswith(".setcookie"))

    # ၄။ Voucher Code ဖြင့် ငွေဖြည့်သည့် Command (.topup)
    # Regex ကို သုံးပြီး register လုပ်တာ ပိုသေချာပါတယ်
    dp.message.register(topup_handler, F.text.regexp(r"(?i)^\.topup\s+[\w-]+"))

    dp.message.register(cookie_status_handler, lambda m: m.text and m.text.lower() == ".ck")

    dp.message.register(help_handler, lambda m: m.text and m.text.lower() == ".help")

    # ၅။ Admin အတွက် Voucher ထုတ်ပေးသည့် Command (.gen)
   # dp.message.register(gen_voucher_handler, lambda m: m.text and m.text.lower().startswith(".gen"))

    # ၆။ UC ဝယ်ယူသည့် Command (.buy သို့မဟုတ် /buy)
    dp.message.register(buy_handler, lambda m: m.text and m.text.lower().startswith((".", "/")) and "buy" in m.text.lower())

    # Bot စတင်လည်ပတ်ကြောင်း အကြောင်းကြားစာ
    print("🚀 PUBG Voucher Bot is running...")
    
    # Polling စတင်ခြင်း
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
