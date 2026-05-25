import telebot
import requests
import time
import json
import os
import threading
import html
import datetime
import pytz
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================
# ⚙️ SECURE BOT CONFIGURATION
# ==========================================
TOKEN = '8926868360:AAGb9kvjfxrdbritVWvYTC7m751lKUxxxg0c'  # Replace with your Token

# 🌐 100 LIKES API CONFIG
API_100_URL = 'https://riyad-like-api-ob-52.vercel.app'
API_100_KEY = 'RIYADAH'

# 🌐 220 LIKES API CONFIG
API_220_URL = 'https://xxxx.vercel.app'
API_220_KEY = 'xxxx'

# 👑 Admin Settings
MASTER_ADMIN_IDS = [7603719412, 7603719412]  # Master Admins - Never Reset
ADMIN_IDS_FILE = 'admin_ids.json'

bot = telebot.TeleBot(TOKEN)

ALLOWED_REGIONS = ['ME', 'ID', 'TH', 'VN', 'SG', 'BD', 'PK', 'MY', 'PH', 'RU', 'AFR']
REMAIN_FILE = 'remain_syreo.json'
GROUPS_FILE = 'group_ids.json'
VIP_FILE = 'vip.json'
AUTO_DB_FILE = 'auto_likes.json'

# Global State Variables
bot_is_on = True
USER_LIMIT = 1
user_usage = {}
pending_requests = {}

# ==========================================
# 🛡️ ADMIN MANAGEMENT (Persistent)
# ==========================================
def load_admins():
    if os.path.exists(ADMIN_IDS_FILE):
        try:
            with open(ADMIN_IDS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('additional_admins', [])
        except:
            return []
    return []

def save_admins(additional_admins):
    try:
        with open(ADMIN_IDS_FILE, 'w') as f:
            json.dump({'additional_admins': additional_admins}, f, indent=4)
    except Exception as e:
        print(f"Error saving admins: {e}")

additional_admins = load_admins()

def is_admin(user_id):
    return user_id in MASTER_ADMIN_IDS or user_id in additional_admins

def get_all_admins():
    return MASTER_ADMIN_IDS + additional_admins

# ==========================================
# 📂 FILE MANAGERS
# ==========================================
def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, type(default)) else default
        except Exception:
            return default
    return default

def save_json(filepath, data):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

def load_vip(): return load_json(VIP_FILE, {})
def save_vip(data): save_json(VIP_FILE, data)
def load_groups(): return load_json(GROUPS_FILE, {})
def save_groups(data): save_json(GROUPS_FILE, data)
def load_auto_db(): 
    default = {
        "auto_time": "04:30",  # 24 hour format: HH:MM
        "auto_time_ampm": "AM",
        "last_run": "",
        "tasks": {}, 
        "next_serial": 1,
        "auto_status": "ON"
    }
    return load_json(AUTO_DB_FILE, default)
def save_auto_db(data): save_json(AUTO_DB_FILE, data)

def load_remain():
    data = load_json(REMAIN_FILE, {})
    return data.get('bot_remain', 15)

def save_remain(remain_value):
    save_json(REMAIN_FILE, {'bot_remain': remain_value})

bot_remain = load_remain()

def is_group_allowed(chat_id):
    groups = load_groups()
    chat_id_str = str(chat_id)
    if chat_id_str in groups:
        expiration = groups[chat_id_str]
        if expiration == "unlimited": return True
        if time.time() < expiration: return True
        del groups[chat_id_str]
        save_groups(groups)
    return False

# ==========================================
# 📢 MUST-JOIN CONFIGURATION
# ==========================================
REQUIRED_CHATS = [
    {"id": -1003880872686, "url": "https://t.me/Syreo_212", "name": "SYREO CENTER"},
]

def get_missing_chats(user_id):
    if is_admin(user_id): return []
    missing = []
    for chat in REQUIRED_CHATS:
        try:
            member = bot.get_chat_member(chat['id'], user_id)
            if member.status in ['left', 'kicked']: missing.append(chat)
        except Exception:
            missing.append(chat)
    return missing

