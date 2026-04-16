import asyncio
from playwright.async_api import async_playwright
from config import GOOGLE_EMAIL, GOOGLE_PASS
from database import get_smile_cookie

SMILE_COOKIE = ""

async def buy_voucher_smile(item_id):
    # Database ထဲက လက်ရှိ Cookie ကို ယူမယ်
    current_cookie = await get_smile_cookie()
    
    if not current_cookie:
        return "error", "Cookie မရှိသေးပါ။ Admin အား သတ်မှတ်ပေးရန် ပြောပါ။"

    url = "https://www.smile.one/br/pay/get_product"
    headers = {
        "Cookie": current_cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    

async def auto_login_smile():
    global SMILE_COOKIE
    async with async_playwright() as p:
        # Browser ကို headless (မမြင်ရအောင်) ဖွင့်မယ်
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Smile One Login Page သို့သွားမယ်
            await page.goto("https://www.smile.one/ph/login")
            
            # Google Login Button ကိုနှိပ်မယ်
            await page.click("text=Google") 
            
            # Email ရိုက်မယ်
            await page.fill('input[type="email"]', GOOGLE_EMAIL)
            await page.click("#identifierNext")
            await asyncio.sleep(2)
            
            # Password ရိုက်မယ်
            await page.fill('input[type="password"]', GOOGLE_PASS)
            await page.click("#passwordNext")
            
            # Login အောင်မြင်သည်အထိ ခဏစောင့်မယ်
            await page.wait_for_url("https://www.smile.one/ph/", timeout=60000)
            
            # Cookie များကို ဆွဲထုတ်မယ်
            cookies = await context.cookies()
            SMILE_COOKIE = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            
            print("✅ Successfully retrieved Smile One Cookie!")
            return True
        except Exception as e:
            print(f"❌ Login Error: {e}")
            return False
        finally:
            await browser.close()
