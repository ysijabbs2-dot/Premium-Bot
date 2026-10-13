#!/usr/bin/env python3
# Telegram shop bot — Termux / Render
# Install: pip install requests

import json
import os
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from html import escape
import requests

BOT_TOKEN = "8990644924:AAGUr2F-qRjEKC6WWPz_tRxdhordWPzunk4"
OWNER_ID = 8886164132
OWNER_USERNAME = "lv_oxyg3n"

DB_FILE = "shopbot.sqlite3"
API = "https://api.telegram.org/bot{}"
FILE_API = "https://api.telegram.org/file/bot{}"

# --- Render Port Binding (Free Web Service ke liye) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

    def log_message(self, format, *args):
        return  # Console me unnecessary HTTP logs hide karne ke liye

def start_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# Background thread me HTTP server start karo taaki Render timeout na de
threading.Thread(target=start_dummy_server, daemon=True).start()
# -----------------------------------------------------

LANGS = {
    "en": {
        "choose_lang": "Choose your language:",
        "share_contact": "Please share your phone number using the button below to continue.",
        "contact_btn": "📱 Share contact",
        "contact_needed": "Please use the Share contact button first.",
        "menu": "Welcome! Choose an option:",
        "buy_accounts": "📲 Telegram & WhatsApp services",
        "ff": "🎮 FF Panel",
        "make_bot": "🤖 Make Your Own Bot",
        "admin": "⚙️ Admin Panel",
        "back": "⬅️ Back",
        "telegram": "Telegram services",
        "whatsapp": "WhatsApp services",
        "main_id": "Main ID",
        "second_id": "Second ID",
        "free_panel": "Free Panel / Downloads",
        "support": "🆘 Support",
        "contact_admin": "Contact admin",
        "contact_owner": "Contact owner",
        "buy": "🛒 Buy / Contact owner",
        "unavailable": "This item is currently unavailable. Contact owner @lv_oxyg3n for details.",
        "no_items": "No items available right now.",
        "bot_desc": "Get a custom Telegram bot. Features and price can be discussed with the owner.",
        "admin_only": "Admin only.",
        "admin_menu": "Admin Panel — choose an action:",
        "add_product": "➕ Add product",
        "list_products": "📦 List products",
        "edit_settings": "📝 Edit settings",
        "users": "👥 Users",
        "send_add": "Send product in this format:\nCATEGORY | TITLE | PRICE\nDESCRIPTION on the next line (optional).\nCategories: telegram, whatsapp, main, second, free, bot\nYou can also send a document/photo after creating a product to attach it.",
        "bad_format": "Format not recognised. Send: CATEGORY | TITLE | PRICE",
        "added": "Product added. Product ID: {}",
        "products_title": "Products (ID — category — title):",
        "no_products": "No products yet.",
        "send_setting": "Send one setting per message:\nowner_username | username_without_@\nsupport_username | username_without_@\nbutton_buy | New button label\nbutton_ff | New button label\nbutton_accounts | New button label\nbutton_bot | New button label\nThen use /admin to return.",
        "setting_saved": "Setting saved.",
        "users_count": "Registered users: {}",
        "product": "Product",
        "language_saved": "Language saved."
    },
    "hi": {
        "choose_lang": "Apni language chuno:",
        "share_contact": "Aage badhne ke liye neeche button se apna contact share karo.",
        "contact_btn": "📱 Contact share karo",
        "contact_needed": "Pehle Share contact button dabao.",
        "menu": "Welcome! Kya chahiye?",
        "buy_accounts": "📲 Telegram & WhatsApp services",
        "ff": "🎮 FF Panel",
        "make_bot": "🤖 Apna Bot Banwao",
        "admin": "⚙️ Admin Panel",
        "back": "⬅️ Back",
        "telegram": "Telegram services",
        "whatsapp": "WhatsApp services",
        "main_id": "Main ID",
        "second_id": "Second ID",
        "free_panel": "Free Panel / Downloads",
        "support": "🆘 Support",
        "contact_admin": "Admin se baat karo",
        "contact_owner": "Owner se baat karo",
        "buy": "🛒 Buy / Owner se contact",
        "unavailable": "Ye item abhi available nahi hai. Details ke liye @lv_oxyg3n se contact karo.",
        "no_items": "Abhi koi item available nahi hai.",
        "bot_desc": "Apna custom Telegram bot banwao. Features aur price owner se discuss karo.",
        "admin_only": "Sirf admin use kar sakta hai.",
        "admin_menu": "Admin Panel — option chuno:",
        "add_product": "➕ Product add karo",
        "list_products": "📦 Products list",
        "edit_settings": "📝 Settings edit karo",
        "users": "👥 Users",
        "send_add": "Is format mein bhejo:\nCATEGORY | TITLE | PRICE\nAgli line par DESCRIPTION (optional).\nCategories: telegram, whatsapp, main, second, free, bot\nProduct banne ke baad uske saath document/photo bhi attach kar sakte ho.",
        "bad_format": "Format galat hai. Bhejo: CATEGORY | TITLE | PRICE",
        "added": "Product add ho gaya. Product ID: {}",
        "products_title": "Products (ID — category — title):",
        "no_products": "Abhi koi product nahi.",
        "send_setting": "Ek setting per message bhejo:\nowner_username | username_without_@\nsupport_username | username_without_@\nbutton_buy | Naya button label\nbutton_ff | Naya button label\nbutton_accounts | Naya button label\nbutton_bot | Naya button label\nWapas aane ke liye /admin bhejo.",
        "setting_saved": "Setting save ho gayi.",
        "users_count": "Registered users: {}",
        "product": "Product",
        "language_saved": "Language save ho gayi."
    },
    "ru": {
        "choose_lang": "Выберите язык:",
        "share_contact": "Поделитесь контактом с помощью кнопки ниже, чтобы продолжить.",
        "contact_btn": "📱 Поделиться контактом",
        "contact_needed": "Сначала нажмите кнопку «Поделиться контактом».",
        "menu": "Добро пожаловать! Выберите действие:",
        "buy_accounts": "📲 Услуги Telegram и WhatsApp",
        "ff": "🎮 FF Panel",
        "make_bot": "🤖 Создать своего бота",
        "admin": "⚙️ Панель администратора",
        "back": "⬅️ Назад",
        "telegram": "Услуги Telegram",
        "whatsapp": "Услуги WhatsApp",
        "main_id": "Основной ID",
        "second_id": "Второй ID",
        "free_panel": "Бесплатные файлы",
        "support": "🆘 Поддержка",
        "contact_admin": "Связаться с админом",
        "contact_owner": "Связаться с владельцем",
        "buy": "🛒 Купить / связаться с владельцем",
        "unavailable": "Сейчас недоступно. Свяжитесь с @lv_oxyg3n.",
        "no_items": "Пока нет доступных товаров.",
        "bot_desc": "Закажите собственного Telegram-бота. Обсудите функции и цену с владельцем.",
        "admin_only": "Только для администратора.",
        "admin_menu": "Панель администратора — выберите действие:",
        "add_product": "➕ Добавить товар",
        "list_products": "📦 Список товаров",
        "edit_settings": "📝 Изменить настройки",
        "users": "👥 Пользователи",
        "send_add": "Отправьте:\nCATEGORY | TITLE | PRICE\nОписание на следующей строке (необязательно).\nКатегории: telegram, whatsapp, main, second, free, bot",
        "bad_format": "Неверный формат. Отправьте: CATEGORY | TITLE | PRICE",
        "added": "Товар добавлен. ID: {}",
        "products_title": "Товары (ID — категория — название):",
        "no_products": "Товаров пока нет.",
        "send_setting": "Отправьте одну настройку:\nowner_username | username_without_@\nsupport_username | username_without_@\nbutton_buy | Новый текст\nbutton_ff | Новый текст\nbutton_accounts | Новый текст\nbutton_bot | Новый текст\nДля возврата отправьте /admin.",
        "setting_saved": "Настройка сохранена.",
        "users_count": "Зарегистрировано пользователей: {}",
        "product": "Товар",
        "language_saved": "Язык сохранён."
    }
}

