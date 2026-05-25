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
TOKEN = '8926868360:AAGb9kvjfxrdbritVWvYTC7m751lKU6Hg0c' # Replace with your Token

# 🌐 20 LIKES API CONFIG (Sends 20 likes)
API_20_URL = 'https://riyad-like-api-ob-52.vercel.app'
API_20_KEY = 'RIYADAH' 

# 🌐 30 LIKES API CONFIG (Sends 30 likes)
API_30_URL = 'https://xxxx.vercel.app'  # Replace with your actual API URL
API_30_KEY = 'xxxx'  # Replace with your actual API key

# 👑 Admin Settings
ADMIN_IDS = [7603719412]  # Add your Admin Telegram IDs here (Integers)

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
# 🛡️ ADMIN CHECKER & FULL CONTROL
# ==========================================
def is_admin(user_id):
    return user_id in ADMIN_IDS

# Admin full control function
def admin_full_control(user_id):
    if is_admin(user_id):
        return True
    return False

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

def load_vip(): 
    return load_json(VIP_FILE, {})

def save_vip(data): 
    save_json(VIP_FILE, data)

def load_groups(): 
    return load_json(GROUPS_FILE, {})

def save_groups(data): 
    save_json(GROUPS_FILE, data)

def load_auto_db(): 
    default = {"time": "08:57 AM", "last_run": "", "tasks": {}, "next_serial": 1}
    return load_json(AUTO_DB_FILE, default)

def save_auto_db(data): 
    save_json(AUTO_DB_FILE, data)

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
    {"id": -1002982043517, "url": "https://t.me/arafatcodex", "name": "ARAFAT CODEX 📡"},
    {"id": -1003761236797, "url": "https://t.me/Syreo_from_bd", "name": "𝙔𝙍𝙀𝙊 𝙇𝙞𝙠𝙚𝙨 𝘾𝙝𝙖𝙣𝙣𝙚𝙡💝"},
    {"id": -1002593537246, "url": "https://t.me/NSlikegroup", "name": "FREE FIRE LIKES GLOBAL ✇ Lite⌛️"}
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
# 🎨 UI TEMPLATES
# ==========================================
def report_ui(data, region, status, response_time, remain_requests, likes_sent):
    nickname = html.escape(str(data.get('PlayerNickname', 'Unknown')))
    uid = data.get('UID', 'Unknown')
    added = data.get('LikesGivenByAPI', 0)
    before = data.get('LikesbeforeCommand', 0)
    after = data.get('LikesafterCommand', 0)

    if status in [1, 2]:
        api_time = round(response_time * 0.8, 2)
        return f"""<blockquote><b>✅ Likes Sent Successfully!</b>
━━━━━━━━━━━━━━━━━━━━━━━
<i>⚡ Speed: {response_time}s</i>
<i>⏱️ API Time: {api_time}s</i>
<b>💎 Likes Sent:</b> <code>{likes_sent}</code>

<b>👤 Account:</b> <code>{nickname}</code>
<b>🆔 UID:</b> <code>{uid}</code>
<b>🌍 Region:</b> <code>{region.upper()}</code>

<b>📈 Before:</b> <code>{before}</code>
<b>❤️ Likes Added:</b> <code>{added}</code>
<b>📉 After:</b> <code>{after}</code>

<i>💎 Remain request : {remain_requests}</i></blockquote>"""
    else:
        return f"""<blockquote><b>❌ Failed to process.</b>
━━━━━━━━━━━━━━━━━━━━━━━
<i>⚠️ Reason: Target reached max or invalid.</i>
<b>📉 Before:</b> <code>{before}</code>
<b>📈 After:</b> <code>{after}</code>
<i>⚡ Speed: {response_time}s</i></blockquote>"""

def auto_report_ui(success, package, speed, nickname, uid, region, before, added, after, serial, reason="ALREADY MAX"):
    if success:
        return f"""<blockquote><b>✅ Auto Likes Sent Successfully! ⚡</b>
━━━━━━━━━━━━━━━━━━━━━━━
💳 Auto Like : {package} Likes
⚡ Speed: {speed}s

👤 Account: {nickname}
🆔 UID: {uid}
🌍 Region: {region.upper()}

📈 Before: {before}
❤️ Likes Added: {added}
📉 After: {after}

🎓 TASK NO : {serial}</blockquote>"""
    else:
        return f"""<blockquote><b>❌ Auto Likes Sent Failed ! ⚡ {{ {reason} }} ❗️</b>
━━━━━━━━━━━━━━━━━━━━━━━
💳 Auto Like : {package} Likes
⚡ Speed: {speed}s

👤 Account: {nickname}
🆔 UID: {uid}
🌍 Region: {region.upper()}

📈 Before: {before}
❤️ Likes Added: {added}
📉 After: {after}

🎓 TASK NO : {serial}</blockquote>"""

