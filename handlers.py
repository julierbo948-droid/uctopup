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


@dp.message(F.text.regexp(r"(?i)^\.topup\s+([a-zA-Z0-9]+)"))
async def handle_topup(message: types.Message):
    if not await is_authorized(message.from_user.id): return await message.reply("ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀ.")
    match = re.search(r"(?i)^\.topup\s+([a-zA-Z0-9]+)", message.text.strip())
    if not match: return await message.reply("Usage format - `.topup <Code>`")
    activation_code = match.group(1).strip()
    tg_id = str(message.from_user.id)
    user_id_int = message.from_user.id 
    loading_msg = await message.reply(f"Checking Code `{activation_code}`...")
    
    async with user_locks[tg_id]:
        scraper = await easy_bby.get_main_scraper()
        from bs4 import BeautifulSoup
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Accept': 'text/html'}
        
        async def try_redeem(api_type):
            if api_type == 'PH':
                page_url = 'https://www.smile.one/ph/customer/activationcode'
                check_url = 'https://www.smile.one/ph/smilecard/pay/checkcard'
                pay_url = 'https://www.smile.one/ph/smilecard/pay/payajax'
                base_origin = 'https://www.smile.one'
                base_referer = 'https://www.smile.one/ph/'
                balance_check_url = 'https://www.smile.one/ph/customer/order'
            else:
                page_url = 'https://www.smile.one/customer/activationcode'
                check_url = 'https://www.smile.one/smilecard/pay/checkcard'
                pay_url = 'https://www.smile.one/smilecard/pay/payajax'
                base_origin = 'https://www.smile.one'
                base_referer = 'https://www.smile.one/'
                balance_check_url = 'https://www.smile.one/customer/order'

            req_headers = headers.copy()
            req_headers['Referer'] = base_referer

            try:
                res = await scraper.get(page_url, headers=req_headers)
                if "login" in str(res.url).lower() or res.status_code in [403, 503]: return "expired", None

                soup = BeautifulSoup(res.text, 'html.parser')
                csrf_token = soup.find('meta', {'name': 'csrf-token'})
                csrf_token = csrf_token.get('content') if csrf_token else (soup.find('input', {'name': '_csrf'}).get('value') if soup.find('input', {'name': '_csrf'}) else None)
                if not csrf_token: return "expired", None 

                ajax_headers = req_headers.copy()
                ajax_headers.update({'X-Requested-With': 'XMLHttpRequest', 'Origin': base_origin, 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})

                check_res_raw = await scraper.post(check_url, data={'_csrf': csrf_token, 'pin': activation_code}, headers=ajax_headers)
                check_res = check_res_raw.json()
                code_status = str(check_res.get('code', check_res.get('status', '')))
                
                card_amount = 0.0
                try:
                    if 'data' in check_res and isinstance(check_res['data'], dict):
                        val = check_res['data'].get('amount', check_res['data'].get('money', 0))
                        if val: card_amount = float(val)
                except: pass

                if code_status in ['200', '201', '0', '1'] or 'success' in str(check_res.get('msg', '')).lower():
                    old_bal = await easy_bby.get_smile_balance(scraper, headers, balance_check_url)
                    pay_res_raw = await scraper.post(pay_url, data={'_csrf': csrf_token, 'sec': activation_code}, headers=ajax_headers)
                    pay_res = pay_res_raw.json()
                    pay_status = str(pay_res.get('code', pay_res.get('status', '')))
                    
                    if pay_status in ['200', '0', '1'] or 'success' in str(pay_res.get('msg', '')).lower():
                        await asyncio.sleep(5) 
                        anti_cache_url = f"{balance_check_url}?_t={int(time.time())}"
                        new_bal = await easy_bby.get_smile_balance(scraper, headers, anti_cache_url)
                        bal_key = 'br_balance' if api_type == 'BR' else 'ph_balance'
                        added = round(new_bal[bal_key] - old_bal[bal_key], 2)
                        if added <= 0 and card_amount > 0: added = card_amount
                        return "success", added
                    else: return "fail", "Payment failed."
                else: return "invalid", "Invalid Code"
            except Exception as e: return "error", str(e)

        status, result = await try_redeem('BR')
        active_region = 'BR'
        if status in ['invalid', 'fail']: 
            status, result = await try_redeem('PH')
            active_region = 'PH'

        if status == "expired":
            await loading_msg.edit_text("⚠️ <b>Cookies Expired!</b>\n\nAuto-login စတင်နေပါသည်... ခဏစောင့်ပြီး ပြန်လည်ကြိုးစားပါ။", parse_mode=ParseMode.HTML)
            await notify_owner("⚠️ <b>Top-up Alert:</b> Code ဖြည့်သွင်းနေစဉ် Cookie သက်တမ်းကုန်သွားပါသည်။ Auto-login စတင်နေပါသည်...")
            success = await easy_bby.auto_login_and_get_cookie()
            if not success: await notify_owner("❌ <b>Critical:</b> Auto-Login မအောင်မြင်ပါ။ `/setcookie` ဖြင့် အသစ်ထည့်ပေးပါ။")
        elif status == "error": await loading_msg.edit_text(f"❌ Error: {result}")
        elif status in ['invalid', 'fail']: await loading_msg.edit_text("Cʜᴇᴄᴋ Fᴀɪʟᴇᴅ❌\n(Code is invalid or might have been used)")
        elif status == "success":
            added_amount = result
            if added_amount <= 0:
                await loading_msg.edit_text(f"sᴍɪʟᴇ ᴏɴᴇ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ sᴜᴄᴄᴇss ✅\n(Cannot retrieve exact amount due to System Delay.)")
            else:
                if user_id_int == OWNER_ID: fee_percent = 0.0
                else:
                    if added_amount >= 10000: fee_percent = 0.1
                    elif added_amount >= 5000: fee_percent = 0.15
                    elif added_amount >= 1000: fee_percent = 0.2
                    elif added_amount >= 1120: fee_percent = 0.2    
                    elif added_amount >= 300: fee_percent = 0.3 
                    else: fee_percent = 0.0

                fee_amount = round(added_amount * (fee_percent / 100), 2)
                net_added = round(added_amount - fee_amount, 2)
        
                user_wallet = await db.get_reseller(tg_id)
                if active_region == 'BR':
                    assets = user_wallet.get('br_balance', 0.0) if user_wallet else 0.0
                    await db.update_balance(tg_id, br_amount=net_added)
                else:
                    assets = user_wallet.get('ph_balance', 0.0) if user_wallet else 0.0
                    await db.update_balance(tg_id, ph_amount=net_added)

                total_assets = assets + net_added
                fmt_amount = int(added_amount) if added_amount % 1 == 0 else added_amount

                msg = (f"✅ <b>Code Top-Up Successful</b>\n\n<code>Code   : {activation_code} ({active_region})\nAmount : {fmt_amount:,}\nFee    : -{fee_amount:.1f} ({fee_percent}%)\nAdded  : +{net_added:,.1f} 🪙\nAssets : {assets:,.1f} 🪙\nTotal  : {total_assets:,.1f} 🪙</code>")
                await loading_msg.edit_text(msg, parse_mode=ParseMode.HTML)
