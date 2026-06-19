import telebot
import requests
import time
import json
import os
import threading
import html
import datetime
import pytz
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity

# ==========================================
# ⚙️ SECURE BOT CONFIGURATION
# ==========================================
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    TOKEN = '8535435533:AAFE5dytFA45Ilk-a1c5wGZY5HxwvqPd9dE'

# 🌐 API CONFIG
API_20_URL = 'https://riyad-like-api-ob-52.vercel.app'
API_20_KEY = 'RIYADAH' 
API_50_URL = 'http://92.118.206.4:30026'
API_50_KEY = 'SAIFUL'

# 🔗 FORCE JOIN
FORCE_CHANNELS = [
    {"username": "@riyadautolikegroup", "link": "https://t.me/riyadautolikegroup", "name": "Riyad Auto Like Group"},
    {"username": "@riyadalhasanbackupchanel", "link": "https://t.me/riyadalhasanbackupchanel", "name": "Riyad Al Hasan Backup Channel"}
]

# 👑 Admin
ADMIN_IDS_FILE = 'admin_ids.json'
DEFAULT_ADMINS = [7603719412]

# ==========================================
# ✨ PREMIUM EMOJI SYSTEM (MessageEntity Style)
# ==========================================
def pe(emoji_char, emoji_id=None):
    """Create custom emoji entity for MessageEntity"""
    return emoji_char, emoji_id

def build_message(text, emoji_map):
    """
    Build message with custom emoji entities
    emoji_map = {"✅": "6336861449360514102", "❌": "6337033209397649451"}
    """
    entities = []
    for emoji_char, emoji_id in emoji_map.items():
        idx = text.find(emoji_char)
        if idx != -1 and emoji_id:
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=idx,
                length=len(emoji_char),
                custom_emoji_id=emoji_id
            ))
    return text, entities if entities else None

# কাস্টম ইমোজি ম্যাপ - আপনার ID গুলো
EMOJI_ID_MAP = {
    "✅": "6336861449360514102",  # Tested Working
    "❌": "6337033209397649451",
    "⚠️": "6100199534351097095",
    "🚀": "6100430105375415737",
    "⚡": "6100409966273764915",
    "💎": "6100451820730064687",
    "❤️": "6100485115316542792",
    "📊": "6102510630483271620",
    "📈": "6102592514034770678",
    "📉": "6102475626499808862",
    "👤": "6102661242101440205",
    "🆔": "6102863908723236868",
    "🌍": "6102926404792360795",
    "💳": "6102638599033858630",
    "⏰": "6102470558438400435",
    "⏳": "6102462664288509137",
    "🎓": "6100639476441161711",
    "🎯": "6100179369479642954",
    "👑": "6102592514034770678",
    "🟢": "6337048276142924106",
    "🔴": "6337018975876030803",
    "📢": "6102475626499808862",
    "🔄": "6102510630483271620",
    "📅": "6102470558438400435",
    "📌": "6102661242101440205",
    "📭": "6102863908723236868",
    "🌟": "6100485115316542792",
    "💠": "6100451820730064687",
    "🤖": "6100639476441161711",
    "🔥": "6100409966273764915",
    "🏆": "6100430105375415737",
    "🥇": "6100485115316542792",
    "🥈": "6102475626499808862",
    "🥉": "6102510630483271620",
    "🔑": "6102661242101440205",
    "💾": "6102863908723236868",
    "📱": "6102926404792360795",
    "🔍": "6102638599033858630",
    "🚫": "6102470558438400435",
    "📝": "6102462664288509137",
    "💰": "6100639476441161711",
}

def send_premium_message(chat_id, text, reply_markup=None, reply_to=None, parse_mode=None):
    """Send message with premium emoji entities"""
    entities = []
    for emoji_char, emoji_id in EMOJI_ID_MAP.items():
        # Find all occurrences
        pos = -1
        while True:
            pos = text.find(emoji_char, pos + 1)
            if pos == -1:
                break
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=pos,
                length=len(emoji_char),
                custom_emoji_id=emoji_id
            ))
    
    # Sort entities by offset
    entities.sort(key=lambda x: x.offset)
    
    return bot.send_message(
        chat_id, text,
        entities=entities if entities else None,
        reply_markup=reply_markup,
        reply_to_message_id=reply_to.message_id if reply_to else None,
        parse_mode=parse_mode
    )

