import httpx
from config import GOOGLE_EMAIL, GOOGLE_PASS, PUBG_PRODUCT_ID

SMILE_COOKIE = ""

async def auto_login_smile():
    global SMILE_COOKIE
    # ဤနေရာတွင် Playwright သို့မဟုတ် Request-based login logic ကိုထည့်ပါ
    # လောလောဆယ် cookie ကို manual ထည့်ထားသည်ဟု ယူဆပါသည်
    SMILE_COOKIE = "session_id=xxxx; user_token=yyyy"
    return True

async def buy_voucher_smile(item_id):
    global SMILE_COOKIE
    url = "https://www.smile.one/ph/pay/get_product"
    
    headers = {
        "Cookie": SMILE_COOKIE,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "product_id": PUBG_PRODUCT_ID,
        "item_id": item_id,
        "pay_type": "wallet"
    }

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, data=payload, headers=headers)
            res = r.json()
            
            # Check for Session Expiry
            if res.get("status") == 401:
                await auto_login_smile()
                headers["Cookie"] = SMILE_COOKIE
                r = await client.post(url, data=payload, headers=headers)
                res = r.json()

            if res.get("status") == 200:
                v_code = res.get("pin_code") or res.get("voucher")
                return "success", v_code
            return "fail", res.get("message", "Purchase Failed")
        except Exception as e:
            return "error", str(e)
