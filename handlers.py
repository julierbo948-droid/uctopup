import re
from aiogram import types, F
from config import OWNER_ID
from database import (
    get_user, update_balance, add_admin, 
    is_authorized, add_balance, users_col, set_smile_cookie
)
from packages import UC_PACKAGES
from easy_bby import buy_voucher_smile, redeem_smile_giftcard

# --- ၁။ Authorization Check (Admin/Owner စစ်ဆေးခြင်း) ---
async def check_auth(user_id: int):
    # Owner ဆိုရင် အမြဲတမ်း OK
    if user_id == OWNER_ID:
        return True
    # DB ထဲမှာ Admin အဖြစ် ရှိမရှိ စစ်မယ်
    return await is_authorized(user_id)

# --- ၂။ Start Handler ---
async def start_handler(message: types.Message):
    user = await get_user(message.from_user.id)
    text = (f"🎮 <b>PUBG UC Voucher Bot</b>\n\n"
            f"👤 User: {message.from_user.full_name}\n"
            f"💰 Balance: {user['balance']}$\n\n"
            f"📌 <b>Commands:</b>\n"
            f"• <code>.buy [item_id]</code> - UC ဝယ်ယူရန်\n"
            f"• <code>.topup [code] [region]</code> - Smile One ထဲ ငွေဖြည့်ရန်")
    await message.reply(text, parse_mode="HTML")

# --- ၃။ Cookie Set Handler (Owner Only) ---
async def set_cookie_handler(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ Owner သာလျှင် Cookie ပြောင်းလဲနိုင်ပါသည်။")

    try:
        new_cookie = message.text.split(maxsplit=1)[1]
        await set_smile_cookie(new_cookie)
        await message.reply("✅ Smile One Cookie Updated!")
    except IndexError:
        await message.reply("💡 Usage: <code>.setcookie [cookie_string]</code>")

# --- ၄။ Add Admin Handler (Owner Only) ---
async def add_admin_handler(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ Owner သာလျှင် Admin ထည့်သွင်းနိုင်ပါသည်။")

    try:
        parts = message.text.split()
        if len(parts) < 2: return await message.reply("💡 Usage: <code>.add [user_id]</code>")
        
        new_admin_id = int(parts[1])
        await add_admin(new_admin_id)
        await message.reply(f"✅ User ID: <code>{new_admin_id}</code> Is Now Admin!")
    except ValueError:
        await message.reply("❌ ID must be a number.")

# --- ၅။ Auto Topup Handler (Smile One Direct Redeem) ---
async def topup_handler(message: types.Message):
    # Admin ဖြစ်မှ သုံးခွင့်ပေးမည်
    if not await check_auth(message.from_user.id):
        return await message.reply("❌ No Permission. Admin မှ ခွင့်ပြုထားသူသာ သုံးနိုင်ပါသည်။")

    try:
        parts = message.text.split()
        # Format: .topup CODE REGION (ဥပမာ: .topup ABC123BR BR)
        if len(parts) < 3:
            return await message.reply("💡 Usage: <code>.topup [code] [region]</code>\nExample: <code>.topup XXXX BR</code>", parse_mode="HTML")
        
        card_code = parts[1]
        region = parts[2].lower()

        loading = await message.reply(f"⏳ Smile One ({region.upper()}) သို့ ငွေဖြည့်နေပါသည်...")

        # easy_bby ထဲမှ logic ကို လှမ်းခေါ်ခြင်း
        success, result = await redeem_smile_giftcard(card_code, region)

        if success:
            # Smile One မှာ အောင်မြင်ရင် result ထဲမှာ ပါလာတဲ့ point ကို ယူမယ်
            # အကယ်၍ result က amount မဟုတ်ခဲ့ရင် manual တိုးပေးရပါမယ်
            added_amount = float(result) if result else 0 
            await add_balance(message.from_user.id, added_amount)
            
            await loading.edit_text(f"✅ <b>Smile One Redeem Success!</b>\n💰 Added: {added_amount}$ to your account.", parse_mode="HTML")
        else:
            if "used" in result.lower() or "not found" in result.lower() or "invalid" in result.lower():
                await loading.edit_text("❌ Code မမှန်ပါ သို့မဟုတ် အသုံးပြုပြီးသား ဖြစ်နေသည်။")
            else:
                await loading.edit_text(f"❌ {result}")

    except Exception as e:
        await message.reply(f"❌ System Error: {str(e)}")

# --- ၆။ Buy Handler (Admin Only) ---
async def buy_handler(message: types.Message):
    if not await check_auth(message.from_user.id):
        return await message.reply("❌ No Permission.")

    match = re.search(r"^[./]buy\s+(\d+)", message.text)
    if not match: return
    
    item_id = match.group(1)
    if item_id not in UC_PACKAGES:
        return await message.reply("❌ Invalid Item ID!")

    user = await get_user(message.from_user.id)
    pkg = UC_PACKAGES[item_id]

    if user['balance'] < pkg['price']:
        return await message.reply(f"❌ Balance မလုံလောက်ပါ။\nလိုအပ်သည်: {pkg['price']}$")

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
        await loading.edit_text(f"❌ Smile One Error: {result}")
