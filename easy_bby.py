import httpx
import asyncio
from database import get_smile_cookie
from config import OWNER_ID

# --- ၁။ Cookie Status စစ်ဆေးပေးမည့် Function ---
async def check_cookie_validity(cookie_string, region="br"):
    """
    Cookie အလုပ်လုပ်၊ မလုပ် စစ်ဆေးပေးမည့် Function
    """
    url = f"https://www.smile.one/{region}/pay/get_product"
    headers = {
        "Cookie": cookie_string, 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            res_json = response.json()
            # Smile One ဘက်မှ status 200 ပြန်မှသာ Cookie အရှင်ဟု သတ်မှတ်မည်
            if res_json.get("status") == 200:
                return True, "Valid"
            else:
                return False, res_json.get("msg", "Expired")
        except Exception as e:
            return False, f"Connection Error: {str(e)}"

# --- ၂။ Smile One ထဲသို့ Gift Card လှမ်းဖြည့်ပေးမည့် Function ---
async def redeem_smile_giftcard(card_code, region, bot):
    current_cookie = await get_smile_cookie()
    
    if not current_cookie:
        return False, "Cookie မရှိသေးပါ။ Admin အား သတ်မှတ်ပေးရန် ပြောပါ။"

    url = f"https://www.smile.one/{region}/pay/giftcard_redeem"
    
    headers = {
        "Cookie": current_cookie,
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://www.smile.one/{region}/pay/giftcard",
        "X-Requested-With": "XMLHttpRequest" # ဒါက API response ရဖို့ အရေးကြီးပါတယ်
    }
    
    data = {"card_number": card_code}

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.post(url, headers=headers, data=data)
            
            # --- ၁။ Response က JSON ဟုတ်မဟုတ် အရင်စစ်မယ် ---
            if "application/json" not in response.headers.get("content-type", ""):
                return False, "❌ Smile One ဘက်မှ Block ထားပါသည်။ ၁၅ မိနစ်ခန့်စောင့်ပြီးမှ ပြန်စမ်းပါ။"

            res_json = response.json()
            status = res_json.get("status")
            msg = res_json.get("msg", "").lower()
            
            # --- ၂။ Cookie သက်တမ်းကုန်ခြင်း စစ်ဆေးခြင်း ---
            if status == 101 or "login" in msg or "limit" in msg:
                await bot.send_message(
                    OWNER_ID, 
                    "⚠️ <b>Cookie Alert!</b>\nSmile One Cookie သက်တမ်းကုန်သွားပါပြီ။",
                    parse_mode="HTML"
                )
                return False, "❌ Cookie သက်တမ်းကုန်သွားသဖြင့် Admin အား အကြောင်းကြားထားပါသည်။"

            # --- ၃။ အောင်မြင်မှု စစ်ဆေးခြင်း ---
            if status == 200:
                amount = res_json.get("amount", "Success")
                return True, amount
            
            # --- ၄။ Code အမှားများ ---
            else:
                return False, "❌ Code မမှန်ပါ သို့မဟုတ် အသုံးပြုပြီးသား ဖြစ်နေသည်။"

        except httpx.HTTPError as e:
            return False, f"🌐 Network Error: ဆာဗာနှင့် ချိတ်ဆက်၍မရပါ။"
        except Exception as e:
            # line 1 column 1 error ကို ဒီနေရာမှာ ဖမ်းလိုက်ပါမယ်
            return False, f"❌ Parsing Error: Smile One ဘက်မှ မှားယွင်းသော Data ပေးပို့လာသည်။"

# --- ၃။ UC ဝယ်ယူသည့် Function ---
async def buy_voucher_smile(item_id):
    current_cookie = await get_smile_cookie()
    if not current_cookie:
        return "error", "Cookie မရှိသေးပါ။"
    
    # ဝယ်ယူမှု API logic များကို ဤနေရာတွင် ဆက်လက်ရေးသားရန်
    return "success", "ABC-123-VOUCHER"