# ==========================================
# 🎨 UI TEMPLATES (YOUR EXACT FORMAT)
# ==========================================
def report_ui(data, region, status, remain_requests):
    nickname = html.escape(str(data.get('PlayerNickname', 'Unknown')))
    uid = data.get('UID', 'Unknown')
    added = data.get('LikesGivenByAPI', 0)
    before = data.get('LikesbeforeCommand', 0)
    after = data.get('LikesafterCommand', 0)

    if status in [1, 2]:
        return f"""✅ 𝗟𝗜𝗞𝗘𝗦 𝗦𝗘𝗡𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦
━━━━━━━━━━━━━━━━━━
🆔 | 𝗨𝗜𝗗: <code>{uid}</code>
👤 | 𝗡𝗔𝗠𝗘: <code>{nickname}</code>
🌍 | 𝗥𝗘𝗚𝗜𝗢𝗡: <code>{region.upper()}</code>

❤️ | 𝗕𝗘𝗙𝗢𝗥𝗘: <code>{before}</code>
💖 | 𝗔𝗙𝗧𝗘𝗥: <code>{after}</code>
🎯 | 𝗚𝗜𝗩𝗘𝗡: <code>{added}</code>

✈️ | 𝗥𝗘𝗠𝗔𝗜𝗡 𝗥𝗘𝗤𝗨𝗘𝗦𝗧: <code>{remain_requests}</code>
━━━━━━━━━━━━━━━━━━
👤 | 𝗕𝗼𝘁 𝗢𝘄𝗻𝗲𝗿: @riyadalhasan11"""
    else:
        return f"""❌ 𝗟𝗜𝗞𝗘𝗦 𝗦𝗘𝗡𝗗 𝗙𝗔𝗜𝗟𝗘𝗗
━━━━━━━━━━━━━━━━━━
🆔 | 𝗨𝗜𝗗: <code>{uid}</code>
👤 | 𝗡𝗔𝗠𝗘: <code>{nickname}</code>
🌍 | 𝗥𝗘𝗚𝗜𝗢𝗡: <code>{region.upper()}</code>

❤️ | 𝗕𝗘𝗙𝗢𝗥𝗘: <code>{before}</code>
💖 | 𝗔𝗙𝗧𝗘𝗥: <code>{after}</code>

⚠️ | 𝗥𝗘𝗔𝗦𝗢𝗡: Target reached max or invalid
━━━━━━━━━━━━━━━━━━
👤 | 𝗕𝗼𝘁 𝗢𝘄𝗻𝗲𝗿: @riyadalhasan11"""

def error_ui(title, message):
    return f"""❌ {title}
━━━━━━━━━━━━━━━━━━
⚠️ {message}
━━━━━━━━━━━━━━━━━━
👤 | 𝗕𝗼𝘁 𝗢𝘄𝗻𝗲𝗿: @riyadalhasan11"""

def info_ui(title, message):
    return f"""ℹ️ {title}
━━━━━━━━━━━━━━━━━━
💠 {message}
━━━━━━━━━━━━━━━━━━
👤 | 𝗕𝗼𝘁 𝗢𝘄𝗻𝗲𝗿: @riyadalhasan11"""

# ==========================================
# 🤖 API FUNCTIONS
# ==========================================
def send_like(uid, region, api_url, api_key):
    try:
        url = f"{api_url}/like?uid={uid}&server_name={region.lower()}&key={api_key}"
        response = requests.get(url, timeout=15)
        return response.json()
    except Exception as e:
        print(f"Error sending like: {e}")
        return None

def get_uid_info(uid, region):
    try:
        url = f"{API_100_URL}/userinfo?uid={uid}&server_name={region.lower()}&key={API_100_KEY}"
        response = requests.get(url, timeout=15)
        return response.json()
    except Exception as e:
        print(f"Error fetching UID info: {e}")
        return None

