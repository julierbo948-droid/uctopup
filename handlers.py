import re
from aiogram import types, F
from config import OWNER_ID
from database import (
    get_user, update_balance, add_admin, 
    is_authorized, add_balance, users_col, set_smile_cookie
)
from packages import UC_PACKAGES
from easy_bby import buy_voucher_smile, redeem_smile_giftcard, check_cookie_validity

# --- ၁။ Authorization Check ---
async def check_auth(user_id: int):
    if user_id == OWNER_ID:
        return True
    return await is_authorized(user_id)

# --- ၂။ Start Handler ---
async def start_handler(message: types.Message):
    user = await get_user(message.from_user.id)
    text = (f"🎮 <b>PUBG UC Voucher Bot</b>\n\n"
            f"👤 User: {message.from_user.full_name}\n"
            f"💰 Balance: {user['balance']}$\n\n"
            f"📌 <b>Commands:</b>\n"
            f"• <code>.help</code> - အသုံးပြုပုံကြည့်ရန်")
    await message.reply(text, parse_mode="HTML")

# --- ၃။ Cookie Status Handler (Owner Only) ---
# ဒီနေရာမှာ နာမည်ကို main.py က ခေါ်တဲ့အတိုင်း အတိအကျပေးထားပါတယ်
async def cookie_status_handler(message: types.Message):
    if message.from_user.id != OWNER_ID: 
        return

    from database import get_smile_cookie
    cookie = await get_smile_cookie()
    if not cookie:
        return await message.reply("❌ Database ထဲမှာ Cookie လုံးဝ မရှိသေးပါ။")
    
    success, msg = await check_cookie_validity(cookie)
    
    if success:
        status_text = "🟢 <b>Aᴄᴛɪᴠᴇ</b>"
        detail = "Smile One စနစ် ပုံမှန် အလုပ်လုပ်နေပါသည်။"
    else:
        status_text = "🔴 <b>Eхᴘɪʀᴇᴅ</b>"
        detail = f"Cookie သက်တမ်းကုန်သွားပါပြီ။"

    text = (f"📊 <b>Sᴍɪʟᴇ Oɴᴇ Cᴏᴏᴋɪᴇ Sᴛᴀᴛᴜs</b>\n\n"
            f"Sᴛᴀᴛᴜs: {status_text}\n"
            f"Iɴғᴏ: <i>{detail}</i>")
    await message.reply(text, parse_mode="HTML")

# --- ၄။ Help Handler ---
async def help_handler(message: types.Message):
    is_owner = message.from_user.id == OWNER_ID
    help_text = (
        "🛡️ <b>Aᴅᴍɪɴ Cᴏᴍᴍᴀɴᴅs</b>\n"
        "• <code>.topup [code] [reg]</code> - Auto Redeem\n"
        "• <code>.buy [item_id]</code> - Buy Voucher\n"
        "• <code>.start</code> - Check Balance\n\n"
    )
    if is_owner:
        help_text += (
            "👑 <b>Oᴡɴᴇʀ Cᴏᴍᴍᴀɴᴅs</b>\n"
            "• <code>.add [user_id]</code> - Add Admin\n"
            "• <code>.setcookie [val]</code> - Set Session\n"
            "• <code>.ck</code> - Cookie Status Check"
        )
    await message.reply(help_text, parse_mode="HTML")

# --- ၅။ Cookie Set Handler ---
async def set_cookie_handler(message: types.Message):
    # ၁။ Owner စစ်ဆေးခြင်း
    if message.from_user.id != OWNER_ID: 
        return await message.reply("❌ Only the Owner can set the Cookie.")

    # ၂။ Format စစ်ဆေးခြင်း
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: 
        return await message.reply("⚠️ **Usage format:**\n`.setcookie <Long_Main_Cookie>`")

    new_cookie = parts[1].strip()

    # ၃။ Database ထဲမှာ Cookie ကို သိမ်းခြင်း
    await set_smile_cookie(new_cookie)

    # ၄။ easy_bby ထဲက Cache များကို Reset လုပ်ခြင်း (အရေးကြီးသည်)
    import easy_bby
    easy_bby.GLOBAL_SCRAPER = None
    easy_bby.GLOBAL_CSRF = {
        'mlbb_br': None, 'mlbb_ph': None, 
        'mcc_br': None, 'mcc_ph': None,
        'pubgm_br': None, 'pubgm_ph': None # PUBG အတွက်ပါ ထည့်ထားလိုက်ပါ
    }

    await message.reply("✅ **Main Cookie has been successfully updated securely.**")

import re
from aiogram.enums import ParseMode

