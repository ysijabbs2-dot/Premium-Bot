#!/usr/bin/env python3
# Telegram Luxury Shop Bot — Upgraded UI & Render Ready

import json
import os
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from html import escape
import requests

# Yahan apni details daal do (Maine already set kar di hain)
BOT_TOKEN = "8990644924:AAGUr2F-qRjEKC6WWPz_tRxdhordWPzunk4"
OWNER_ID = 8886164132
OWNER_USERNAME = "lv_oxyg3n"

DB_FILE = "shopbot.sqlite3"
API = "https://api.telegram.org/bot{}"

# --- Render Port Binding (Web Service fix) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is active.")

    def log_message(self, format, *args):
        return # Hide console spam

def start_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# Start background server
threading.Thread(target=start_dummy_server, daemon=True).start()
# ---------------------------------------------

def db():
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            uid INTEGER PRIMARY KEY, lang TEXT DEFAULT 'hi', phone TEXT DEFAULT '',
            first_name TEXT DEFAULT '', username TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, title TEXT,
            price TEXT, description TEXT DEFAULT '', file_id TEXT DEFAULT '',
            file_type TEXT DEFAULT '', active INTEGER DEFAULT 1)""")
        c.execute("""CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT)""")
        defaults = {
            "owner_username": OWNER_USERNAME,
            "support_username": OWNER_USERNAME,
            "store_name": "⚡ 𝐎𝐗𝐘𝐆𝐄𝐍 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝐋 𝐒𝐓𝐎𝐑𝐄 ⚡"
        }
        for k, v in defaults.items():
            c.execute("INSERT OR IGNORE INTO settings(k,v) VALUES(?,?)", (k, v))

def setting(k):
    with db() as c:
        r = c.execute("SELECT v FROM settings WHERE k=?", (k,)).fetchone()
    return r["v"] if r else ""

def set_setting(k, v):
    with db() as c:
        c.execute("INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, v))

def api(token, method, payload=None, files=None):
    try:
        r = requests.post(API.format(token) + "/" + method, data=payload or {}, files=files, timeout=35)
        return r.json()
    except Exception as e:
        print("API error:", e)
        return {}

def send(token, chat_id, text, markup=None, parse_mode="HTML"):
    p = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if markup is not None:
        p["reply_markup"] = json.dumps(markup, ensure_ascii=False)
    return api(token, "sendMessage", p)

def edit(token, chat_id, message_id, text, markup=None, parse_mode="HTML"):
    p = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
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

def save_user(uid, **kw):
    old = user_row(uid)
    vals = {
        "lang": kw.get("lang", old["lang"] if old else "hi"),
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

def contact_keyboard():
    return {"keyboard": [[{"text": "⚡ 𝐕𝐄𝐑𝐈𝐅𝐘 & 𝐂𝐎𝐍𝐓𝐈𝐍𝐔𝐄 📱", "request_contact": True}]],
            "resize_keyboard": True, "one_time_keyboard": True}

def remove_reply_keyboard():
    return {"remove_keyboard": True}

def owner_link():
    return "https://t.me/" + setting("owner_username").lstrip("@")

def main_menu_keyboard(uid):
    rows = [
        [{"text": "🔥 𝐒𝐎𝐂𝐈𝐀𝐋 𝐒𝐄𝐑𝐕𝐈𝐂𝐄𝐒", "callback_data": "cat_social"},
         {"text": "🎮 𝐅𝐅 𝐏𝐀𝐍𝐄𝐋𝐒", "callback_data": "cat_ff"}],
        [{"text": "🤖 𝐌𝐀𝐊𝐄 𝐘𝐎𝐔𝐑 𝐎𝐖𝐍 𝐁𝐎𝐓", "callback_data": "makebot"}],
        [{"text": "🆘 𝟐𝟒/𝟕 𝐒𝐔𝐏𝐏𝐎𝐑𝐓", "callback_data": "support"},
         {"text": "👑 𝐎𝐖𝐍𝐄𝐑", "url": owner_link()}]
    ]
    if is_admin(uid):
        rows.append([{"text": "⚙️ 𝐀𝐃𝐌𝐈𝐍 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃 ⚡", "callback_data": "admin"}])
    return ikb(rows)

def main_menu_text(uid, name):
    title = setting("store_name")
    return (
        f"<b>{title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👋 Welcome, <b>{escape(name)}</b>!\n\n"
        f"◈ Instant Delivery & Safe Services\n"
        f"◈ Select a category below to explore:"
    )

def admin_dashboard_markup():
    return ikb([
        [{"text": "➕ Add Product", "callback_data": "adm:add"},
         {"text": "📦 Products List", "callback_data": "adm:list"}],
        [{"text": "👥 User Analytics", "callback_data": "adm:users"},
         {"text": "📝 Edit Store Name", "callback_data": "adm:storename"}],
        [{"text": "🔄 Refresh", "callback_data": "admin"},
         {"text": "⬅️ Back To Store", "callback_data": "home"}]
    ])

def admin_dashboard_text():
    with db() as c:
        u_count = c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
        p_count = c.execute("SELECT COUNT(*) n FROM products").fetchone()["n"]
    return (
        f"👑 <b>𝐎𝐗𝐘𝐆𝐄𝐍 𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Total Users:</b> <code>{u_count}</code>\n"
        f"📦 <b>Total Products:</b> <code>{p_count}</code>\n"
        f"🏷 <b>Store Name:</b> {setting('store_name')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Quick controls se actions select karo:"
    )

def show_products(token, chat_id, cat, title_bar):
    with db() as c:
        items = c.execute("SELECT * FROM products WHERE category=? AND active=1 ORDER BY id DESC", (cat,)).fetchall()
    
    if not items:
        text = f"<b>{title_bar}</b>\n━━━━━━━━━━━━━━━━━━\n⚠️ <i>Abhi is category me koi product available nahi hai.</i>"
        send(token, chat_id, text, ikb([[{"text": "⬅️ Back", "callback_data": "home"}]]))
        return

    for p in items:
        t = escape(p["title"])
        d = escape(p["description"] or "Instant delivery guaranteed.")
        pr = escape(p["price"])
        text = (
            f"📦 <b>{t}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{d}\n\n"
            f"💰 <b>Price:</b> <code>{pr}</code>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        rows = [[{"text": "💳 𝐁𝐔𝐘 𝐍𝐎𝐖", "url": owner_link()}]]
        if p["file_id"] and cat == "free":
            rows.insert(0, [{"text": "⬇️ 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃 𝐅𝐈𝐋𝐄", "callback_data": f"dl:{p['id']}"}])
        send(token, chat_id, text, ikb(rows))

def send_file(token, chat_id, file_type, file_id, caption=""):
    method_map = {"document": "sendDocument", "photo": "sendPhoto", "video": "sendVideo", "animation": "sendAnimation"}
    method = method_map.get(file_type, "sendDocument")
    key = file_type if file_type in method_map else "document"
    return api(token, method, {"chat_id": chat_id, "caption": caption, key: file_id})

def process_message(token, m, state):
    chat = m.get("chat", {})
    uid = m.get("from", {}).get("id", 0)
    chat_id = chat.get("id", uid)
    txt = m.get("text", "")
    frm = m.get("from", {})
    if not uid: return

    save_user(uid, first_name=frm.get("first_name", ""), username=frm.get("username", ""))

    if txt == "/start":
        r = user_row(uid)
        if not r or not r["phone"]:
            text = (
                "🛡️ <b>𝐀𝐂𝐂𝐄𝐒𝐒 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Welcome to <b>Oxygen Store</b>!\n"
                "Aage badhne ke liye neeche button dabakar apna number verify karein:"
            )
            send(token, chat_id, text, contact_keyboard())
            return
        send(token, chat_id, main_menu_text(uid, frm.get("first_name", "User")), main_menu_keyboard(uid))
        return

    if txt == "/admin" and is_admin(uid):
        state.pop(uid, None)
        send(token, chat_id, admin_dashboard_text(), admin_dashboard_markup())
        return

    if "contact" in m:
        con = m["contact"]
        if con.get("user_id") != uid:
            send(token, chat_id, "⚠️ Apna khud ka contact share karein.", contact_keyboard())
            return
        save_user(uid, phone=con.get("phone_number", ""))
        send(token, chat_id, "✅ <b>Verification successful!</b>", remove_reply_keyboard())
        send(token, chat_id, main_menu_text(uid, frm.get("first_name", "User")), main_menu_keyboard(uid))
        send(token, OWNER_ID, f"🔔 <b>New Verified User:</b>\nID: <code>{uid}</code>\nName: {escape(frm.get('first_name',''))}\nUser: @{frm.get('username','')}\nPhone: {con.get('phone_number','')}")
        return

    if uid in state:
        mode = state[uid]
        if mode == "addproduct":
            lines = txt.splitlines()
            parts = lines[0].split("|")
            if len(parts) < 3:
                send(token, chat_id, "❌ Format galat hai!\nFormat: <code>CATEGORY | TITLE | PRICE</code>")
                return
            cat, title, price = [x.strip() for x in parts[:3]]
            allowed_cats = ("telegram", "whatsapp", "main", "second", "free", "bot")
            if cat.lower() not in allowed_cats:
                send(token, chat_id, f"❌ Invalid category.\nAllowed: {', '.join(allowed_cats)}")
                return
            desc = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
            with db() as c:
                cur = c.execute("INSERT INTO products(category,title,price,description) VALUES(?,?,?,?)",
                                (cat.lower(), title, price, desc))
                pid = cur.lastrowid
            state[uid] = f"attach:{pid}"
            send(token, chat_id, f"✅ <b>Product #{pid} Added!</b>\nAb file/photo bhejo attach karne ke liye, ya /admin bhejo skip karne ko.")
            return

        if mode.startswith("attach:"):
            pid = int(mode.split(":")[1])
            types = [("document", "document"), ("photo", "photo"), ("video", "video"), ("animation", "animation")]
            for key, typ in types:
                if key in m:
                    item = m[key][-1] if key == "photo" else m[key]
                    fid = item.get("file_id")
                    with db() as c:
                        c.execute("UPDATE products SET file_id=?, file_type=? WHERE id=?", (fid, typ, pid))
                    state.pop(uid, None)
                    send(token, chat_id, "✅ File attached successfully!", admin_dashboard_markup())
                    return
            if txt == "/admin":
                state.pop(uid, None)
                send(token, chat_id, admin_dashboard_text(), admin_dashboard_markup())
                return

        if mode == "storename":
            if txt.strip():
                set_setting("store_name", txt.strip())
                state.pop(uid, None)
                send(token, chat_id, f"✅ Store Name updated to: <b>{escape(txt.strip())}</b>\n/admin bhejo return hone ke liye.")
                return

    r = user_row(uid)
    if not r or not r["phone"]:
        send(token, chat_id, "⚠️ Kripya pehle apna contact verify karein.", contact_keyboard())
        return

    send(token, chat_id, main_menu_text(uid, frm.get("first_name", "User")), main_menu_keyboard(uid))

def process_callback(token, cq, state):
    uid = cq.get("from", {}).get("id", 0)
    msg = cq.get("message", {})
    chat_id = msg.get("chat", {}).get("id", uid)
    mid = msg.get("message_id")
    data = cq.get("data", "")

    r = user_row(uid)
    if not r or not r["phone"]:
        answer(token, cq["id"], "Pehle verify karein!", True)
        return

    if data == "home":
        answer(token, cq["id"])
        edit(token, chat_id, mid, main_menu_text(uid, cq.get("from", {}).get("first_name", "User")), main_menu_keyboard(uid))
        return

    if data == "cat_social":
        answer(token, cq["id"])
        rows = [
            [{"text": "📱 Telegram Accounts", "callback_data": "cat:telegram"},
             {"text": "💬 WhatsApp Services", "callback_data": "cat:whatsapp"}],
            [{"text": "⬅️ Back", "callback_data": "home"}]
        ]
        text = "📲 <b>𝐒𝐎𝐂𝐈𝐀𝐋 𝐌𝐄𝐃𝐈𝐀 𝐒𝐄𝐑𝐕𝐈𝐂𝐄𝐒</b>\n━━━━━━━━━━━━━━━━━━\nSelect category:"
        edit(token, chat_id, mid, text, ikb(rows))
        return

    if data == "cat_ff":
        answer(token, cq["id"])
        rows = [
            [{"text": "🛡️ Main ID Safe Panel", "callback_data": "cat:main"},
             {"text": "⚡ Second ID Brutal", "callback_data": "cat:second"}],
            [{"text": "🎁 Free Panel / Files", "callback_data": "cat:free"}],
            [{"text": "⬅️ Back", "callback_data": "home"}]
        ]
        text = "🎮 <b>𝐅𝐑𝐄𝐄 𝐅𝐈𝐑𝐄 𝐏𝐀𝐍𝐄𝐋𝐒 & 𝐓𝐎𝐎𝐋𝐒</b>\n━━━━━━━━━━━━━━━━━━\nSelect type:"
        edit(token, chat_id, mid, text, ikb(rows))
        return

    if data.startswith("cat:"):
        answer(token, cq["id"])
        cat = data.split(":", 1)[1]
        titles = {
            "telegram": "📱 TELEGRAM ACCOUNTS",
            "whatsapp": "💬 WHATSAPP SERVICES",
            "main": "🛡️ MAIN ID PANELS",
            "second": "⚡ SECOND ID PANELS",
            "free": "🎁 FREE DOWNLOADS",
            "bot": "🤖 CUSTOM BOTS"
        }
        show_products(token, chat_id, cat, titles.get(cat, "PRODUCTS"))
        return

    if data == "makebot":
        answer(token, cq["id"])
        text = (
            "🤖 <b>𝐂𝐔𝐒𝐓𝐎𝐌 𝐓𝐄𝐋𝐄𝐆𝐑𝐀𝐌 𝐁𝐎𝐓𝐒</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Apne setup ke liye custom bots banwayein:\n\n"
            "• Shop / Store Bots\n"
            "• OTP / Account Bots\n"
            "• Panel & Key Management Bots\n"
            "• High Speed 24/7 Hosting Setup\n\n"
            "Owner se features aur price discuss karein:"
        )
        rows = [[{"text": "💬 𝐃𝐈𝐒𝐂𝐔𝐒𝐒 𝐖𝐈𝐓𝐇 𝐎𝐖𝐍𝐄𝐑", "url": owner_link()}],
                [{"text": "⬅️ Back", "callback_data": "home"}]]
        edit(token, chat_id, mid, text, ikb(rows))
        return

    if data == "support":
        answer(token, cq["id"])
        su = setting("support_username").lstrip("@")
        rows = [[{"text": "👨‍💻 Admin Support", "url": f"https://t.me/{su}"},
                 {"text": "👑 Owner Direct", "url": owner_link()}],
                [{"text": "⬅️ Back", "callback_data": "home"}]]
        text = "🆘 <b>𝟐𝟒/𝟕 𝐇𝐄𝐋𝐏 & 𝐒𝐔𝐏𝐏𝐎𝐑𝐓</b>\n━━━━━━━━━━━━━━━━━━\nKisi bhi query ya order problem ke liye contact karein:"
        edit(token, chat_id, mid, text, ikb(rows))
        return

    if data.startswith("dl:"):
        answer(token, cq["id"], "Downloading file...")
        pid = int(data.split(":")[1])
        with db() as c:
            p = c.execute("SELECT * FROM products WHERE id=? AND active=1", (pid,)).fetchone()
        if p and p["file_id"]:
            send_file(token, chat_id, p["file_type"], p["file_id"], caption=p["title"])
        else:
            send(token, chat_id, "⚠️ File filhaal available nahi hai.")
        return

    if data == "admin":
        answer(token, cq["id"])
        if not is_admin(uid): return
        edit(token, chat_id, mid, admin_dashboard_text(), admin_dashboard_markup())
        return

    if data.startswith("adm:"):
        answer(token, cq["id"])
        if not is_admin(uid): return
        act = data.split(":", 1)[1]

        if act == "add":
            state[uid] = "addproduct"
            text = (
                "➕ <b>𝐀𝐃𝐃 𝐍𝐄𝐖 𝐏𝐑𝐎𝐃𝐔𝐂𝐓</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Is format me message bhejein:\n"
                "<code>CATEGORY | TITLE | PRICE</code>\n"
                "<i>Agli line me Description (optional)</i>\n\n"
                "Categories: <code>telegram, whatsapp, main, second, free, bot</code>"
            )
            send(token, chat_id, text)

        elif act == "storename":
            state[uid] = "storename"
            send(token, chat_id, "📝 Naya Store Title enter karein:")

        elif act == "list":
            with db() as c:
                ps = c.execute("SELECT id, category, title, price, active FROM products ORDER BY id DESC LIMIT 50").fetchall()
            if not ps:
                edit(token, chat_id, mid, "📦 Koi products nahi hain abhi.", ikb([[{"text": "⬅️ Back", "callback_data": "admin"}]]))
            else:
                lines = ["📦 <b>𝐏𝐑𝐎𝐃𝐔𝐂𝐓 𝐋𝐈𝐒𝐓:</b>\n━━━━━━━━━━━━━━━━━━"]
                for p in ps:
                    status = "🟢" if p["active"] == 1 else "🔴"
                    lines.append(f"{status} <b>#{p['id']}</b> [{p['category'].upper()}] - {escape(p['title'])} ({p['price']})")
                lines.append("\nCommands:\n• Delete: <code>/delete ID</code>\n• Toggle: <code>/toggle ID</code>")
                edit(token, chat_id, mid, "\n".join(lines), ikb([[{"text": "⬅️ Back to Admin", "callback_data": "admin"}]]))

        elif act == "users":
            with db() as c:
                count = c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
                rows = c.execute("SELECT uid, first_name, username, phone FROM users ORDER BY uid DESC LIMIT 20").fetchall()
            lines = [f"👥 <b>Registered Users:</b> {count}\n━━━━━━━━━━━━━━━━━━"]
            for u in rows:
                lines.append(f"• <code>{u['uid']}</code> | {escape(u['first_name'] or '')} | @{u['username'] or 'N/A'} | {u['phone']}")
            edit(token, chat_id, mid, "\n".join(lines), ikb([[{"text": "⬅️ Back to Admin", "callback_data": "admin"}]]))

def main():
    token = BOT_TOKEN
    init_db()
    me = api(token, "getMe")
    if not me.get("ok"):
        print("Bot token check failed.")
        return
    print("Running as @" + me["result"].get("username", "bot"))
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
                            send(token, uid, f"🗑️ Product #{pid} deleted.")
                        except: send(token, uid, "Format: /delete PRODUCT_ID")
                    elif is_admin(uid) and txt.startswith("/toggle "):
                        try:
                            pid = int(txt.split()[1])
                            with db() as c: c.execute("UPDATE products SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id=?", (pid,))
                            send(token, uid, f"🔄 Toggled status for #{pid}.")
                        except: send(token, uid, "Format: /toggle PRODUCT_ID")
                    else:
                        process_message(token, m, state)
                elif "callback_query" in upd:
                    process_callback(token, upd["callback_query"], state)
        except KeyboardInterrupt:
            break
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