# ==========================================
# 🤖 BOT COMMANDS
# ==========================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_text = """╭━〔 🤖 **AUTO LIKE BOT** 〕━⬣
│
│ ✅ Welcome to Auto Like Bot!
│ 
│ 📌 **User Commands:**
│ • `/like <region> <uid>` - Send likes
│ • `/remains` - Check your limit
│ 
│ 👑 **Admin Commands:**
│ • `/likeauto <uid> <region> <days>` - Setup autolike
│ • `/autolist` - Show all autolikes
│ • `/autostatus <uid>` - Check autolike status
│ • `/autoremove <uid>` - Remove autolike
│ • `/autologs <uid>` - View autolike logs
│ • `/setautotime <HH:MM>` - Set auto time (24h)
│ • `/autooff` - Turn AUTO system OFF
│ • `/autoon` - Turn AUTO system ON
│ • `/autotime` - Check auto time status
│ • `/admin <userid>` - Add new admin
│ • `/removeadmin <userid>` - Remove admin
│ • `/adminlist` - Show all admins
│ • `/vipadd <userid> <limit>` - Add VIP
│ • `/vipremove <userid>` - Remove VIP
│ • `/viplist` - Show VIP list
│ • `/allow <duration>` - Allow group
│ • `/disallow` - Disallow group
│ • `/p0` - Turn bot ON
│ • `/p02` - Turn bot OFF
│ • `/remainreset` - Reset limits
│ • `/freeon <seconds>` - Temp ON
│
╰━━━━━━━━━━━━━━━━━━⬣"""
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['p0', 'p02', 'remainreset'])
def handle_admin_commands(message):
    global bot_is_on, bot_remain, user_usage
    if not is_admin(message.from_user.id): return 

    command = message.text.split()[0].lower()
    if command == '/p0':
        bot_is_on = True
        bot.reply_to(message, info_ui("SYSTEM ALIVE", "Bot has been turned **ON**."), parse_mode="Markdown")
    elif command == '/p02':
        bot_is_on = False
        bot.reply_to(message, info_ui("SYSTEM SLEEP", "Bot has been turned **OFF**."), parse_mode="Markdown")
    elif command == '/remainreset':
        bot_remain = 15
        save_remain(bot_remain)
        user_usage.clear()
        bot.reply_to(message, info_ui("SYSTEM RESET", "Global limits reset."), parse_mode="Markdown")

# --- AUTO TIME COMMANDS ---
@bot.message_handler(commands=['setautotime'])
def handle_setautotime(message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/setautotime <HH:MM>`\nExample: `/setautotime 04:30`\n📌 Use 24-hour format", parse_mode="Markdown")
        return
    
    time_str = args[1]
    try:
        # Validate time format
        hour, minute = map(int, time_str.split(':'))
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError
        auto_db = load_auto_db()
        auto_db['auto_time'] = f"{hour:02d}:{minute:02d}"
        # Calculate AM/PM for display
        ampm = "AM" if hour < 12 else "PM"
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12
        auto_db['auto_time_ampm'] = f"{hour_12:02d}:{minute:02d} {ampm}"
        save_auto_db(auto_db)
        bot.reply_to(message, f"✅ **Auto Time Set Successfully!**\n⏰ New Time: `{auto_db['auto_time_ampm']}` (BD Timezone)", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ **Invalid Time Format!**\nUse: `/setautotime 04:30` (24-hour format)", parse_mode="Markdown")

@bot.message_handler(commands=['autoon'])
def handle_autoon(message):
    if not is_admin(message.from_user.id): return
    auto_db = load_auto_db()
    auto_db['auto_status'] = "ON"
    save_auto_db(auto_db)
    bot.reply_to(message, info_ui("AUTO SYSTEM", "Auto Like System has been turned **ON** ✅"), parse_mode="Markdown")

@bot.message_handler(commands=['autooff'])
def handle_autooff(message):
    if not is_admin(message.from_user.id): return
    auto_db = load_auto_db()
    auto_db['auto_status'] = "OFF"
    save_auto_db(auto_db)
    bot.reply_to(message, info_ui("AUTO SYSTEM", "Auto Like System has been turned **OFF** ❌"), parse_mode="Markdown")

@bot.message_handler(commands=['autotime'])
def handle_autotime(message):
    if not is_admin(message.from_user.id): return
    auto_db = load_auto_db()
    status_text = "🟢 ACTIVE" if auto_db.get('auto_status', 'ON') == "ON" else "🔴 INACTIVE"
    response = f"""╭━〔 ⏰ **AUTO TIME STATUS** 〕━⬣
