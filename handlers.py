import re
import types
from aiogram import types, F
from database import get_user, update_balance
from packages import UC_PACKAGES
from easy_bby import buy_voucher_smile
from database import add_admin, is_authorized
from database import redeem_voucher, users_col
from config import OWNER_ID

async def is_authorized(user_id: int):
    from config import OWNER_ID
    # Owner ID ဖြစ်နေရင် True ပေးမယ်
    return user_id == OWNER_ID

async def start_handler(message: types.Message):
    user = await get_user(message.from_user.id)
    text = (f"🎮 <b>PUBG UC Voucher Bot</b>\n\n"
            f"👤 User: {message.from_user.full_name}\n"
            f"💰 Balance: {user['balance']}$\n\n"
            f"📌 <b>Commands:</b>\n"
            f"• <code>.buy [item_id]</code> - UC ဝယ်ယူရန်\n"
            f"• <code>.topup [code]</code> - ငွေဖြည့်ရန်")
    await message.reply(text, parse_mode="HTML")

from database import set_smile_cookie
from config import OWNER_ID

async def set_cookie_handler(message: types.Message):
    # Owner စစ်ဆေးခြင်း
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ သင်သည် Admin မဟုတ်ပါ။")

    # Command Format: .setcookie session_id=xxx;...
    try:
        new_cookie = message.text.split(maxsplit=1)[1]
        await set_smile_cookie(new_cookie)
        await message.reply("✅ Smile One Cookie ကို အောင်မြင်စွာ Update လုပ်ပြီးပါပြီ။")
    except IndexError:
        await message.reply("💡 Usage: <code>.setcookie [cookie_string]</code>", parse_mode="HTML")

async def add_admin_handler(message: types.Message):
    # Owner တစ်ယောက်တည်းသာ Admin အသစ် ထည့်ခွင့်ရှိမည်
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ Owner သာလျှင် Admin အသစ် ထည့်သွင်းနိုင်ပါသည်။")

    try:
        # Command ပုံစံ: .add 12345678
        parts = message.text.split()
        if len(parts) < 2:
            return await message.reply("💡 Usage: <code>.add [user_id]</code>", parse_mode="HTML")
        
        new_admin_id = int(parts[1])
        await add_admin(new_admin_id)
        await message.reply(f"✅ User ID: <code>{new_admin_id}</code> ကို Admin အဖြစ် ထည့်သွင်းပြီးပါပြီ။", parse_mode="HTML")
    except ValueError:
        await message.reply("❌ User ID သည် ကိန်းဂဏန်း (Number) သာ ဖြစ်ရပါမည်။")

async def buy_handler(message: types.Message):
    if not await is_authorized(message.from_user.id):
        return await message.reply("❌ သင်သည် ခွင့်ပြုချက်ရထားသော User မဟုတ်ပါ။ Admin အား ဆက်သွယ်ပါ။")
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

# handlers.py ထဲတွင်
from aiogram import types
from database import add_balance, is_authorized
from config import OWNER_ID

# handlers.py ထဲတွင်
from database import redeem_voucher

async def topup_handler(message: types.Message):
    # Admin ဖြစ်မှ သုံးခွင့်ပေးမည်
    if not await is_authorized(message.from_user.id):
        return await message.reply("❌ သင်သည် ခွင့်ပြုချက်ရထားသော User မဟုတ်ပါ။ Admin အား ဆက်သွယ်ပါ။")

    try:
        parts = message.text.split()
        if len(parts) < 2:
            return await message.reply("💡 Usage: <code>.topup [voucher_code]</code>", parse_mode="HTML")
        
        voucher_code = parts[1].upper()
        amount, error = await redeem_voucher(message.from_user.id, voucher_code)
        
        if error:
            return await message.reply(error)
        
        await message.reply(f"✅ Redeem Successful! 💰 {amount:,} $ ထည့်သွင်းပြီးပါပြီ။")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
# handlers.py ထဲတွင် Admin အတွက်
async def gen_voucher_handler(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return # Owner မဟုတ်ရင် ဘာမှပြန်မလုပ်ပါ

    try:
        # .gen CODE AMOUNT
        parts = message.text.split()
        code, amount = parts[1].upper(), float(parts[2])
        
        from database import vouchers_col
        await vouchers_col.insert_one({"code": code, "amount": amount, "status": "unused"})
        await message.reply(f"🎫 Voucher <code>{code}</code> သိမ်းပြီးပါပြီ။")
    except:
        await message.reply("💡 Usage: <code>.gen [code] [amount]</code>")