def db():
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            uid INTEGER PRIMARY KEY, lang TEXT DEFAULT 'en', phone TEXT DEFAULT '',
            first_name TEXT DEFAULT '', username TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, title TEXT,
            price TEXT, description TEXT DEFAULT '', file_id TEXT DEFAULT '',
            file_type TEXT DEFAULT '', active INTEGER DEFAULT 1)""")
        c.execute("""CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT)""")
        defaults = {
            "owner_username": OWNER_USERNAME, "support_username": OWNER_USERNAME,
            "button_buy": "📲 Telegram & WhatsApp services",
            "button_ff": "🎮 FF Panel", "button_accounts": "📲 Buy accounts",
            "button_bot": "🤖 Make Your Own Bot"
        }
        for k, v in defaults.items():
            c.execute("INSERT OR IGNORE INTO settings(k,v) VALUES(?,?)", (k,v))

def setting(k):
    with db() as c:
        r = c.execute("SELECT v FROM settings WHERE k=?", (k,)).fetchone()
    return r["v"] if r else ""

def set_setting(k, v):
    with db() as c:
        c.execute("INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k,v))

def api(token, method, payload=None, files=None):
    try:
        r = requests.post(API.format(token) + "/" + method, data=payload or {}, files=files, timeout=40)
        return r.json()
    except Exception as e:
        print("API error:", e)
        return {}

def send(token, chat_id, text, markup=None, parse_mode=None):
    p = {"chat_id": chat_id, "text": text}
    if markup is not None:
        p["reply_markup"] = json.dumps(markup, ensure_ascii=False)
    if parse_mode:
        p["parse_mode"] = parse_mode
    return api(token, "sendMessage", p)

def edit(token, chat_id, message_id, text, markup=None):
    p = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if markup is not None:
        p["reply_markup"] = json.dumps(markup, ensure_ascii=False)
    return api(token, "editMessageText", p)

def answer(token, cqid, text="", alert=False):
    api(token, "answerCallbackQuery", {"callback_query_id": cqid, "text": text, "show_alert": str(alert).lower()})

def ikb(rows):
    return {"inline_keyboard": rows}

def user_row(uid):
    with db() as c:
        return c.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()

def lang(uid):
    r = user_row(uid)
    return (r["lang"] if r and r["lang"] in LANGS else "en")

def tr(uid, key):
    return LANGS[lang(uid)].get(key, LANGS["en"].get(key, key))

def save_user(uid, **kw):
    old = user_row(uid)
    vals = {
        "lang": kw.get("lang", old["lang"] if old else "en"),
        "phone": kw.get("phone", old["phone"] if old else ""),
        "first_name": kw.get("first_name", old["first_name"] if old else ""),
        "username": kw.get("username", old["username"] if old else "")
    }
    with db() as c:
        c.execute("""INSERT INTO users(uid,lang,phone,first_name,username) VALUES(?,?,?,?,?)
        ON CONFLICT(uid) DO UPDATE SET lang=excluded.lang, phone=excluded.phone,
        first_name=excluded.first_name, username=excluded.username""",
        (uid, vals["lang"], vals["phone"], vals["first_name"], vals["username"]))

def is_admin(uid):
    return int(uid) == OWNER_ID

def language_keyboard():
    return ikb([[{"text":"English 🇬🇧","callback_data":"lang:en"},
                 {"text":"Hinglish 🇮🇳","callback_data":"lang:hi"},
                 {"text":"Русский 🇷🇺","callback_data":"lang:ru"}]])

def contact_keyboard(uid):
    return {"keyboard":[[{"text":tr(uid,"contact_btn"),"request_contact":True}]],
            "resize_keyboard":True, "one_time_keyboard":True}

def remove_reply_keyboard():
    return {"remove_keyboard":True}

def main_menu(uid):
    rows = [
        [{"text":setting("button_accounts") or tr(uid,"buy_accounts"),"callback_data":"accounts"}],
        [{"text":setting("button_ff") or tr(uid,"ff"),"callback_data":"ff"}],
        [{"text":setting("button_bot") or tr(uid,"make_bot"),"callback_data":"makebot"}],
    ]
    if is_admin(uid):
        rows.append([{"text":tr(uid,"admin"),"callback_data":"admin"}])
    return ikb(rows)

def send_main(token, uid, chat_id=None):
    chat_id = chat_id or uid
    send(token, chat_id, tr(uid,"menu"), main_menu(uid))

def owner_link():
    return "https://t.me/" + setting("owner_username").lstrip("@")

def products_for(cat):
    with db() as c:
        return c.execute("SELECT * FROM products WHERE category=? AND active=1 ORDER BY id DESC", (cat,)).fetchall()

def show_products(token, uid, cat):
    items = products_for(cat)
    if not items:
        send(token, uid, tr(uid,"no_items") + "\n" + tr(uid,"unavailable"))
        return
    for p in items:
        title = escape(p["title"])
        desc = escape(p["description"] or "")
        text = f"<b>{title}</b>\n{desc}\n\nPrice: {escape(p['price'])}"
        rows = [[{"text":tr(uid,"buy"),"url":owner_link()}]]
        if p["file_id"] and cat == "free":
            rows.insert(0,[{"text":"⬇️ Download","callback_data":f"download:{p['id']}"}])
        send(token, uid, text, ikb(rows), "HTML")
        if p["file_id"] and cat != "free":
            send_file(token, uid, p["file_type"], p["file_id"], caption=p["title"])

def send_file(token, chat_id, file_type, file_id, caption=""):
    method_map = {
        "document": "sendDocument",
        "photo": "sendPhoto",
        "video": "sendVideo",
        "animation": "sendAnimation"
    }
    method = method_map.get(file_type, "sendDocument")
    key = file_type if file_type in method_map else "document"
    payload = {"chat_id": chat_id, "caption": caption, key: file_id}
    return api(token, method, payload)

def admin_menu(token, uid):
    rows = [
        [{"text":tr(uid,"add_product"),"callback_data":"adm:add"}],
        [{"text":tr(uid,"list_products"),"callback_data":"adm:list"}],
        [{"text":tr(uid,"edit_settings"),"callback_data":"adm:settings"}],
        [{"text":tr(uid,"users"),"callback_data":"adm:users"}],
        [{"text":tr(uid,"back"),"callback_data":"home"}]
    ]
    send(token, uid, tr(uid,"admin_menu"), ikb(rows))

def process_message(token, m, state):
    chat = m.get("chat",{})
    uid = m.get("from",{}).get("id",0)
    chat_id = chat.get("id", uid)
    txt = m.get("text","")
    frm = m.get("from",{})
    if not uid: return
    save_user(uid, first_name=frm.get("first_name",""), username=frm.get("username",""))
    if txt == "/start":
        send(token, chat_id, tr(uid,"choose_lang"), language_keyboard())
        return
    if txt == "/admin" and is_admin(uid):
        state.pop(uid, None)
        admin_menu(token, uid)
        return
    if "contact" in m:
        con = m["contact"]
        if con.get("user_id") != uid:
            send(token, chat_id, tr(uid,"contact_needed"), contact_keyboard(uid))
            return
        save_user(uid, phone=con.get("phone_number",""))
        send(token, chat_id, tr(uid,"menu"), remove_reply_keyboard())
        send(token, chat_id, tr(uid,"menu"), main_menu(uid))
        send(token, OWNER_ID, f"Contact shared\nUser ID: {uid}\nName: {frm.get('first_name','')}\nUsername: @{frm.get('username','')}\nPhone: {con.get('phone_number','')}")
        return
    if uid in state:
        mode = state[uid]
        if mode == "addproduct":
            lines = txt.splitlines()
            parts = lines[0].split("|")
            if len(parts) < 3:
                send(token, chat_id, tr(uid,"bad_format"))
                return
            cat, title, price = [x.strip() for x in parts[:3]]
            if cat not in ("telegram","whatsapp","main","second","free","bot"):
                send(token, chat_id, "Invalid category. Use: telegram, whatsapp, main, second, free, bot")
                return
            desc = "\n".join(lines[1:]).strip()
            with db() as c:
                cur = c.execute("INSERT INTO products(category,title,price,description) VALUES(?,?,?,?)", (cat,title,price,desc))
                pid = cur.lastrowid
            state[uid] = f"attach:{pid}"
            send(token, chat_id, tr(uid,"added").format(pid) + "\nNow optionally send a photo, video, animation or document to attach it, or send /admin.")
            return
        if mode.startswith("attach:"):
            pid = int(mode.split(":")[1])
            types = [("document","document"),("photo","photo"),("video","video"),("animation","animation")]
            for key, typ in types:
                if key in m:
                    item = m[key][-1] if key == "photo" else m[key]
                    fid = item.get("file_id")
                    with db() as c:
                        c.execute("UPDATE products SET file_id=?,file_type=? WHERE id=?", (fid,typ,pid))
                    send(token, chat_id, "File attached. Send another file or /admin.")
                    return
            if txt == "/admin":
                state.pop(uid,None)
                admin_menu(token,uid)
                return
            send(token, chat_id, "Send a document/photo/video/animation to attach, or /admin to finish.")
            return
        if mode == "settings":
            if "|" not in txt:
                send(token, chat_id, tr(uid,"send_setting"))
                return
            k,v = [x.strip() for x in txt.split("|",1)]
            allowed = ("owner_username","support_username","button_buy","button_ff","button_accounts","button_bot")
            if k not in allowed or not v:
                send(token, chat_id, "Unknown setting. " + tr(uid,"send_setting"))
                return
            if k.endswith("username"): v = v.lstrip("@")
            set_setting(k,v)
            send(token, chat_id, tr(uid,"setting_saved"))
            return

    r = user_row(uid)
    if not r or not r["phone"]:
        if not r or r["lang"] not in LANGS:
            send(token, chat_id, tr(uid,"choose_lang"), language_keyboard())
        else:
            send(token, chat_id, tr(uid,"share_contact"), contact_keyboard(uid))
        return
    if txt:
        send(token, chat_id, tr(uid,"menu"), main_menu(uid))

def process_callback(token, cq, state):
    uid = cq.get("from",{}).get("id",0)
    msg = cq.get("message",{})
    chat_id = msg.get("chat",{}).get("id",uid)
    mid = msg.get("message_id")
    data = cq.get("data","")
    if data.startswith("lang:"):
        l = data.split(":",1)[1]
        save_user(uid, lang=l)
        answer(token,cq["id"],tr(uid,"language_saved"))
        r = user_row(uid)
        if not r["phone"]:
            send(token, chat_id, tr(uid,"share_contact"), contact_keyboard(uid))
        else:
            send(token, chat_id, tr(uid,"menu"), main_menu(uid))
        return
    r = user_row(uid)
    if not r or not r["phone"]:
        answer(token,cq["id"],tr(uid,"contact_needed"),True)
        send(token, chat_id, tr(uid,"share_contact"), contact_keyboard(uid))
        return
    if data == "home":
        answer(token,cq["id"])
        send(token,chat_id,tr(uid,"menu"),main_menu(uid))
        return
    if data == "accounts":
        answer(token,cq["id"])
        rows = [[{"text":tr(uid,"telegram"),"callback_data":"cat:telegram"}],
                [{"text":tr(uid,"whatsapp"),"callback_data":"cat:whatsapp"}],
                [{"text":tr(uid,"back"),"callback_data":"home"}]]
        send(token,chat_id,tr(uid,"buy_accounts"),ikb(rows))
        return
    if data == "ff":
        answer(token,cq["id"])
        rows = [[{"text":tr(uid,"main_id"),"callback_data":"cat:main"}],
                [{"text":tr(uid,"second_id"),"callback_data":"cat:second"}],
                [{"text":tr(uid,"free_panel"),"callback_data":"cat:free"}],
                [{"text":tr(uid,"support"),"callback_data":"support"}],
                [{"text":tr(uid,"back"),"callback_data":"home"}]]
        send(token,chat_id,tr(uid,"ff"),ikb(rows))
        return
    if data.startswith("cat:"):
        answer(token,cq["id"])
        show_products(token,chat_id,data.split(":",1)[1])
        return
    if data == "makebot":
        answer(token,cq["id"])
        send(token,chat_id,tr(uid,"bot_desc"),ikb([[{"text":tr(uid,"buy"),"url":owner_link()}],[{"text":tr(uid,"back"),"callback_data":"home"}]]))
        return
    if data == "support":
        answer(token,cq["id"])
        su = setting("support_username").lstrip("@")
        rows = [[{"text":tr(uid,"contact_admin"),"url":"https://t.me/"+su}],
                [{"text":tr(uid,"contact_owner"),"url":owner_link()}],
                [{"text":tr(uid,"back"),"callback_data":"ff"}]]
        send(token,chat_id,tr(uid,"support"),ikb(rows))
        return
    if data.startswith("download:"):
        answer(token,cq["id"],"Preparing download…")
        pid = int(data.split(":")[1])
        with db() as c: p = c.execute("SELECT * FROM products WHERE id=? AND active=1",(pid,)).fetchone()
        if p and p["file_id"]:
            send_file(token,chat_id,p["file_type"],p["file_id"],p["title"])
        else:
            send(token,chat_id,tr(uid,"unavailable"))
        return
    if data == "admin":
        answer(token,cq["id"])
        if not is_admin(uid):
            send(token,chat_id,tr(uid,"admin_only"))
            return
        admin_menu(token,uid)
        return
    if data.startswith("adm:"):
        answer(token,cq["id"])
        if not is_admin(uid): return
        action = data.split(":",1)[1]
        if action == "add":
            state[uid] = "addproduct"
            send(token,chat_id,tr(uid,"send_add"))
        elif action == "settings":
            state[uid] = "settings"
            send(token,chat_id,tr(uid,"send_setting"))
        elif action == "list":
            with db() as c: ps = c.execute("SELECT id,category,title,price,active FROM products ORDER BY id DESC LIMIT 100").fetchall()
            if not ps:
                send(token,chat_id,tr(uid,"no_products"))
            else:
                lines = [tr(uid,"products_title")]
                for p in ps: lines.append(f'{p["id"]} — {p["category"]} — {p["title"]} — {p["price"]} — active={p["active"]}')
                lines.append("\nTo delete: /delete ID\nTo enable/disable: /toggle ID")
                send(token,chat_id,"\n".join(lines))
        elif action == "users":
            with db() as c:
                count = c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
                rows = c.execute("SELECT uid,first_name,username,phone FROM users ORDER BY uid DESC LIMIT 50").fetchall()
            lines = [tr(uid,"users_count").format(count)]
            for u in rows:
                lines.append(f'{u["uid"]} | {u["first_name"]} | @{u["username"]} | {u["phone"]}')
            send(token,chat_id,"\n".join(lines))
        return

def main():
    token = BOT_TOKEN
    init_db()
    me = api(token, "getMe")
    if not me.get("ok"):
        print("Token invalid. Check your bot token.")
        return
    print("Running as @" + me["result"].get("username", "bot") + " — press Ctrl+C to stop.")
    offset = 0
    state = {}
    while True:
        try:
            data = api(token, "getUpdates", {"timeout": 25, "offset": offset, "allowed_updates": json.dumps(["message", "callback_query"])})
            if not data.get("ok"):
                time.sleep(2)
                continue
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                if "message" in upd:
                    m = upd["message"]
                    uid = m.get("from", {}).get("id", 0)
                    txt = m.get("text", "")
                    if is_admin(uid) and txt.startswith("/delete "):
                        try:
                            pid = int(txt.split()[1])
                            with db() as c: c.execute("DELETE FROM products WHERE id=?", (pid,))
                            send(token, uid, "Deleted product " + str(pid))
                        except: send(token, uid, "Use /delete PRODUCT_ID")
                    elif is_admin(uid) and txt.startswith("/toggle "):
                        try:
                            pid = int(txt.split()[1])
                            with db() as c: c.execute("UPDATE products SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id=?", (pid,))
                            send(token, uid, "Toggled product " + str(pid))
                        except: send(token, uid, "Use /toggle PRODUCT_ID")
                    else:
                        process_message(token, m, state)
                elif "callback_query" in upd:
                    process_callback(token, upd["callback_query"], state)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print("Loop error:", e)
            time.sleep(2)

if __name__ == "__main__":
    main()