│🕐 Set Time: `{auto_db.get('auto_time_ampm', '04:30 AM')}`
│📋 Last Run: `{auto_db.get('last_run', 'Never')}`
│⚙️ Auto Status: {status_text}
│📊 Active Tasks: `{len(auto_db.get('tasks', {}))}`
╰━━━━━━━━━━━━━━━━━━⬣"""
    bot.reply_to(message, response, parse_mode="Markdown")

# --- FREE ON COMMAND ---
def freeon_worker(chat_id, seconds):
    global bot_is_on
    original_state = bot_is_on
    bot_is_on = True
    for i in range(1, seconds + 1):
        try: 
            bot.send_message(chat_id, str(i))
        except: 
            pass
        time.sleep(1)
    bot_is_on = original_state
    bot.send_message(chat_id, "🛑 **Bot is back to original state**", parse_mode="Markdown")

@bot.message_handler(commands=['freeon'])
def handle_freeon(message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/freeon <seconds>`\nExample: `/freeon 10`", parse_mode="Markdown")
        return
    try:
        seconds = int(args[1])
        if seconds <= 0 or seconds > 120: 
            bot.reply_to(message, "❌ Duration must be between 1 and 120 seconds.", parse_mode="Markdown")
            return
    except ValueError:
        bot.reply_to(message, "❌ Seconds must be a number.", parse_mode="Markdown")
        return
    bot.reply_to(message, f"✅ Bot is temporarily ON for {seconds} seconds.")
    threading.Thread(target=freeon_worker, args=(message.chat.id, seconds)).start()

# --- ADMIN MANAGEMENT ---
@bot.message_handler(commands=['admin'])
def handle_add_admin(message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/admin <tguserid>`", parse_mode="Markdown")
        return
    try:
        new_admin_id = int(args[1])
        global additional_admins
        if new_admin_id not in MASTER_ADMIN_IDS and new_admin_id not in additional_admins:
            additional_admins.append(new_admin_id)
            save_admins(additional_admins)
            bot.reply_to(message, f"✅ **Admin Added!**\nUser ID: `{new_admin_id}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ User is already an admin.", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Invalid User ID.", parse_mode="Markdown")

@bot.message_handler(commands=['removeadmin'])
def handle_remove_admin(message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/removeadmin <tguserid>`", parse_mode="Markdown")
        return
    try:
        remove_admin_id = int(args[1])
        global additional_admins
        if remove_admin_id in MASTER_ADMIN_IDS:
            bot.reply_to(message, "⚠️ Cannot remove MASTER admin!", parse_mode="Markdown")
            return
        if remove_admin_id in additional_admins:
            additional_admins.remove(remove_admin_id)
            save_admins(additional_admins)
            bot.reply_to(message, f"🚫 **Admin Removed!**\nUser ID: `{remove_admin_id}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ User is not an admin.", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Invalid User ID.", parse_mode="Markdown")

@bot.message_handler(commands=['adminlist'])
def handle_adminlist(message):
    if not is_admin(message.from_user.id): return
    text = "╭━〔 👑 **ADMIN LIST** 〕━⬣\n"
    text += "┃ 🔹 **MASTER ADMINS (Permanent):**\n"
    for admin in MASTER_ADMIN_IDS:
        text += f"┃    • `{admin}`\n"
    if additional_admins:
        text += "┃ 🔸 **ADDITIONAL ADMINS:**\n"
        for admin in additional_admins:
            text += f"┃    • `{admin}`\n"
    else:
        text += "┃ 🔸 No additional admins\n"
    text += "╰━━━━━━━━━━━━━━━━━━⬣"
    bot.reply_to(message, text, parse_mode="Markdown")

# --- VIP COMMANDS ---
@bot.message_handler(commands=['vipadd'])
def handle_vipadd(message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "⚠️ **Usage:** `/vipadd <userid> <limit>`", parse_mode="Markdown")
        return
    target_id = args[1]
    try:
        limit = int(args[2])
    except ValueError:
        bot.reply_to(message, "❌ Limit must be a number.", parse_mode="Markdown")
        return
    vips = load_vip()
    vips[target_id] = {"name": f"User ID: {target_id}", "limit": limit}
    save_vip(vips)
    bot.reply_to(message, f"✅ **VIP Added**\nID: `{target_id}`\nLimit: `{limit}`", parse_mode="Markdown")

@bot.message_handler(commands=['vipremove'])
def handle_vipremove(message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/vipremove <userid>`", parse_mode="Markdown")
        return
    target_id = args[1]
    vips = load_vip()
    if target_id in vips:
        del vips[target_id]
        save_vip(vips)
        bot.reply_to(message, f"🚫 **VIP Removed**\nUser `{target_id}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ User is not in VIP list.", parse_mode="Markdown")

@bot.message_handler(commands=['viplist'])
def handle_viplist(message):
    if not is_admin(message.from_user.id): return
    vips = load_vip()
    if not vips:
        bot.reply_to(message, "ℹ️ **VIP List is empty.**", parse_mode="Markdown")
        return
    text = "╭━〔 🌟 **VIP LIST** 〕━⬣\n"
    for uid, data in vips.items():
        used = user_usage.get(int(uid) if uid.isdigit() else uid, 0)
        text += f"┃ 👤 ID: `{uid}` - Used: `{used}/{data['limit']}`\n"
    text += "╰━━━━━━━━━━━━━━━━━━⬣"
    bot.reply_to(message, text, parse_mode="Markdown")

# --- GROUP COMMANDS ---
@bot.message_handler(commands=['allow'])
def handle_allow(message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/allow <duration>`\nFormats: `30d`, `2m`, `1y`, `unlimited`", parse_mode="Markdown")
        return
    duration_str = args[1].lower()
    chat_id_str = str(message.chat.id)
    groups = load_groups()
    if duration_str == "unlimited":
        groups[chat_id_str] = "unlimited"
        bot.reply_to(message, f"✅ **Group Allowed Permanently**", parse_mode="Markdown")
    else:
        try:
            val = int(duration_str[:-1])
            unit = duration_str[-1]
            if unit == 'd': seconds = val * 86400
            elif unit == 'm': seconds = val * 86400 * 30
            elif unit == 'y': seconds = val * 86400 * 365
            else: raise ValueError
            exp_time = time.time() + seconds
            groups[chat_id_str] = exp_time
            bot.reply_to(message, f"✅ **Group Allowed for {val}{unit}**", parse_mode="Markdown")
        except ValueError:
            bot.reply_to(message, "❌ **Invalid format!**", parse_mode="Markdown")
            return
    save_groups(groups)

@bot.message_handler(commands=['disallow'])
def handle_disallow(message):
    if not is_admin(message.from_user.id): return
    chat_id_str = str(message.chat.id)
    groups = load_groups()
    if chat_id_str in groups:
        del groups[chat_id_str]
        save_groups(groups)
        bot.reply_to(message, "🚫 **Group Disallowed**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ Group not in allowed list.", parse_mode="Markdown")

# --- REMAINS COMMAND ---
@bot.message_handler(commands=['remains'])
def handle_remains(message):
    if not bot_is_on: return
    user_id = message.from_user.id
    vips = load_vip()
    if is_admin(user_id):
        user_uses_left = "♾️ Unlimited (Admin)"
    elif str(user_id) in vips:
        vip_limit = vips[str(user_id)]['limit']
        user_uses_left = f"{vip_limit - user_usage.get(user_id, 0)}/{vip_limit} (VIP)"
    else:
        user_uses_left = f"{USER_LIMIT - user_usage.get(user_id, 0)}/{USER_LIMIT}"
    text = f"""╭━〔 🌐 **SYSTEM REMAINS** 〕━⬣