def error_ui(title, message):
    return f"╭━〔 ⚠️ **{title}** 〕━⬣\n┃ ❌ {message}\n╰━━━━━━━━━━━━━━━━━━⬣"

def info_ui(title, message):
    return f"╭━〔 ℹ️ **{title}** 〕━⬣\n┃ 💠 {message}\n╰━━━━━━━━━━━━━━━━━━⬣"

# ==========================================
# 🤖 BOT COMMANDS (UPDATED)
# ==========================================
@bot.message_handler(commands=['p0', 'p02', 'resetremain', 'y5', 'y6'])
def handle_admin_commands(message):
    global bot_is_on, bot_remain, user_usage
    if not admin_full_control(message.from_user.id): return 
    command = message.text.split()[0].lower()
    
    if command in ['/p0', '/y5']:
        bot_is_on = True
        bot.reply_to(message, info_ui("SYSTEM ALIVE", "Bot has been turned **ON**."), parse_mode="Markdown")
    elif command in ['/p02', '/y6']:
        bot_is_on = False
        bot.reply_to(message, info_ui("SYSTEM SLEEP", "Bot has been turned **OFF**."), parse_mode="Markdown")
    elif command == '/resetremain':
        bot_remain = 15
        save_remain(bot_remain)
        user_usage.clear()
        bot.reply_to(message, info_ui("SYSTEM RESET", "Global limits reset."), parse_mode="Markdown")

def freeon_worker(chat_id, seconds):
    global bot_is_on
    bot_is_on = True
    for i in range(1, seconds + 1):
        try: bot.send_message(chat_id, str(i))
        except: pass
        time.sleep(1)
    bot_is_on = False
    bot.send_message(chat_id, "🛑 **bot is off now**", parse_mode="Markdown")