async def smart_cookie_handler(message: types.Message):
    # ၁။ Owner စစ်ဆေးခြင်း
    if message.from_user.id != OWNER_ID: 
        return await message.reply("❌ You are not authorized.")

    text = message.text
    # Smile One အတွက် လိုအပ်သော Cookie Keys များ
    target_keys = ["PHPSESSID", "cf_clearance", "__cf_bm", "_did", "_csrf"]
    extracted_cookies = {}

    try:
        # Regex သုံးပြီး Cookie key နဲ့ value များကို ရှာဖွေခြင်း
        for key in target_keys:
            pattern = rf"['\"]?{key}['\"]?\s*[:=]\s*['\"]?([^'\",;\s}}]+)['\"]?"
            match = re.search(pattern, text)
            if match:
                extracted_cookies[key] = match.group(1)

        # အဓိက လိုအပ်သော key များ ပါ/မပါ စစ်ဆေးခြင်း
        if "PHPSESSID" not in extracted_cookies or "cf_clearance" not in extracted_cookies:
            return await message.reply(
                "❌ <b>Error:</b> <code>PHPSESSID</code> နှင့် <code>cf_clearance</code> ကို ရှာမတွေ့ပါ။\n"
                "Format မှန်ကန်ကြောင်း စစ်ဆေးပါ။", 
                parse_mode=ParseMode.HTML
            )

        # Cookie String အဖြစ် ပြန်လည် တည်ဆောက်ခြင်း
        formatted_cookie_str = "; ".join([f"{k}={v}" for k, v in extracted_cookies.items()])
        
        # Database တွင် သိမ်းဆည်းခြင်း
        await set_smile_cookie(formatted_cookie_str)
        
        # easy_bby ထဲမှ Cache များကို Clear လုပ်ခြင်း
        import easy_bby
        easy_bby.GLOBAL_SCRAPER = None
        easy_bby.GLOBAL_CSRF = {'mlbb_br': None, 'mlbb_ph': None, 'mcc_br': None, 'mcc_ph': None}
        
        # အောင်မြင်ကြောင်း ပြန်ကြားစာ
        success_msg = "✅ <b>Cookies Successfully Extracted & Saved!</b>\n\n📦 <b>Extracted Data:</b>\n"
        for k, v in extracted_cookies.items():
            display_v = f"{v[:15]}...{v[-15:]}" if len(v) > 35 else v
            success_msg += f"🔸 <code>{k}</code> : {display_v}\n"
        
        success_msg += f"\n🍪 <b>Final String:</b>\n<code>{formatted_cookie_str}</code>"
        await message.reply(success_msg, parse_mode=ParseMode.HTML)

    except Exception as e:
        await message.reply(f"❌ <b>Parsing Error:</b> {str(e)}", parse_mode=ParseMode.HTML)

# --- ၆။ Add Admin Handler ---
async def add_admin_handler(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ Owner Only.")
    try:
        new_admin_id = int(message.text.split()[1])
        await add_admin(new_admin_id)
        await message.reply(f"✅ User {new_admin_id} is now Admin!")
    except:
        await message.reply("❌ Invalid ID.")

# --- ၇။ Topup Handler ---
async def topup_handler(message: types.Message):
    if not await check_auth(message.from_user.id):
        return await message.reply("❌ No Permission.")
    try:
        parts = message.text.split()
        if len(parts) < 3: return await message.reply("💡 Usage: <code>.topup [code] [region]</code>")
        
        success, result = await redeem_smile_giftcard(parts[1], parts[2].lower(), message.bot)
        if success:
            await add_balance(message.from_user.id, float(result))
            await message.reply(f"✅ Success! Added: {result}$")
        else:
            await message.reply(result)
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# --- ၈။ Buy Handler ---
async def buy_handler(message: types.Message):
    if not await check_auth(message.from_user.id):
        return await message.reply("❌ No Permission.")
    match = re.search(r"^[./]buy\s+(\d+)", message.text)
    if not match: return
    
    item_id = match.group(1)
    if item_id not in UC_PACKAGES: return await message.reply("❌ Invalid ID!")

    user = await get_user(message.from_user.id)
    pkg = UC_PACKAGES[item_id]
    if user['balance'] < pkg['price']: return await message.reply("❌ Not enough balance.")

    status, result = await buy_voucher_smile(item_id)
    if status == "success":
        await update_balance(message.from_user.id, -pkg['price'])
        await message.reply(f"✅ Success!\nCode: <code>{result}</code>", parse_mode="HTML")
    else:
        await message.reply(f"❌ Error: {result}")
