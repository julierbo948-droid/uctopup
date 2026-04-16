import re
from aiogram import types, F
from database import get_user, update_balance
from packages import UC_PACKAGES
from easy_bby import buy_voucher_smile

async def start_handler(message: types.Message):
    user = await get_user(message.from_user.id)
    text = (f"🎮 <b>PUBG UC Voucher Bot</b>\n\n"
            f"👤 User: {message.from_user.full_name}\n"
            f"💰 Balance: {user['balance']}$\n\n"
            f"📌 <b>Commands:</b>\n"
            f"• <code>.buy [item_id]</code> - UC ဝယ်ယူရန်\n"
            f"• <code>.topup [code]</code> - ငွေဖြည့်ရန်")
    await message.reply(text, parse_mode="HTML")

async def buy_handler(message: types.Message):
    match = re.search(r"^[./]buy\s+(\d+)", message.text)
    if not match: return
    
    item_id = match.group(1)
    if item_id not in UC_PACKAGES:
        return await message.reply("❌ Invalid Item ID!")

    user = await get_user(message.from_user.id)
    pkg = UC_PACKAGES[item_id]

    if user['balance'] < pkg['price']:
        return await message.reply(f"❌ လက်ကျန်ငွေမလုံလောက်ပါ။\nလိုအပ်သည်: {pkg['price']}$")

    loading = await message.reply(f"⏳ {pkg['name']} ဝယ်ယူနေပါသည်...")
    status, result = await buy_voucher_smile(item_id)

    if status == "success":
        await update_balance(message.from_user.id, -pkg['price'])
        await loading.edit_text(
            f"✅ <b>ဝယ်ယူမှုအောင်မြင်သည်!</b>\n\n"
            f"📦 Item: {pkg['name']}\n"
            f"🎫 Code: <code>{result}</code>\n\n"
            f"<i>Midasbuy တွင် Redeem လုပ်ပါ။</i>", parse_mode="HTML"
        )
    else:
        await loading.edit_text(f"❌ Error: {result}")
