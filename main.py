import requests
import jdatetime
import os

TOKEN = os.getenv("BOT_TOKEN", "8896230810:AAFg7WJ-SpqDD3lGKR0uKXmUOAfZPt3LlhM") # حتما revoke کن و در Secret بذار
CHAT_ID = os.getenv("CHAT_ID", "")
TEMPLATE_PATH = "template.jpg" # همین عکسی که فرستادی - ثابت

def fetch_prices():
    try:
        r = requests.get("https://call.tgju.org/ajax.json", timeout=10)
        j = r.json()
        curr = j.get("current", {})
        def get(key, fallback_price, fallback_change):
            try:
                p = curr[key]['p'] # قیمت
                d = curr[key]['d'] # درصد
                # فرمت دهی با کاما
                price = f"{int(str(p).replace(',','')):,}"
                change = str(d)
                return price, change
            except:
                return fallback_price, fallback_change

        return {
            "انس طلای جهانی": get("ons", "4,607", "-0.90"),
            "طلا ۱۸ عیار": get("geram18", "21,550,600", "-0.48"),
            "سکه امامی": get("sekee", "213,800,000", "-0.09"),
            "انس نقره جهانی": get("silver_ons", "68.05", "-0.31"),
            "نقره ۹۹۹ عیار": get("silver_999", "462,010", "0.32"),
            "نفت برنت": get("oil_brent", "85.89", "-1.23"),
            "تتر": get("price_dollar_rl", "197,055", "-0.73"),
            "بیت کوین": get("crypto-bitcoin", "78,713", "-0.75"),
        }
    except Exception as e:
        print(f"fetch error {e}")
        return {
            "انس طلای جهانی": ("4,607", "-0.90"),
            "طلا ۱۸ عیار": ("21,550,600", "-0.48"),
            "سکه امامی": ("213,800,000", "-0.09"),
            "انس نقره جهانی": ("68.05", "-0.31"),
            "نقره ۹۹۹ عیار": ("462,010", "0.32"),
            "نفت برنت": ("85.89", "-1.23"),
            "تتر": ("197,055", "-0.73"),
            "بیت کوین": ("78,713", "-0.75"),
        }

def build_caption(prices):
    now = jdatetime.datetime.now()
    date_str = now.strftime("%A %d %B %Y")
    # واحدها
    units = {
        "انس طلای جهانی": "دلار",
        "طلا ۱۸ عیار": "تومان",
        "سکه امامی": "تومان",
        "انس نقره جهانی": "دلار",
        "نقره ۹۹۹ عیار": "تومان",
        "نفت برنت": "دلار",
        "تتر": "تومان",
        "بیت کوین": "دلار",
    }
    lines = []
    lines.append("گزارش روز قیمت بازارهای جهانی")
    lines.append(f"{date_str} - ساعت ۱۴")
    lines.append("")
    for title, (price, change) in prices.items():
        unit = units.get(title, "")
        # درصد با علامت
        try:
            ch = float(str(change).replace("%",""))
            change_str = f"%{ch:+.2f}" if abs(ch) < 10 else f"%{ch:+.2f}"
            # فارسی: (-0.90%) -> (-۰.۹۰٪) نمیخوایم، همین انگلیسی بماند تا مرتب باشد
            change_str = f"({change_str})"
        except:
            change_str = f"({change}%)" if "%" not in str(change) else f"({change})"
        lines.append(f"{title}: {price} {unit} {change_str}")
    lines.append("")
    lines.append("منبع: isignal.ir / rahavard365.com")
    return "\n".join(lines)

def send_fixed_photo(caption):
    if not CHAT_ID:
        print("CHAT_ID خالیه - کپشن ساخته شد ولی ارسال نشد:")
        print(caption)
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(TEMPLATE_PATH, "rb") as f:
        r = requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": f})
        print(r.text)
        r.raise_for_status()
        print("ارسال شد")

if __name__ == "__main__":
    prices = fetch_prices()
    print(prices)
    caption = build_caption(prices)
    print("---caption---")
    print(caption)
    send_fixed_photo(caption)