┃ 🤖 **Global Bot:** `{bot_remain}/15`
┃ 👤 **Your Limit:** `{user_uses_left}`
╰━━━━━━━━━━━━━━━━━━⬣"""
    bot.reply_to(message, text, parse_mode="Markdown")

# ==========================================
# 🚀 LIKE COMMAND
# ==========================================

@bot.message_handler(commands=['like'])
def handle_like(message):
    global bot_remain, user_usage

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    vips = load_vip()
    is_vip = str(user_id) in vips

    if not is_admin(user_id):
        if not bot_is_on: return
        if not is_group_allowed(message.chat.id):
            bot.reply_to(message, error_ui("ACCESS DENIED", "This group is not allowed to use the bot."), parse_mode="Markdown")
            return 

    if not is_admin(user_id):
        if is_vip:
            vip_limit = vips[str(user_id)]['limit']
            if user_usage.get(user_id, 0) >= vip_limit:
                bot.reply_to(message, error_ui("LIMIT REACHED", f"Sorry {user_name}, you have used your VIP daily limit ({vip_limit})."), parse_mode="Markdown")
                return
        else:
            if bot_remain <= 0:
                bot.reply_to(message, error_ui("SYSTEM EMPTY", "The global bot limit (15) has been exhausted."), parse_mode="Markdown")
                return
            if user_usage.get(user_id, 0) >= USER_LIMIT:
                bot.reply_to(message, error_ui("LIMIT REACHED", f"Sorry {user_name}, you have used your daily limit."), parse_mode="Markdown")
                return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, error_ui("INVALID FORMAT", "Use: `/like {region} {uid}`\nExample: `/like BD 14947008828`"), parse_mode="Markdown")
        return

    region = args[1].upper()
    uid = args[2]

    if region not in ALLOWED_REGIONS:
        bot.reply_to(message, error_ui("INVALID REGION", f"Allowed: `{', '.join(ALLOWED_REGIONS)}`"), parse_mode="Markdown")
        return

    missing_chats = get_missing_chats(user_id)
    if missing_chats:
        pending_requests[user_id] = {'message': message, 'region': region, 'uid': uid}
        
        markup = InlineKeyboardMarkup()
        for chat in missing_chats:
            markup.add(InlineKeyboardButton(text=f"📢 Join {chat['name']}", url=chat['url']))
        
        markup.add(InlineKeyboardButton(text="✅ I've Joined - Verify", callback_data=f"verify_{user_id}"))

        bot.reply_to(
            message, 
            f"╭━〔 ⚠️ **ACCESS DENIED** 〕━⬣\n┃ [{user_name}](tg://user?id={user_id}), you must join our sponsors to use this bot!\n╰━━━━━━━━━━━━━━━━━━⬣", 
            reply_markup=markup, 
            parse_mode="Markdown"
        )
        return

    process_like_request(message, region, uid, user_id, user_name)

@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def verify_join_callback(call):
    clicker_id = call.from_user.id
    target_user_id = int(call.data.split('_')[1])

    if clicker_id != target_user_id:
        bot.answer_callback_query(call.id, "❌ This button belongs to another user!", show_alert=True)
        return

    missing_chats = get_missing_chats(clicker_id)
    if missing_chats:
        bot.answer_callback_query(call.id, "❌ You haven't joined all channels yet!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "✅ Verified! Sending likes...", show_alert=False)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass 

        if clicker_id in pending_requests:
            req = pending_requests.pop(clicker_id)
            process_like_request(req['message'], req['region'], req['uid'], clicker_id, req['message'].from_user.first_name)
        else:
            bot.send_message(call.message.chat.id, "⚠️ Session expired. Please send your `/like` command again.", parse_mode="Markdown")

def process_like_request(message, region, uid, user_id, user_name):
    global bot_remain, user_usage
    
    wait_msg = bot.reply_to(message, "𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐥𝐢𝐤𝐞𝐬 𝐒𝐞𝐧𝐝𝐢𝐧𝐠.....🚀")

    try:
        result = send_like(uid, region, API_100_URL, API_100_KEY)
        
        if not result:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=wait_msg.message_id,
                text=error_ui("ERROR", "API is not responding. Please try again."),
                parse_mode="Markdown"
            )
            return
        
        status = result.get('status')

        if status in [1, 2]:
            vips = load_vip()
            
            if not is_admin(user_id):
                user_usage[user_id] = user_usage.get(user_id, 0) + 1
                if str(user_id) not in vips:
                    bot_remain -= 1
                    save_remain(bot_remain)
            
            if is_admin(user_id):
                remain_requests = "♾️" 
            elif str(user_id) in vips:
                vip_limit = vips[str(user_id)]['limit']
                remain_requests = vip_limit - user_usage.get(user_id, 0)
            else:
                remain_requests = USER_LIMIT - user_usage.get(user_id, 0)

            final_text = report_ui(result, region, status, remain_requests)
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=final_text, parse_mode="HTML")

        elif status == 0:
            final_text = error_ui("FAILED", "Could not process UID. It may be invalid or already maxed out.")
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=final_text, parse_mode="Markdown")
        else:
            final_text = error_ui("ERROR", "Service is temporarily unavailable.")
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=final_text, parse_mode="Markdown")

    except Exception as e:
        print(f"[ERROR] Like request failed: {e}")
        bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=wait_msg.message_id, 
            text=error_ui("TIMEOUT", "The server is currently busy. Please try again later."), 
            parse_mode="Markdown"
        )

# ==========================================
# 🚀 LIKEAUTO COMMAND (AUTOLIKE SETUP)
# ==========================================

@bot.message_handler(commands=['likeauto'])
def handle_likeauto(message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) != 4:
        bot.reply_to(message, "⚠️ **Usage:** `/likeauto <uid> <region> <days>`\nExample: `/likeauto 123456789 BD 30`", parse_mode="Markdown")
        return
    
    uid = args[1]
    region = args[2].upper()
    
    try:
        days = int(args[3])
        if days <= 0 or days > 365:
            bot.reply_to(message, "❌ Days must be between 1 and 365.", parse_mode="Markdown")
            return
    except ValueError:
        bot.reply_to(message, "❌ Days must be a number.", parse_mode="Markdown")
        return
    
    if region not in ALLOWED_REGIONS:
        bot.reply_to(message, error_ui("INVALID REGION", f"Allowed: `{', '.join(ALLOWED_REGIONS)}`"), parse_mode="Markdown")
        return
    
    # Check if UID already in autolike
    autolike_data = load_auto_db()
    tasks = autolike_data.get('tasks', {})
    for existing in tasks.values():
        if existing.get('uid') == uid:
            bot.reply_to(message, f"❌ UID `{uid}` is already in autolike system!", parse_mode="Markdown")
            return
    
    # Get UID info
    uid_info = get_uid_info(uid, region)
    if not uid_info:
        bot.reply_to(message, error_ui("ERROR", "Failed to fetch UID information. Check UID and Region."), parse_mode="Markdown")
        return
    
    # Create autolike entry
    serial_num = str(autolike_data.get('next_serial', 1)).zfill(4)
    autolike_data['next_serial'] = autolike_data.get('next_serial', 1) + 1
    added_date = datetime.datetime.now().strftime("%Y-%m-%d")
    expiry_date = time.time() + (days * 86400)
    
    autolike_data['tasks'][serial_num] = {
        'uid': uid,
        'region': region,
        'added_date': added_date,
        'expiry': expiry_date,
        'days': days,
        'status': 'active',
        'chat_id': message.chat.id
    }
    
    save_auto_db(autolike_data)
    
    nickname = html.escape(str(uid_info.get('PlayerNickname', 'Unknown')))
    
    response_text = f"""╭━〔 ✅ **AUTOLIKE ACTIVATED** 〕━⬣
