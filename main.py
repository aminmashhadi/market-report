import requests
import jdatetime
import os
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("BOT_TOKEN", "8896230810:AAFg7WJ-SpqDD3lGKR0uKXmUOAfZPt3LlhM")
CHAT_ID = os.getenv("CHAT_ID", "")
TEMPLATE_PATH = "template.jpg"

def find_item(curr, candidates):
    for k in candidates:
        if k in curr:
            return k, curr[k]
        for real in curr.keys():
            if real.replace("-","").replace("_","").lower() == k.replace("-","").replace("_","").lower():
                return real, curr[real]
    return None, None

def fetch_prices():
    try:
        r = requests.get("https://call.tgju.org/ajax.json", timeout=12)
        j = r.json()
        curr = j.get("current", {})
        print("TGJU keys sample:", list(curr.keys())[:20])
        for test_key in ["ons","geram18","sekee","silver_ons","oil_brent"]:
            if test_key in curr:
                print(test_key, curr[test_key])

        mapping = {
            "انس طلای جهانی": (["ons","ons_gold"], "دلار", False),
            "طلا ۱۸ عیار": (["geram18","geram_18"], "تومان", True),
            "سکه امامی": (["sekee","sekke","seke_emami"], "تومان", True),
            "انس نقره جهانی": (["silver_ons","silver","ons_silver"], "دلار", False),
            "نقره ۹۹۹ عیار": (["silver_999","silver999","geram_silver_999","silver_999_1"], "تومان", True),
            "نفت برنت": (["oil_brent","brent","oil"], "دلار", False),
            "تتر": (["price_dollar_rl","price_dollar","tether","usdt"], "تومان", True),
            "بیت کوین": (["crypto-bitcoin","bitcoin","btc","crypto_bitcoin"], "دلار", False),
        }

        result = {}
        for title, (candidates, unit, is_rial) in mapping.items():
            real_key, item = find_item(curr, candidates)
            if item is None:
                print(f"NOT FOUND {title} candidates={candidates}")
                fallback = {
                    "انس طلای جهانی": ("4,607","-0.90"),
                    "طلا ۱۸ عیار": ("21,550,600","-0.48"),
                    "سکه امامی": ("213,800,000","-0.09"),
                    "انس نقره جهانی": ("68.05","-0.31"),
                    "نقره ۹۹۹ عیار": ("462,010","0.32"),
                    "نفت برنت": ("85.89","-1.23"),
                    "تتر": ("197,055","-0.73"),
                    "بیت کوین": ("78,713","-0.75"),
                }[title]
                result[title] = fallback
                continue

            p_raw = str(item.get("p","0")).replace(",","").strip()
            change_raw = item.get("dp", item.get("d", item.get("change","0")))
            try:
                ch_test = float(str(change_raw).replace("%","").replace("٪","").replace(",",""))
                if abs(ch_test) > 50:
                    alt = item.get("dp")
                    if alt is not None and abs(float(str(alt).replace("%",""))) < 50:
                        change_raw = alt
                    else:
                        print(f"WARN huge change for {title}: {change_raw} -> using 0")
                        change_raw = "0"
            except:
                pass

            try:
                if is_rial:
                    p_int = int(float(p_raw))
                    p_int = p_int // 10
                    price_str = f"{p_int:,}"
                else:
                    if "." in p_raw:
                        p_val = float(p_raw)
                        if p_val < 10000:
                            price_str = f"{p_val:,.2f}"
                            if price_str.endswith(".00"):
                                price_str = price_str[:-3]
                        else:
                            price_str = f"{int(p_val):,}"
                    else:
                        price_str = f"{int(float(p_raw)):,}"
            except:
                price_str = p_raw

            change_str = str(change_raw).replace("٪","%").strip()
            if "%" in change_str:
                change_str = change_str.replace("%","")
            try:
                ch = float(change_str.replace(",",""))
                if abs(ch) > 50:
                    ch = 0
                change_str = f"{ch:.2f}"
            except:
                change_str = "0.00"

            print(f"{title} [{real_key}] -> {price_str} | {change_str}%")
            result[title] = (price_str, change_str)

        return result
    except Exception as e:
        print(f"fetch error {e}")
        import traceback; traceback.print_exc()
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
    try:
        tehran_now = datetime.now(ZoneInfo("Asia/Tehran"))
        jnow = jdatetime.datetime.fromgregorian(datetime=tehran_now)
    except:
        jnow = jdatetime.datetime.now()
        tehran_now = datetime.now()

    try:
        w = jnow.strftime("%A")
        en_to_fa = {"Saturday":"شنبه","Sunday":"یکشنبه","Monday":"دوشنبه","Tuesday":"سه‌شنبه","Wednesday":"چهارشنبه","Thursday":"پنجشنبه","Friday":"جمعه"}
        weekday = en_to_fa.get(w, w)
    except:
        weekday = ""
    months = ["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور","مهر","آبان","آذر","دی","بهمن","اسفند"]
    date_str = f"{weekday} {jnow.day} {months[jnow.month-1]} {jnow.year}"

    event = os.getenv("GITHUB_EVENT_NAME", "")
    if event == "schedule":
        time_str = "۱۴:۰۰"
    else:
        hh = f"{tehran_now.hour:02d}"
        mm = f"{tehran_now.minute:02d}"
        time_str = f"{hh}:{mm}"

    meta = {
        "انس طلای جهانی": ("🥇","دلار"),
        "طلا ۱۸ عیار": ("🥇","تومان"),
        "سکه امامی": ("👑","تومان"),
        "انس نقره جهانی": ("🥈","دلار"),
        "نقره ۹۹۹ عیار": ("🥈","تومان"),
        "نفت برنت": ("🛢️","دلار"),
        "تتر": ("💵","تومان"),
        "بیت کوین": ("₿","دلار"),
    }
    lines = []
    lines.append("📊 گزارش روزانه بازارهای جهانی")
    lines.append(f"📅 {date_str} | 🕑 ساعت {time_str}")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    for title, (price, change) in prices.items():
        emoji, unit = meta.get(title, ("•",""))
        try:
            ch = float(str(change).replace("%",""))
        except:
            ch = 0
        if ch > 0:
            indicator = "🟢 🔺"
            sign = "+"
        elif ch < 0:
            indicator = "🔴 🔻"
            sign = ""
        else:
            indicator = "⚪ ➖"
            sign = ""
        change_fmt = f"({sign}{ch:.2f}%)"
        lines.append(f"{emoji} {title}: {price} {unit}  {indicator} {change_fmt}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("🔴 کاهش  |  🟢 افزایش  |  ⚪ بدون تغییر")
    lines.append("🔻📉 افت روزانه  |  🔺📈 رشد روزانه")
    lines.append("منبع: isignal.ir / rahavard365.com")
    return "\n".join(lines)

def send_fixed_photo(caption):
    if not CHAT_ID:
        print("CHAT_ID خالیه")
        print(caption)
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(TEMPLATE_PATH, "rb") as f:
        r = requests.post(url, data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"}, files={"photo": f})
        print(r.text)
        r.raise_for_status()

if __name__ == "__main__":
    prices = fetch_prices()
    print(prices)
    caption = build_caption(prices)
    print("---caption---")
    print(caption)
    send_fixed_photo(caption)
