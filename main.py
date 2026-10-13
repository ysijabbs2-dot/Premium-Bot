import requests
import json
import time
import sqlite3
import os
import threading
from flask import Flask

TOKEN = "8990644924:AAGUr2F-qRjEKC6WWPz_tRxdhordWPzunk4"
ADMIN_ID = 8886164132
OWNER_USER = "lv_oxyg3n"
API = f"https://api.telegram.org/bot{TOKEN}/"

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, chat_id INTEGER, language TEXT, phone TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS buttons (
                    btn_id TEXT PRIMARY KEY, text TEXT, style TEXT, emoji_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Default Buttons
DEFAULT_BTNS = {
    "tg_wa": {"text": "Buy TG & WhatsApp", "style": "primary", "emoji_id": ""},
    "ff_panel": {"text": "FF PANNEL", "style": "success", "emoji_id": ""},
    "make_bot": {"text": "Make Your Own Bot", "style": "primary", "emoji_id": ""}
}

def get_btn(btn_id):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT text, style, emoji_id FROM buttons WHERE btn_id=?", (btn_id,))
    res = c.fetchone()
    conn.close()
    if res:
        return {"text": res[0], "style": res[1], "emoji_id": res[2]}
    return DEFAULT_BTNS.get(btn_id, {"text": "Button", "style": "primary", "emoji_id": ""})

def save_btn(btn_id, text, style, emoji_id):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO buttons (btn_id, text, style, emoji_id) VALUES (?, ?, ?, ?)", 
              (btn_id, text, style, emoji_id))
    conn.commit()
    conn.close()

# --- DICTIONARY ---
TEXTS = {
    "en": {
        "ask_contact": "🔒 **Verification Required**\n\nPlease share your contact to continue. Your data is 100% safe.",
        "contact_btn": "📞 Share Contact",
        "main": "✨ **WELCOME TO PREMIUM HUB** ✨\n\nSelect an option:",
        "unavail": f"⚠️ Currently unavailable. Contact @{OWNER_USER}."
    },
    "hi": {
        "ask_contact": "🔒 **Verification Required**\n\nAage badhne ke liye contact share karein. Data 100% safe hai.",
        "contact_btn": "📞 Contact Share Karein",
        "main": "✨ **WELCOME TO PREMIUM HUB** ✨\n\nOption chunein:",
        "unavail": f"⚠️ Ye abhi available nahi hai. Contact @{OWNER_USER}."
    }
}
TEXTS["ru"] = TEXTS["en"] # Copying English for Russian placeholder

# --- API FUNCTIONS ---
def api_call(method, data=None):
    try:
        r = requests.post(API + method, json=data or {}, timeout=15)
        return r.json()
    except:
        return {}

def send_msg(chat_id, text, markup=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if markup: data["reply_markup"] = markup
    return api_call("sendMessage", data)

def edit_msg(chat_id, msg_id, text, markup=None):
    data = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "Markdown"}
    if markup: data["reply_markup"] = markup
    return api_call("editMessageText", data)

def build_btn(btn_id, cb_data=None, url=None):
    b = get_btn(btn_id)
    obj = {"text": b["text"], "style": b["style"]}
    if url: obj["url"] = url
    else: obj["callback_data"] = cb_data or btn_id
    if b["emoji_id"]: obj["icon_custom_emoji_id"] = str(b["emoji_id"])
    return obj

# --- ANIMATIONS ---
def play_anim(chat_id, msg_id, anim_type="vaporize"):
    frames = ["⬛️⬛️⬛️⬛️", "💨⬛️⬛️⬛️", "💨💨⬛️⬛️", "💨💨💨⬛️", "✨ Loaded!"] if anim_type == "vaporize" else ["⚙️ Generating.", "⚙️ Generating..", "⚙️ Generating...", "✅ Ready!"]
    for f in frames:
        edit_msg(chat_id, msg_id, f"**{f}**")
        time.sleep(0.4)

# --- MENUS ---
def show_main(chat_id, lang, msg_id=None):
    kb = {"inline_keyboard": [[build_btn("tg_wa")], [build_btn("ff_panel")], [build_btn("make_bot")]]}
    if msg_id: edit_msg(chat_id, msg_id, TEXTS[lang]["main"], kb)
    else: send_msg(chat_id, TEXTS[lang]["main"], kb)