@bot.message_handler(commands=['freeon'])
def handle_freeon(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/freeon <seconds>`", parse_mode="Markdown")
        return
    try:
        seconds = int(args[1])
        if seconds <= 0 or seconds > 120: return bot.reply_to(message, "❌ 1-120 seconds only.")
    except:
        return bot.reply_to(message, "❌ Seconds must be a number.")
    bot.reply_to(message, f"✅ Bot is temporarily ON for {seconds} seconds.")
    threading.Thread(target=freeon_worker, args=(message.chat.id, seconds)).start()

# --- VIP & GROUP COMMANDS ---
@bot.message_handler(commands=['vipadd', 'removevip', 'viplist', 'allow', 'disallow', 'remains'])
def handle_vip_group_commands(message):
    cmd = message.text.split()[0].lower()
    user_id = message.from_user.id
    
    if cmd == '/remains':
        if not bot_is_on: return
        vips = load_vip()
        if is_admin(user_id): uses_left = "♾️ Unlimited (Admin)"
        elif str(user_id) in vips: uses_left = f"{vips[str(user_id)]['limit'] - user_usage.get(user_id, 0)}/{vips[str(user_id)]['limit']} (VIP)"
        else: uses_left = f"{USER_LIMIT - user_usage.get(user_id, 0)}/{USER_LIMIT}"
        text = f"╭━〔 🌐 **𝗦𝗬𝗦𝗧𝗘𝗠 𝗥𝗘𝗠𝗔𝗜𝗡𝗦** 〕━⬣\n┃ 🤖 **𝗚𝗹𝗼𝗯𝗮𝗹 𝗕𝗼𝘁:** `{bot_remain}/15`\n┃ 👤 **𝗬𝗼𝘂𝗿 𝗟𝗶𝗺𝗶𝘁:** `{uses_left}`\n╰━━━━━━━━━━━━━━━━━━⬣"
        return bot.reply_to(message, text, parse_mode="Markdown")

    if not admin_full_control(user_id): return
    args = message.text.split()

    if cmd == '/vipadd' and len(args) == 3:
        vips = load_vip()
        vips[args[1]] = {"name": f"User ID: {args[1]}", "limit": int(args[2])}
        save_vip(vips)
        bot.reply_to(message, f"✅ VIP Added: {args[1]} (Limit: {args[2]})")
    elif cmd == '/removevip' and len(args) == 2:
        vips = load_vip()
        if args[1] in vips: del vips[args[1]]; save_vip(vips); bot.reply_to(message, "🚫 VIP Removed.")
    elif cmd == '/viplist':
        vips = load_vip()
        text = "╭━〔 🌟 **𝗩𝗜𝗣 𝗟𝗜𝗦𝗧** 〕━⬣\n"
        for uid, data in vips.items(): text += f"┃ 👤 ID: `{uid}` - Limit: `{data['limit']}`\n"
        text += "╰━━━━━━━━━━━━━━━━━━⬣"
        bot.reply_to(message, text, parse_mode="Markdown")
    elif cmd == '/allow' and len(args) == 2:
        groups = load_groups()
        dur = args[1].lower()
        if dur == "unlimited": groups[str(message.chat.id)] = "unlimited"
        else:
            try:
                val, unit = int(dur[:-1]), dur[-1]
                mult = {'d': 86400, 'm': 2592000, 'y': 31536000}.get(unit, 0)
                if not mult: raise ValueError
                groups[str(message.chat.id)] = time.time() + (val * mult)
            except: return bot.reply_to(message, "❌ Invalid format.")
        save_groups(groups); bot.reply_to(message, "✅ Group Allowed.")
    elif cmd == '/disallow':
        groups = load_groups()
        if str(message.chat.id) in groups: del groups[str(message.chat.id)]; save_groups(groups); bot.reply_to(message, "🚫 Group Disallowed.")

# ==========================================
# 🚀 AUTO-TASK COMMANDS (UPDATED)
# ==========================================
@bot.message_handler(commands=['autotime'])  # Changed from /settime to /autotime
def handle_autotime(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/autotime HH:MM AM/PM`\nExample: `/autotime 04:30 AM`", parse_mode="Markdown")
        return
    
    time_str = args[1].upper()
    db = load_auto_db()
    db['time'] = time_str
    save_auto_db(db)
    bot.reply_to(message, f"✅ Auto-task time set to **{time_str}** (BD TimeZone).", parse_mode="Markdown")

@bot.message_handler(commands=['likeauto'])
def handle_likeauto(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split()
    if len(args) != 5:
        bot.reply_to(message, "⚠️ **Usage:** `/likeauto {region} {uid} {20/30} {days}`\nExample: `/likeauto BD 123456 20 7`", parse_mode="Markdown")
        return

    region, uid, package_str, days_str = args[1].upper(), args[2], args[3], args[4]
    
    if region not in ALLOWED_REGIONS:
        bot.reply_to(message, error_ui("INVALID REGION", f"Allowed: `{', '.join(ALLOWED_REGIONS)}`"), parse_mode="Markdown")
        return
    if package_str not in ['20', '30']:
        bot.reply_to(message, error_ui("INVALID PACKAGE", "Package must be 20 or 30."), parse_mode="Markdown")
        return

    try:
        package, days = int(package_str), int(days_str)
        total_likes = package * days
    except ValueError:
        bot.reply_to(message, "❌ Package and Days must be numbers.", parse_mode="Markdown")
        return

    db = load_auto_db()
    serial_num = str(db['next_serial']).zfill(4) 
    db['next_serial'] += 1

    db['tasks'][serial_num] = {
        "chat_id": message.chat.id,
        "region": region,
        "uid": uid,
        "package": package,
        "total_target": total_likes,
        "sent": 0,
        "remain": total_likes,
        "days": days,
        "nickname": "Waiting for run..."
    }
    save_auto_db(db)
    
    bot.reply_to(message, f"✅ **Auto Task Added!**\n🎓 Task No: `{serial_num}`\n🆔 UID: `{uid}`\n💳 Package: `{package}` for `{days}` days", parse_mode="Markdown")

@bot.message_handler(commands=['autoremove'])  # New command to remove by UID
def handle_autoremove(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/autoremove {uid}`\nExample: `/autoremove 1234567890`", parse_mode="Markdown")
        return
    
    uid_to_remove = args[1]
    db = load_auto_db()
    tasks = db.get('tasks', {})
    
    found = False
    removed_tasks = []
    
    for serial, task in list(tasks.items()):
        if task['uid'] == uid_to_remove:
            removed_tasks.append((serial, task))
            del db['tasks'][serial]
            found = True
    
    if found:
        save_auto_db(db)
        msg = f"✅ **Removed {len(removed_tasks)} task(s) with UID:** `{uid_to_remove}`\n"
        for serial, task in removed_tasks:
            msg += f"└─ 🎓 Task No: `{serial}` | Package: `{task['package']}`\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ No auto task found with UID: `{uid_to_remove}`", parse_mode="Markdown")

@bot.message_handler(commands=['autolist'])
def handle_autolist(message):
    if not admin_full_control(message.from_user.id): return
    db = load_auto_db()
    tasks = db.get('tasks', {})
    
    count_20 = sum(1 for t in tasks.values() if t['package'] == 20)
    count_30 = sum(1 for t in tasks.values() if t['package'] == 30)
    
    header = f"""<blockquote><b>📊 MEMBERSHIP DATABASE 📊</b></blockquote>
<blockquote><b>📈 SYSTEM OVERVIEW:</b>
├─ 👥 TOTAL ACTIVE : {len(tasks)}
├─ ⏳ TOTAL QUEUED : 0
├─ 💙 20 LIKES : {str(count_20).zfill(2)}
└─ ❤️‍🔥 30 LIKES : {str(count_30).zfill(2)}</blockquote>
<blockquote><b>⏰ AUTO TASK TIME : {db.get('time', 'Not Set')} (BD)</b></blockquote>\n"""

    msg_body = header
    for serial, data in tasks.items():
        nickname = data.get('nickname', 'Unknown')
        user_block = f"""<blockquote>👤 {nickname}
├─ 🆔 <code>{data['uid']}</code> | 🇧🇩 {data['region']}
├─ ➡️ PACKAGE TYPE : {data['package']} LIKES
├─ 📊 SENT: {data['sent']} | REMAIN: {data['remain']} ⚡
└─ 🎓 TASK NO: {serial}</blockquote>\n"""
        msg_body += user_block

    if not tasks:
        msg_body += "<i>No active auto tasks currently.</i>"

    bot.reply_to(message, msg_body, parse_mode="HTML")

# ==========================================
# ⏰ BACKGROUND CRON JOB (BD TIMEZONE)
# ==========================================
def execute_auto_tasks():
    db = load_auto_db()
    tasks = db.get("tasks", {})
    if not tasks: return

    for serial, task in list(tasks.items()):
        uid = task['uid']
        region = task['region']
        package = task['package']
        chat_id = task['chat_id']
        
        # 🔄 DYNAMIC API SELECTION BASED ON PACKAGE
        if package == 20:
            base_api = API_20_URL
            api_key = API_20_KEY
        else:  # package == 30
            base_api = API_30_URL
            api_key = API_30_KEY
        
        url = f"{base_api}/like?uid={uid}&server_name={region.lower()}&key={api_key}"
        
        start_time = time.time()
        try:
            response = requests.get(url, timeout=15)
            res_data = response.json()
            response_time = round(time.time() - start_time, 2)
            
            status = res_data.get('status')
            nickname = html.escape(str(res_data.get('PlayerNickname', 'Unknown')))
            added = res_data.get('LikesGivenByAPI', 0)
            before = res_data.get('LikesbeforeCommand', 0)
            after = res_data.get('LikesafterCommand', 0)
            
            if status in [1, 2]:
                task['sent'] += added
                task['remain'] -= added
                task['nickname'] = nickname
                
                msg_text = auto_report_ui(True, package, response_time, nickname, uid, region, before, added, after, serial)
                bot.send_message(chat_id, msg_text, parse_mode="HTML")
            else:
                msg_text = auto_report_ui(False, package, response_time, nickname, uid, region, before, 0, after, serial, "ALREADY MAX")
                bot.send_message(chat_id, msg_text, parse_mode="HTML")
                
        except Exception as e:
            print(f"[AUTO TASK ERROR] {uid}: {e}")
            bot.send_message(chat_id, f"⚠️ Auto Task Failed for Task No: {serial} (Timeout/Error).")

        if task['remain'] <= 0:
            bot.send_message(chat_id, f"✅ <b>Task {serial} Completed!</b> Target likes reached. Removed from DB.", parse_mode="HTML")
            del db['tasks'][serial]
        
        save_auto_db(db)
        time.sleep(5)

def cron_worker():
    print("⏳ Auto-Task Cron Started (Checking BD Timezone)...")
    tz = pytz.timezone('Asia/Dhaka')
    
    while True:
        try:
            now = datetime.datetime.now(tz)
            db = load_auto_db()
            target_time = db.get("time", "04:30 AM")
            last_run = db.get("last_run", "")
            
            current_time_str = now.strftime("%I:%M %p")
            current_date_str = now.strftime("%Y-%m-%d")
            
            if current_time_str == target_time and last_run != current_date_str:
                print(f"🚀 Executing Auto Tasks for {current_date_str} at {current_time_str}")
                db['last_run'] = current_date_str
                save_auto_db(db) 
                
                execute_auto_tasks()
                
        except Exception as e:
            print(f"Cron Worker Error: {e}")
            
        time.sleep(30)

# ==========================================
# 🚀 STANDARD LIKE COMMAND (Uses 20 likes API)
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
        if not is_group_allowed(message.chat.id): return 

    if not is_admin(user_id):
        if is_vip:
            vip_limit = vips[str(user_id)]['limit']
            if user_usage.get(user_id, 0) >= vip_limit:
                bot.reply_to(message, error_ui("LIMIT REACHED", f"Sorry {user_name}, you have used your VIP daily limit."), parse_mode="Markdown")
                return
        else:
            if bot_remain <= 0:
                bot.reply_to(message, error_ui("SYSTEM EMPTY", "Global bot limit exhausted."), parse_mode="Markdown")
                return
            if user_usage.get(user_id, 0) >= USER_LIMIT:
                bot.reply_to(message, error_ui("LIMIT REACHED", f"Sorry {user_name}, you have used your daily limit."), parse_mode="Markdown")
                return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, error_ui("INVALID FORMAT", "Use: `/like {region} {uid}`"), parse_mode="Markdown")
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
        bot.reply_to(message, f"⚠️ You must join our sponsors!", reply_markup=markup)
        return

    process_like_request(message, region, uid, user_id, user_name)

@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def verify_join_callback(call):
    clicker_id = call.from_user.id
    target_user_id = int(call.data.split('_')[1])
    if clicker_id != target_user_id:
        return bot.answer_callback_query(call.id, "❌ This button belongs to another user!", show_alert=True)

    if get_missing_chats(clicker_id):
        bot.answer_callback_query(call.id, "❌ You haven't joined all channels yet!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "✅ Verified! Sending likes...", show_alert=False)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass 
        if clicker_id in pending_requests:
            req = pending_requests.pop(clicker_id)
            process_like_request(req['message'], req['region'], req['uid'], clicker_id, req['message'].from_user.first_name)

def process_like_request(message, region, uid, user_id, user_name):
    global bot_remain, user_usage
    
    # Manual /like command uses 20 likes API
    likes_sent = 20
    base_api = API_20_URL
    api_key = API_20_KEY
    
    wait_msg = bot.reply_to(message, "𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒊𝒏𝒈 𝒍𝒊𝒌𝒆𝒔 𝑺𝒆𝒏𝒅𝒊𝒏𝒈.....🚀")

    try:
        start_time = time.time() 
        url = f"{base_api}/like?uid={uid}&server_name={region.lower()}&key={api_key}"
        
        response = requests.get(url, timeout=15) 
        data = response.json()
        
        response_time = round(time.time() - start_time, 2)
        status = data.get('status')

        if status in [1, 2]:
            vips = load_vip()
            if not is_admin(user_id):
                user_usage[user_id] = user_usage.get(user_id, 0) + 1
                if str(user_id) not in vips:
                    bot_remain -= 1
                    save_remain(bot_remain)
            
            remain_requests = "♾️" if is_admin(user_id) else (vips[str(user_id)]['limit'] - user_usage.get(user_id, 0) if str(user_id) in vips else USER_LIMIT - user_usage.get(user_id, 0))
            final_text = report_ui(data, region, status, response_time, remain_requests, likes_sent)
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=final_text, parse_mode="HTML")

        elif status == 0:
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("FAILED", "Could not process UID. It may be invalid or maxed."), parse_mode="Markdown")
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("ERROR", "Service is temporarily unavailable."), parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("TIMEOUT", "Server is busy. Try again later."), parse_mode="Markdown")

if __name__ == "__main__":
    print("🚀 Premium Bot is starting securely...")
    print("📌 Admin ID: 7603719412 (Full Control)")
    print("📌 Updated Features:")
    print("   - /p0 (Turn ON) | /p02 (Turn OFF)")
    print("   - /freeon (Temporary ON)")
    print("   - /vipadd (Add VIP)")
    print("   - /likeauto (Auto Like Command)")
    print("   - /autotime (Set Auto Task Time)")
    print("   - /autoremove {uid} (Remove Auto Task by UID)")
    print("   - 20 Likes API | 30 Likes API")
    print("   - Admin Full Control Enabled")
    
    # Start Cron Worker in background
    threading.Thread(target=cron_worker, daemon=True).start()
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Bot crashed, restarting in 5 seconds... Error: {e}")
            time.sleep(5)