│🆔 UID: `{uid}`
│🌍 Region: {region}
│👤 Name: {nickname}
│📅 Added: {added_date}
│📆 Expires: {(datetime.datetime.now() + datetime.timedelta(days=days)).strftime('%Y-%m-%d')}
│⏰ Duration: {days} days
│🎓 Task No: `{serial_num}`
│
│🔄 Will run daily at {autolike_data.get('auto_time_ampm', '04:30 AM')} (BD Timezone)
╰━━━━━━━━━━━━━━━━━━⬣"""
    
    bot.reply_to(message, response_text, parse_mode="Markdown")

@bot.message_handler(commands=['autolist'])
def handle_autolist(message):
    if not is_admin(message.from_user.id):
        return
    
    autolike_data = load_auto_db()
    tasks = autolike_data.get('tasks', {})
    
    if not tasks:
        bot.reply_to(message, "ℹ️ **No active autolike requests found.**", parse_mode="Markdown")
        return
    
    current_time = time.time()
    response = "╭━〔 📋 **ACTIVE AUTOLIKE LIST** 〕━⬣\n"
    
    for serial, data in list(tasks.items())[:20]:
        uid = data['uid']
        region = data['region']
        added_date = data.get('added_date', 'Unknown')
        expiry_date = data.get('expiry', 0)
        days_left = int((expiry_date - current_time) / 86400) if current_time < expiry_date else 0
        status = "✅" if current_time < expiry_date else "❌"
        
        response += f"""│