def reply_premium_message(message, text, reply_markup=None, parse_mode=None):
    """Reply with premium emoji"""
    entities = []
    for emoji_char, emoji_id in EMOJI_ID_MAP.items():
        pos = -1
        while True:
            pos = text.find(emoji_char, pos + 1)
            if pos == -1:
                break
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=pos,
                length=len(emoji_char),
                custom_emoji_id=emoji_id
            ))
    
    entities.sort(key=lambda x: x.offset)
    
    return bot.reply_to(
        message, text,
        entities=entities if entities else None,
        reply_markup=reply_markup,
        parse_mode=parse_mode
    )

# ==========================================
# LOAD ADMIN
# ==========================================
def load_admin_ids():
    if os.path.exists(ADMIN_IDS_FILE):
        try:
            with open(ADMIN_IDS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('admin_ids', DEFAULT_ADMINS.copy())
        except: return DEFAULT_ADMINS.copy()
    return DEFAULT_ADMINS.copy()

def save_admin_ids(admin_ids):
    try:
        with open(ADMIN_IDS_FILE, 'w') as f:
            json.dump({'admin_ids': admin_ids}, f, indent=4)
    except: pass

ADMIN_IDS = load_admin_ids()

bot = telebot.TeleBot(TOKEN)

ALLOWED_REGIONS = ['ME', 'ID', 'TH', 'VN', 'SG', 'BD', 'PK', 'MY', 'PH', 'RU', 'AFR']
GROUPS_FILE = 'group_ids.json'
VIP_FILE = 'vip.json'
AUTO_DB_FILE = 'auto_likes.json'
GROUP_STATUS_FILE = 'group_status.json'
ALL_GROUPS_FILE = 'all_groups.json'

bot_is_on = True
USER_LIMIT = 1
user_usage = {}

# ==========================================
# 🔗 FORCE JOIN
# ==========================================
def check_force_join(user_id):
    not_joined = []
    for channel in FORCE_CHANNELS:
        try:
            member = bot.get_chat_member(channel['username'], user_id)
            if member.status in ['left', 'kicked']:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    return not_joined

def force_join_keyboard(not_joined):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in not_joined:
        markup.add(InlineKeyboardButton(f"📢 Join {channel['name']}", url=channel['link']))
    markup.add(InlineKeyboardButton("🔄 Try Again", callback_data="check_join"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    user_id = call.from_user.id
    not_joined = check_force_join(user_id)
    
    if not not_joined:
        bot.answer_callback_query(call.id, "✅ Verified!")
        bot.edit_message_text("✅ Verification Successful!\n\nYou have joined all required channels.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Not joined!")
        channels_text = "\n".join([f"❌ {ch['name']}" for ch in not_joined])
        bot.edit_message_text(f"⚠️ ACCESS DENIED!\n\n❌ Not joined:\n{channels_text}", call.message.chat.id, call.message.message_id, reply_markup=force_join_keyboard(not_joined))

# ==========================================
# HELPERS
# ==========================================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def admin_full_control(user_id):
    return is_admin(user_id)

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, type(default)) else default
        except: return default
    return default

def save_json(filepath, data):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except: pass

def load_vip(): return load_json(VIP_FILE, {})
def save_vip(data): save_json(VIP_FILE, data)
def load_groups(): return load_json(GROUPS_FILE, {})
def save_groups(data): save_json(GROUPS_FILE, data)
def load_all_groups(): return load_json(ALL_GROUPS_FILE, {})
def save_all_groups(data): save_json(ALL_GROUPS_FILE, data)

def load_auto_db(): 
    default = {"time": "08:57 AM", "last_run": "", "tasks": {}, "next_serial": 1, "stats": {"total_20_tasks": 0, "total_50_tasks": 0, "total_20_likes_sent": 0, "total_50_likes_sent": 0}}
    return load_json(AUTO_DB_FILE, default)

def save_auto_db(data): save_json(AUTO_DB_FILE, data)
def load_group_status(): return load_json(GROUP_STATUS_FILE, {})
def save_group_status(data): save_json(GROUP_STATUS_FILE, data)

def get_group_status(chat_id):
    return load_group_status().get(str(chat_id), True)

def set_group_status(chat_id, status):
    gs = load_group_status(); gs[str(chat_id)] = status; save_group_status(gs)

def is_bot_on_for_chat(chat_id):
    if chat_id > 0: return bot_is_on
    return get_group_status(chat_id)

# ==========================================
# 🚀 LIKE COMMAND
# ==========================================
@bot.message_handler(commands=['like'])
def handle_like(message):
    global user_usage
    user_id = message.from_user.id
    chat_id = message.chat.id
    vips = load_vip()
    is_vip = str(user_id) in vips

    if not is_admin(user_id):
        not_joined = check_force_join(user_id)
        if not_joined:
            channels_text = "\n".join([f"❌ {ch['name']}" for ch in not_joined])
            reply_premium_message(message, f"⚠️ ACCESS DENIED!\n\nHello {message.from_user.first_name}!\n\n❌ Not joined:\n{channels_text}", reply_markup=force_join_keyboard(not_joined))
            return
        if not is_bot_on_for_chat(chat_id):
            reply_premium_message(message, "❌ Bot OFF!"); return
        if is_vip and user_usage.get(user_id, 0) >= vips[str(user_id)]['limit']:
            reply_premium_message(message, "❌ VIP limit!"); return
        if not is_vip and user_usage.get(user_id, 0) >= USER_LIMIT:
            reply_premium_message(message, "❌ Daily limit!"); return

    args = message.text.split()
    if len(args) != 3:
        reply_premium_message(message, "⚠️ /like region uid"); return

    region, uid = args[1].upper(), args[2]
    if region not in ALLOWED_REGIONS:
        reply_premium_message(message, "❌ Invalid region!"); return

    wait_msg = bot.reply_to(message, "🚀 Processing...")

    try:
        start = time.time()
        url = f"{API_50_URL}/like?api_key={API_50_KEY}&server_name={region.lower()}&uid={uid}"
        resp = requests.get(url, timeout=45).json()
        rt = round(time.time() - start, 2)
        status = resp.get('status')

        if status in [1, 2]:
            if not is_admin(user_id): user_usage[user_id] = user_usage.get(user_id, 0) + 1
            vips = load_vip()
            remain = "♾️" if is_admin(user_id) else (vips[str(user_id)]['limit'] - user_usage.get(user_id, 0) if str(user_id) in vips else USER_LIMIT - user_usage.get(user_id, 0))
            nick = html.escape(str(resp.get('PlayerNickname', '?')))
            added = resp.get('LikesGivenByAPI', 0)
            before = resp.get('LikesbeforeCommand', 0)
            after = resp.get('LikesafterCommand', 0)
            api_time = round(rt * 0.8, 2)
            
            text = f"""✅ Likes Sent Successfully!
━━━━━━━━━━━━━━━━━━━━━━━
⚡ Speed: {rt}s | ⏱️ API: {api_time}s
💎 Likes Sent: {50}

👤 Account: {nick}
🆔 UID: {uid}
🌍 Region: {region}

📈 Before: {before}
❤️ Added: {added}
📉 After: {after}

💎 Remaining: {remain}"""
            
            bot.delete_message(chat_id, wait_msg.message_id)
            send_premium_message(chat_id, text)
        else:
            bot.delete_message(chat_id, wait_msg.message_id)
            send_premium_message(chat_id, f"❌ Failed!\nUID may be invalid or maxed.\n⚡ {rt}s")
    except Exception as e:
        try: bot.delete_message(chat_id, wait_msg.message_id)
        except: pass
        send_premium_message(chat_id, f"❌ Error: {str(e)[:50]}")

# ==========================================
# ADMIN COMMANDS
# ==========================================
@bot.message_handler(commands=['admin'])
def handle_admin(message):
    if not is_admin(message.from_user.id):
        reply_premium_message(message, "❌ Not authorized!"); return
    args = message.text.split()
    
    if len(args) == 3 and args[1].lower() == 'add':
        try:
            nid = int(args[2])
            if nid in ADMIN_IDS: reply_premium_message(message, "❌ Already admin!"); return
            ADMIN_IDS.append(nid); save_admin_ids(ADMIN_IDS)
            reply_premium_message(message, f"✅ Admin Added: {nid}")
        except: reply_premium_message(message, "❌ Invalid!")
    elif len(args) == 2 and args[1].lower() == 'list':
        text = f"👑 Admins: {len(ADMIN_IDS)}\n" + "\n".join([f"• {a}" + (" 👑" if a==7603719412 else "") for a in ADMIN_IDS])
        reply_premium_message(message, text)

@bot.message_handler(commands=['glist'])
def handle_glist(message):
    if not admin_full_control(message.from_user.id): return
    all_groups = load_all_groups()
    if not all_groups: reply_premium_message(message, "📭 No groups!"); return
    text = f"📊 Groups: {len(all_groups)}\n"
    for cid, data in all_groups.items():
        status = "🟢" if get_group_status(int(cid)) else "🔴"
        text += f"{status} {data.get('title','?')} | {cid}\n"
    reply_premium_message(message, text)

@bot.message_handler(commands=['p0', 'p02', 'remainreset'])
def handle_controls(message):
    global bot_is_on, user_usage
    if not admin_full_control(message.from_user.id): return
    cmd = message.text.split()[0].lower()
    chat_id = message.chat.id
    
    if cmd == '/p0':
        if chat_id < 0: set_group_status(chat_id, True); reply_premium_message(message, "✅ Group ON!")
        else: bot_is_on = True; reply_premium_message(message, "✅ Global ON!")
    elif cmd == '/p02':
        if chat_id < 0: set_group_status(chat_id, False); reply_premium_message(message, "❌ Group OFF!")
        else: bot_is_on = False; reply_premium_message(message, "❌ Global OFF!")
    elif cmd == '/remainreset':
        user_usage.clear()
        reply_premium_message(message, "✅ Limits reset!")

@bot.message_handler(commands=['remains'])
def handle_remains(message):
    user_id = message.from_user.id
    if not is_admin(user_id) and not is_bot_on_for_chat(message.chat.id):
        reply_premium_message(message, "❌ Bot OFF!"); return
    vips = load_vip()
    if is_admin(user_id): uses = "♾️"
    elif str(user_id) in vips: uses = f"{vips[str(user_id)]['limit'] - user_usage.get(user_id, 0)}/{vips[str(user_id)]['limit']}"
    else: uses = f"{USER_LIMIT - user_usage.get(user_id, 0)}/{USER_LIMIT}"
    reply_premium_message(message, f"👤 Your Limit: {uses}")

# ==========================================
# ⏰ CRON (Simple)
# ==========================================
def cron_worker():
    tz = pytz.timezone('Asia/Dhaka')
    while True:
        try:
            now = datetime.datetime.now(tz); db = load_auto_db()
            target = db.get("time", "04:30 AM"); last = db.get("last_run", "")
            if now.strftime("%I:%M %p") == target and last != now.strftime("%Y-%m-%d"):
                db['last_run'] = now.strftime("%Y-%m-%d"); save_auto_db(db)
        except: pass
        time.sleep(30)

if __name__ == "__main__":
    print("🚀 Premium Like Bot (Premium Emoji) Starting...")
    threading.Thread(target=cron_worker, daemon=True).start()
    print("✅ Bot is running!")
    while True:
        try: bot.polling(none_stop=True, timeout=60)
        except Exception as e: print(f"Restart... {e}"); time.sleep(5)
