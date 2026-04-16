import httpx
import asyncio
from database import get_smile_cookie

# --- ၁။ Smile One ထဲသို့ Gift Card လှမ်းဖြည့်ပေးမည့် Function ---
async def redeem_smile_giftcard(card_code, region="br"):
    """
    Smile One Account ထဲသို့ Gift Card လှမ်းဖြည့်ပေးမည့် Logic
    """
    current_cookie = await get_smile_cookie()
    
    if not current_cookie:
        return False, "Cookie မရှိသေးပါ။ Admin အား သတ်မှတ်ပေးရန် ပြောပါ။"

    # Region အလိုက် URL ပြောင်းလဲနိုင်သည်
    url = f"https://www.smile.one/{region}/pay/giftcard_redeem"
    
    headers = {
        "Cookie": current_cookie,
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://www.smile.one/{region}/pay/giftcard",
        "Origin": "https://www.smile.one"
    }
    
    data = {
        "card_number": card_code
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, headers=headers, data=data)
            res_json = response.json()
            
            # Smile One တုံ့ပြန်ချက်ကို စစ်ဆေးခြင်း
            if res_json.get("status") == 200:
                # အောင်မြင်လျှင် ရရှိလာသည့် ပမာဏ (သို့မဟုတ်) အောင်မြင်ကြောင်းစာ ပြန်ပေးမည်
                amount = res_json.get("amount", "Success")
                return True, amount
            else:
                return False, res_json.get("msg", "Redeem Failed")
        except Exception as e:
            return False, f"Network Error: {str(e)}"

# --- ၂။ UC ဝယ်ယူသည့် Function ---
async def buy_voucher_smile(item_id):
    current_cookie = await get_smile_cookie()
    if not current_cookie:
        return "error", "Cookie မရှိသေးပါ။"

    url = "https://www.smile.one/br/pay/get_product" # နမူနာ URL
    # ဒီနေရာမှာ Smile One ရဲ့ ဝယ်ယူမှု API logic များကို ဆက်လက်ထည့်သွင်းရန်
    # ... (ဝယ်ယူမှု code များ) ...
    return "success", "ABC-123-VOUCHER" # နမူနာ ပြန်ပေးချက်