│🎓 **TASK:** `{serial}`
│🆔 **UID:** `{uid}`
│🌍 **Region:** {region}
│📅 **Added:** {added_date}
│📆 **Expires:** {datetime.datetime.fromtimestamp(expiry_date).strftime('%Y-%m-%d') if expiry_date else 'N/A'}
│⏰ **Days Left:** {days_left} {status}
│━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    response += f"│⏰ Auto Time: {autolike_data.get('auto_time_ampm', '04:30 AM')}\n"
    response += "╰━━━━━━━━━━━━━━━━━━⬣"
    
    if len(response) > 4000:
        bot.reply_to(message, "📋 List is too long. Check auto_likes.json file.", parse_mode="Markdown")
    else:
        bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['autostatus'])
def handle_autostatus(message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/autostatus <uid>`", parse_mode="Markdown")
        return
    
    uid = args[1]
    autolike_data = load_auto_db()
    tasks = autolike_data.get('tasks', {})
    
    found = None
    for serial, data in tasks.items():
        if data['uid'] == uid:
            found = (serial, data)
            break
    
    if not found:
        bot.reply_to(message, f"❌ No autolike found for UID: `{uid}`", parse_mode="Markdown")
        return
    
    serial, data = found
    current_time = time.time()
    expiry_date = data.get('expiry', 0)
    days_left = int((expiry_date - current_time) / 86400) if current_time < expiry_date else 0
    status = "🟢 ACTIVE" if current_time < expiry_date else "🔴 EXPIRED"
    
    # Get UID info
    uid_info = get_uid_info(data['uid'], data['region'])
    if uid_info:
        nickname = html.escape(str(uid_info.get('PlayerNickname', 'Unknown')))
        before = uid_info.get('LikesbeforeCommand', 0)
        after = uid_info.get('LikesafterCommand', 0)
        given = after - before if after > before else 0
        level = uid_info.get('Level', 'Unknown')
    else:
        nickname = 'Unknown'
        before = 0
        after = 0
        given = 0
        level = 'Unknown'
    
    response = f"""╭━⟮ 🆔 UID: {data['uid']} ⟯
│🌍 REGION: {data['region']}
│⚠️ STATUS: {status}
│👤 NAME: {nickname}
│⭐ LEVEL: {level}
│👍 BEFORE: {before}
│❤️ AFTER: {after}
│➕ GIVEN: {given}
│📅 ADDED: {data.get('added_date', 'Unknown')}
│📆 EXPIRES: {datetime.datetime.fromtimestamp(expiry_date).strftime('%Y-%m-%d') if expiry_date else 'N/A'}
│📅 DAYS LEFT: {days_left}
│🎓 TASK NO: {serial}
╰━━━━━━━━━━━━━━━✪"""
    
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['autoremove'])
def handle_autoremove(message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/autoremove <uid>`", parse_mode="Markdown")
        return
    
    uid = args[1]
    autolike_data = load_auto_db()
    tasks = autolike_data.get('tasks', {})
    
    removed = False
    for serial, data in list(tasks.items()):
        if data['uid'] == uid:
            del tasks[serial]
            removed = True
            break
    
    if removed:
        autolike_data['tasks'] = tasks
        save_auto_db(autolike_data)
        bot.reply_to(message, f"✅ **AutoLike Removed**\nUID: `{uid}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ No autolike found for UID: `{uid}`", parse_mode="Markdown")

@bot.message_handler(commands=['autologs'])
def handle_autologs(message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/autologs <uid>`", parse_mode="Markdown")
        return
    
    uid = args[1]
    bot.reply_to(message, f"📋 **Logs for UID: {uid}**\n\nComing soon! Logs feature under development.", parse_mode="Markdown")

# ==========================================
# ⏰ BACKGROUND AUTO TASK WORKER
# ==========================================

def execute_auto_tasks():
    auto_db = load_auto_db()
    tasks = auto_db.get('tasks', {})
    
    if auto_db.get('auto_status', 'ON') != "ON":
        print("Auto system is OFF, skipping...")
        return
    
    if not tasks:
        print("No auto tasks found.")
        return
    
    print(f"🚀 Executing {len(tasks)} auto tasks...")
    
    for serial, task in list(tasks.items()):
        uid = task['uid']
        region = task['region']
        chat_id = task.get('chat_id')
        
        if not chat_id:
            continue
        
        # Send like using 100 likes API
        result = send_like(uid, region, API_100_URL, API_100_KEY)
        
        if result and result.get('status') in [1, 2]:
            nickname = html.escape(str(result.get('PlayerNickname', 'Unknown')))
            added = result.get('LikesGivenByAPI', 0)
            before = result.get('LikesbeforeCommand', 0)
            after = result.get('LikesafterCommand', 0)
            
            msg = f"""✅ **AUTO LIKE SUCCESS** ⚡
━━━━━━━━━━━━━━━━━━
🎓 Task: `{serial}`
🆔 UID: `{uid}`
👤 Name: {nickname}
🌍 Region: {region.upper()}

❤️ Before: {before}
💖 Added: +{added}
📉 After: {after}
━━━━━━━━━━━━━━━━━━
👤 Bot Owner: @riyadalhasan11"""
            
            try:
                bot.send_message(chat_id, msg, parse_mode="HTML")
            except:
                pass
        else:
            msg = f"""❌ **AUTO LIKE FAILED** ⚡
━━━━━━━━━━━━━━━━━━
🎓 Task: `{serial}`
🆔 UID: `{uid}`
🌍 Region: {region.upper()}

⚠️ Reason: MAX REACHED or Invalid UID
━━━━━━━━━━━━━━━━━━
👤 Bot Owner: @riyadalhasan11"""
            
            try:
                bot.send_message(chat_id, msg, parse_mode="HTML")
            except:
                pass
        
        # Check if expired
        if time.time() > task.get('expiry', 0):
            del auto_db['tasks'][serial]
            try:
                bot.send_message(chat_id, f"⏰ **Task {serial} Expired!** Removed from auto system.", parse_mode="HTML")
            except:
                pass
        
        save_auto_db(auto_db)
        time.sleep(3)

def auto_task_scheduler():
    """Background worker that runs every minute and executes tasks at scheduled time"""
    print("⏰ Auto Task Scheduler Started...")
    last_run_date = ""
    tz = pytz.timezone('Asia/Dhaka')
    
    while True:
        try:
            now = datetime.datetime.now(tz)
            current_time_24h = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")
            
            auto_db = load_auto_db()
            target_time = auto_db.get('auto_time', "04:30")
            auto_status = auto_db.get('auto_status', "ON")
            
            # Check if it's time to run and not run today
            if current_time_24h == target_time and last_run_date != current_date and auto_status == "ON":
                print(f"🕐 Running auto tasks at {current_time_24h} on {current_date}")
                execute_auto_tasks()
                last_run_date = current_date
                
                # Update last run in DB
                auto_db['last_run'] = current_date
                save_auto_db(auto_db)
                
                # Wait 60 seconds to avoid multiple runs
                time.sleep(60)
            
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            print(f"Auto Task Scheduler Error: {e}")
            time.sleep(30)

# ==========================================
# 🚀 BOT START
# ==========================================

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 PREMIUM BOT STARTING...")
    print(f"🤖 Bot Token: {TOKEN[:10]}...")
    print(f"👑 Master Admins: {MASTER_ADMIN_IDS}")
    print(f"👥 Additional Admins: {additional_admins}")
    print(f"🌍 Allowed Regions: {ALLOWED_REGIONS}")
    print("⏰ Auto Task Scheduler Started")
    print("=" * 50)
    
    # Start Auto Task Scheduler in background
    scheduler_thread = threading.Thread(target=auto_task_scheduler, daemon=True)
    scheduler_thread.start()
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"❌ Bot crashed: {e}")
            print("🔄 Restarting in 5 seconds...")
            time.sleep(5)