admin_state = {}

# --- MAIN LOOP ---
def run_bot():
    offset = 0
    print("Mega Bot Running...")
    
    while True:
        try:
            updates = api_call("getUpdates", {"offset": offset, "timeout": 30})
            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    text = msg.get("text", "")

                    conn = sqlite3.connect("bot_data.db")
                    c = conn.cursor()
                    c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
                    row = c.fetchone()
                    conn.close()
                    lang = row[0] if row else "en"

                    if "contact" in msg:
                        phone = msg["contact"].get("phone_number")
                        conn = sqlite3.connect("bot_data.db")
                        c = conn.cursor()
                        c.execute("UPDATE users SET phone=? WHERE user_id=?", (phone, user_id))
                        conn.commit()
                        conn.close()
                        api_call("sendMessage", {"chat_id": chat_id, "text": "✅ Verified!", "reply_markup": {"remove_keyboard": True}})
                        show_main(chat_id, lang)
                        continue

                    if text == "/start":
                        conn = sqlite3.connect("bot_data.db")
                        c = conn.cursor()
                        c.execute("INSERT OR IGNORE INTO users (user_id, chat_id, language) VALUES (?, ?, ?)", (user_id, chat_id, "en"))
                        conn.commit()
                        conn.close()
                        kb = {"inline_keyboard": [
                            [{"text": "🇺🇸 English", "callback_data": "lang_en", "style": "primary"}],
                            [{"text": "🇮🇳 Hinglish", "callback_data": "lang_hi", "style": "success"}],
                            [{"text": "🇷🇺 Russian", "callback_data": "lang_ru", "style": "danger"}]
                        ]}
                        send_msg(chat_id, "🌐 **Select Language:**", kb)

                    elif text == "/admin" and user_id == ADMIN_ID:
                        conn = sqlite3.connect("bot_data.db")
                        c = conn.cursor()
                        c.execute("SELECT COUNT(*), COUNT(phone) FROM users")
                        stats = c.fetchone()
                        conn.close()
                        kb = {"inline_keyboard": [
                            [{"text": "✏️ Edit 'Buy TG/WA'", "callback_data": "adminedit_tg_wa"}],
                            [{"text": "✏️ Edit 'FF PANNEL'", "callback_data": "adminedit_ff_panel"}],
                            [{"text": "✏️ Edit 'Make Bot'", "callback_data": "adminedit_make_bot"}]
                        ]}
                        send_msg(chat_id, f"⚙️ **ADMIN PANEL**\nUsers: {stats[0]} | Verified: {stats[1]}\n\nSelect button to edit:", kb)

                    elif user_id == ADMIN_ID and user_id in admin_state:
                        btn_id = admin_state[user_id]["btn"]
                        action = admin_state[user_id]["action"]
                        b = get_btn(btn_id)
                        
                        if action == "text":
                            save_btn(btn_id, text, b["style"], b["emoji_id"])
                            send_msg(chat_id, "✅ Name Updated!")
                        elif action == "emoji":
                            emoji_id = text if text.isdigit() else ""
                            save_btn(btn_id, b["text"], b["style"], emoji_id)
                            send_msg(chat_id, "✅ Emoji ID Updated!")
                        elif action == "color":
                            colors = {"blue": "primary", "green": "success", "red": "danger"}
                            save_btn(btn_id, b["text"], colors.get(text.lower(), "primary"), b["emoji_id"])
                            send_msg(chat_id, "✅ Color Updated!")
                        
                        del admin_state[user_id]

                elif "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id, msg_id = cb["message"]["chat"]["id"], cb["message"]["message_id"]
                    data, user_id, cb_id = cb["data"], cb["from"]["id"], cb["id"]
                    api_call("answerCallbackQuery", {"callback_query_id": cb_id})

                    conn = sqlite3.connect("bot_data.db")
                    c = conn.cursor()
                    c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
                    row = c.fetchone()
                    conn.close()
                    lang = row[0] if row else "en"

                    if data.startswith("lang_"):
                        l = data.split("_")[1]
                        conn = sqlite3.connect("bot_data.db")
                        c = conn.cursor()
                        c.execute("UPDATE users SET language=? WHERE user_id=?", (l, user_id))
                        conn.commit()
                        conn.close()
                        api_call("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
                        kb = {"keyboard": [[{"text": TEXTS[l]["contact_btn"], "request_contact": True}]], "resize_keyboard": True, "one_time_keyboard": True}
                        send_msg(chat_id, TEXTS[l]["ask_contact"], kb)

                    elif data == "ff_panel":
                        kb = {"inline_keyboard": [
                            [{"text": "🥇 Main ID", "callback_data": "unavail", "style": "primary"}, {"text": "🥈 Second ID", "callback_data": "unavail", "style": "primary"}],
                            [{"text": "🆓 Free Panel", "callback_data": "free_panel", "style": "success"}],
                            [{"text": "🛠 Support", "callback_data": "support", "style": "danger"}],
                            [{"text": "🔙 Back", "callback_data": "back", "style": "secondary"}]
                        ]}
                        edit_msg(chat_id, msg_id, "🎯 **FF PANEL SELECTION**", kb)

                    elif data == "tg_wa":
                        kb = {"inline_keyboard": [
                            [{"text": "✈️ Telegram Account", "callback_data": "unavail", "style": "primary"}],
                            [{"text": "🟢 WhatsApp Account", "callback_data": "unavail", "style": "success"}],
                            [{"text": "🔙 Back", "callback_data": "back", "style": "secondary"}]
                        ]}
                        edit_msg(chat_id, msg_id, "📱 **ACCOUNT STORE**", kb)

                    elif data == "make_bot":
                        kb = {"inline_keyboard": [[{"text": "🛒 Buy Bot", "url": f"https://t.me/{OWNER_USER}", "style": "success"}], [{"text": "🔙 Back", "callback_data": "back", "style": "secondary"}]]}
                        edit_msg(chat_id, msg_id, "🤖 **BOT SERVICES**\n- Premium UI\n- 24/7 Hosting\n- SQLite DB", kb)

                    elif data == "free_panel":
                        threading.Thread(target=lambda: play_anim(chat_id, msg_id, "generating")).start()
                        time.sleep(1.5)
                        edit_msg(chat_id, msg_id, "🆓 **FREE PANEL**\n\nDownload Link Generated!", {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "ff_panel", "style": "secondary"}]]})

                    elif data == "support":
                        kb = {"inline_keyboard": [[{"text": "👑 Owner", "url": f"https://t.me/{OWNER_USER}", "style": "primary"}], [{"text": "🔙 Back", "callback_data": "ff_panel", "style": "secondary"}]]}
                        edit_msg(chat_id, msg_id, "🛠 **SUPPORT**", kb)

                    elif data == "unavail":
                        api_call("answerCallbackQuery", {"callback_query_id": cb_id, "text": TEXTS[lang]["unavail"], "show_alert": True})

                    elif data == "back":
                        threading.Thread(target=lambda: play_anim(chat_id, msg_id, "vaporize")).start()
                        time.sleep(2)
                        show_main(chat_id, lang, msg_id)

                    elif data.startswith("adminedit_"):
                        btn_id = data.replace("adminedit_", "")
                        kb = {"inline_keyboard": [
                            [{"text": "📝 Change Text", "callback_data": f"settext_{btn_id}"}],
                            [{"text": "✨ Change Emoji ID", "callback_data": f"setemoji_{btn_id}"}],
                            [{"text": "🎨 Change Color", "callback_data": f"setcol_{btn_id}"}]
                        ]}
                        edit_msg(chat_id, msg_id, f"Editing `{btn_id}`:", kb)

                    elif data.startswith("settext_") or data.startswith("setemoji_") or data.startswith("setcol_"):
                        action, btn_id = data.split("_")[0].replace("set", ""), data.split("_")[1]
                        admin_state[user_id] = {"btn": btn_id, "action": action}
                        prompts = {"text": "Send new text:", "emoji": "Send numeric custom emoji ID:", "col": "Send color (blue, green, red):"}
                        send_msg(chat_id, prompts[action])

        except Exception as e:
            print("Loop Error:", e)
            time.sleep(2)

# --- DUMMY SERVER FOR RENDER ---
app = Flask(__name__)
@app.route('/')
def home(): return "Premium Bot is Alive 24/7!"
def run_server(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    run_bot()
