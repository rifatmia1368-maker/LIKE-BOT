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
TOKEN = '8926868360:AAGb9kvjfxrdbritVWvYTC7m751lKU6Hg0c'  # Replace with your Token

# 🌐 20 LIKES API CONFIG (Sends 20 likes)
API_20_URL = 'https://riyad-like-api-ob-52.vercel.app'
API_20_KEY = 'RIYADAH' 

# 🌐 30 LIKES API CONFIG (Sends 30 likes)
API_30_URL = 'http://2.56.246.128:30264'
API_30_KEY = '1SAIFUL1'

# 👑 Admin Settings
ADMIN_IDS_FILE = 'admin_ids.json'
DEFAULT_ADMINS = [7603719412]  # Default admin IDs (Integers)

# Load admin IDs from file
def load_admin_ids():
    if os.path.exists(ADMIN_IDS_FILE):
        try:
            with open(ADMIN_IDS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('admin_ids', DEFAULT_ADMINS.copy())
        except Exception:
            return DEFAULT_ADMINS.copy()
    return DEFAULT_ADMINS.copy()

def save_admin_ids(admin_ids):
    try:
        with open(ADMIN_IDS_FILE, 'w') as f:
            json.dump({'admin_ids': admin_ids}, f, indent=4)
    except Exception as e:
        print(f"Error saving admin IDs: {e}")

ADMIN_IDS = load_admin_ids()

bot = telebot.TeleBot(TOKEN)

ALLOWED_REGIONS = ['ME', 'ID', 'TH', 'VN', 'SG', 'BD', 'PK', 'MY', 'PH', 'RU', 'AFR']
REMAIN_FILE = 'remain_syreo.json'
GROUPS_FILE = 'group_ids.json'
VIP_FILE = 'vip.json'
AUTO_DB_FILE = 'auto_likes.json'

# Global State Variables
bot_is_on = True
USER_LIMIT = 1  # Default limit for normal users
user_usage = {}
pending_requests = {}

# ==========================================
# 🛡️ ADMIN CHECKER & FULL CONTROL
# ==========================================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def admin_full_control(user_id):
    return is_admin(user_id)

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
    default = {
        "time": "08:57 AM", 
        "last_run": "", 
        "tasks": {}, 
        "next_serial": 1,
        "stats": {
            "total_20_tasks": 0,
            "total_30_tasks": 0,
            "total_likes_sent_20": 0,
            "total_likes_sent_30": 0
        }
    }
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
    """Check if a group is allowed to use the bot (supports multiple groups)"""
    groups = load_groups()
    chat_id_str = str(chat_id)
    if chat_id_str in groups:
        expiration = groups[chat_id_str]
        if expiration == "unlimited": 
            return True
        if time.time() < expiration: 
            return True
        # Expired, remove it
        del groups[chat_id_str]
        save_groups(groups)
    return False

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
# 🤖 ADMIN MANAGEMENT COMMAND
# ==========================================
@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ You are not authorized to use this command!", parse_mode="Markdown")
        return
    
    args = message.text.split()
    
    # /admin add <user_id> - Add new admin
    if len(args) == 3 and args[1].lower() == 'add':
        try:
            new_admin_id = int(args[2])
            if new_admin_id in ADMIN_IDS:
                bot.reply_to(message, f"❌ User `{new_admin_id}` is already an admin!", parse_mode="Markdown")
                return
            
            ADMIN_IDS.append(new_admin_id)
            save_admin_ids(ADMIN_IDS)
            bot.reply_to(message, f"✅ **New Admin Added!**\n👑 User ID: `{new_admin_id}`\n📌 This user now has full control over the bot.", parse_mode="Markdown")
            
            # Notify the new admin
            try:
                bot.send_message(new_admin_id, "🎉 **Congratulations!** You have been granted Admin access to the bot.\nYou now have full control over all bot functions.", parse_mode="Markdown")
            except:
                pass
                
        except ValueError:
            bot.reply_to(message, "❌ Invalid User ID! Please provide a valid numeric ID.", parse_mode="Markdown")
    
    # /admin remove <user_id> - Remove admin
    elif len(args) == 3 and args[1].lower() == 'remove':
        try:
            remove_admin_id = int(args[2])
            if remove_admin_id not in ADMIN_IDS:
                bot.reply_to(message, f"❌ User `{remove_admin_id}` is not an admin!", parse_mode="Markdown")
                return
            
            if remove_admin_id == 7603719412:
                bot.reply_to(message, "❌ Cannot remove the master admin (7603719412)!", parse_mode="Markdown")
                return
            
            ADMIN_IDS.remove(remove_admin_id)
            save_admin_ids(ADMIN_IDS)
            bot.reply_to(message, f"✅ **Admin Removed!**\n👑 User ID: `{remove_admin_id}`\n📌 This user no longer has admin access.", parse_mode="Markdown")
            
            # Notify the removed admin
            try:
                bot.send_message(remove_admin_id, "⚠️ **Admin Access Revoked!**\nYou are no longer an admin of this bot.", parse_mode="Markdown")
            except:
                pass
                
        except ValueError:
            bot.reply_to(message, "❌ Invalid User ID! Please provide a valid numeric ID.", parse_mode="Markdown")
    
    # /admin list - List all admins
    elif len(args) == 2 and args[1].lower() == 'list':
        admin_list = ""
        for idx, admin_id in enumerate(ADMIN_IDS, 1):
            master_tag = " 👑 MASTER" if admin_id == 7603719412 else ""
            try:
                user_info = bot.get_chat(admin_id)
                name = user_info.first_name or user_info.username or str(admin_id)
                admin_list += f"{idx}. `{admin_id}` - {name}{master_tag}\n"
            except:
                admin_list += f"{idx}. `{admin_id}`{master_tag}\n"
        
        text = f"""╭━〔 👑 **ADMIN LIST** 〕━⬣
├─ 📊 Total Admins: `{len(ADMIN_IDS)}`
{admin_list}
╰━━━━━━━━━━━━━━━━━━⬣"""
        bot.reply_to(message, text, parse_mode="Markdown")
    
    else:
        bot.reply_to(message, """⚠️ **Admin Command Usage:**

`/admin add <user_id>` - Add new admin
`/admin remove <user_id>` - Remove admin
`/admin list` - List all admins

📌 **Note:** Only existing admins can use these commands.
👑 Master Admin (7603719412) cannot be removed.""", parse_mode="Markdown")

# ==========================================
# 🔧 USER LIMIT COMMAND (New Feature)
# ==========================================
@bot.message_handler(commands=['limit'])
def handle_limit_command(message):
    """Change daily limit for users (admins only)"""
    if not admin_full_control(message.from_user.id):
        bot.reply_to(message, "❌ You are not authorized to use this command!", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/limit <number>`\nExample: `/limit 5`\n\n📌 This sets the daily limit for normal users.", parse_mode="Markdown")
        return
    
    try:
        new_limit = int(args[1])
        if new_limit < 1:
            bot.reply_to(message, "❌ Limit must be at least 1!", parse_mode="Markdown")
            return
        
        global USER_LIMIT
        USER_LIMIT = new_limit
        bot.reply_to(message, f"✅ **User Daily Limit Updated!**\n📊 New limit: `{USER_LIMIT}` requests per day for normal users.", parse_mode="Markdown")
        
    except ValueError:
        bot.reply_to(message, "❌ Please provide a valid number!", parse_mode="Markdown")

# ==========================================
# 🤖 BOT COMMANDS (UPDATED)
# ==========================================
@bot.message_handler(commands=['p0', 'p02', 'remainreset', 'y5', 'y6'])
def handle_admin_commands(message):
    global bot_is_on, bot_remain, user_usage
    if not admin_full_control(message.from_user.id): return 
    command = message.text.split()[0].lower()
    
    if command in ['/p0', '/y1']:
        bot_is_on = True
        bot.reply_to(message, info_ui("SYSTEM ALIVE", "Bot has been turned **ON**."), parse_mode="Markdown")
    elif command in ['/p02', '/y0']:
        bot_is_on = False
        bot.reply_to(message, info_ui("SYSTEM SLEEP", "Bot has been turned **OFF**."), parse_mode="Markdown")
    elif command == '/remainreset':
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

# ==========================================
# 🎯 30 LIKES COMMAND
# ==========================================
@bot.message_handler(commands=['like30'])
def handle_like30(message):
    global bot_remain, user_usage

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    vips = load_vip()
    is_vip = str(user_id) in vips

    if not is_admin(user_id):
        if not bot_is_on: return

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
        bot.reply_to(message, error_ui("INVALID FORMAT", "Use: `/like30 {region} {uid}`"), parse_mode="Markdown")
        return

    region = args[1].upper()
    uid = args[2]

    if region not in ALLOWED_REGIONS:
        bot.reply_to(message, error_ui("INVALID REGION", f"Allowed: `{', '.join(ALLOWED_REGIONS)}`"), parse_mode="Markdown")
        return

    missing_chats = get_missing_chats(user_id)
    if missing_chats:
        pending_requests[user_id] = {'message': message, 'region': region, 'uid': uid, 'type': '30'}
        markup = InlineKeyboardMarkup()
        for chat in missing_chats:
            markup.add(InlineKeyboardButton(text=f"📢 Join {chat['name']}", url=chat['url']))
        markup.add(InlineKeyboardButton(text="✅ I've Joined - Verify", callback_data=f"verify_{user_id}"))
        bot.reply_to(message, f"⚠️ You must join our sponsors!", reply_markup=markup)
        return

    process_like_request(message, region, uid, user_id, user_name, likes_count=30)

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
        pending_requests[user_id] = {'message': message, 'region': region, 'uid': uid, 'type': '20'}
        markup = InlineKeyboardMarkup()
        for chat in missing_chats:
            markup.add(InlineKeyboardButton(text=f"📢 Join {chat['name']}", url=chat['url']))
        markup.add(InlineKeyboardButton(text="✅ I've Joined - Verify", callback_data=f"verify_{user_id}"))
        bot.reply_to(message, f"⚠️ You must join our sponsors!", reply_markup=markup)
        return

    process_like_request(message, region, uid, user_id, user_name, likes_count=20)

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
            process_like_request(req['message'], req['region'], req['uid'], clicker_id, req['message'].from_user.first_name, req.get('type', '20') == '30' and 30 or 20)

def process_like_request(message, region, uid, user_id, user_name, likes_count=20):
    global bot_remain, user_usage
    
    # Select API based on likes count
    if likes_count == 30:
        base_api = API_30_URL
        api_key = API_30_KEY
        api_endpoint = f"{base_api}/like"
    else:
        base_api = API_20_URL
        api_key = API_20_KEY
        api_endpoint = f"{base_api}/like"
    
    wait_msg = bot.reply_to(message, "𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒊𝒏𝒈 𝒍𝒊𝒌𝒆𝒔 𝑺𝒆𝒏𝒅𝒊𝒏𝒈.....🚀")

    try:
        start_time = time.time() 
        # Format URL for 30 likes API (different format)
        if likes_count == 30:
            url = f"{api_endpoint}?api_key={api_key}&server_name={region.lower()}&uid={uid}"
        else:
            url = f"{api_endpoint}?uid={uid}&server_name={region.lower()}&key={api_key}"
        
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
            final_text = report_ui(data, region, status, response_time, remain_requests, likes_count)
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=final_text, parse_mode="HTML")

        elif status == 0:
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("FAILED", "Could not process UID. It may be invalid or maxed."), parse_mode="Markdown")
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("ERROR", "Service is temporarily unavailable."), parse_mode="Markdown")

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("TIMEOUT", "Server is busy. Try again later."), parse_mode="Markdown")

# ==========================================
# 🚀 AUTO-TASK COMMANDS (PACKAGE WISE PERSISTENT)
# ==========================================
@bot.message_handler(commands=['autotime'])
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
    
    # Update package-wise stats
    if package == 20:
        db['stats']['total_20_tasks'] += 1
    else:
        db['stats']['total_30_tasks'] += 1

    db['tasks'][serial_num] = {
        "chat_id": message.chat.id,
        "region": region,
        "uid": uid,
        "package": package,
        "total_target": total_likes,
        "sent": 0,
        "remain": total_likes,
        "days": days,
        "days_completed": 0,
        "nickname": "Waiting for run...",
        "created_at": time.time(),
        "status": "active"
    }
    save_auto_db(db)
    
    bot.reply_to(message, f"""✅ **Auto Task Added Successfully!**
━━━━━━━━━━━━━━━━━━━━━━━
🎓 Task No: `{serial_num}`
🆔 UID: `{uid}`
🌍 Region: `{region}`
💳 Package: `{package}` Likes/Day
📅 Duration: `{days}` Days
🎯 Total Likes: `{total_likes}`

📊 Package Statistics:
├─ 20 Likes Tasks: `{db['stats']['total_20_tasks']}`
└─ 30 Likes Tasks: `{db['stats']['total_30_tasks']}`""", parse_mode="Markdown")

@bot.message_handler(commands=['autoremove'])
def handle_autoremove(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ **Usage:** `/autoremove {uid}`\nExample: `/autoremove 1234567890`\nOr use: `/autoremove task_{serial}`", parse_mode="Markdown")
        return
    
    remove_param = args[1]
    db = load_auto_db()
    tasks = db.get('tasks', {})
    
    found = False
    removed_tasks = []
    
    # Check if removing by UID or serial number
    if remove_param.startswith('task_'):
        serial = remove_param.replace('task_', '')
        if serial in tasks:
            task = tasks[serial]
            removed_tasks.append((serial, task))
            del db['tasks'][serial]
            found = True
            # Update package-wise stats
            if task['package'] == 20:
                db['stats']['total_20_tasks'] = max(0, db['stats']['total_20_tasks'] - 1)
            else:
                db['stats']['total_30_tasks'] = max(0, db['stats']['total_30_tasks'] - 1)
    else:
        # Remove by UID
        for serial, task in list(tasks.items()):
            if task['uid'] == remove_param:
                removed_tasks.append((serial, task))
                del db['tasks'][serial]
                found = True
                # Update package-wise stats
                if task['package'] == 20:
                    db['stats']['total_20_tasks'] = max(0, db['stats']['total_20_tasks'] - 1)
                else:
                    db['stats']['total_30_tasks'] = max(0, db['stats']['total_30_tasks'] - 1)
    
    if found:
        save_auto_db(db)
        msg = f"✅ **Removed {len(removed_tasks)} task(s)**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
        for serial, task in removed_tasks:
            msg += f"""🎓 Task No: `{serial}`
├─ UID: `{task['uid']}`
├─ Package: `{task['package']}` Likes
├─ Sent: `{task['sent']}/{task['total_target']}`
└─ Status: Removed\n\n"""
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ No auto task found with identifier: `{remove_param}`", parse_mode="Markdown")

@bot.message_handler(commands=['listauto'])
def handle_listauto(message):
    if not admin_full_control(message.from_user.id): return
    db = load_auto_db()
    tasks = db.get('tasks', {})
    stats = db.get('stats', {"total_20_tasks": 0, "total_30_tasks": 0, "total_likes_sent_20": 0, "total_likes_sent_30": 0})
    
    count_20 = sum(1 for t in tasks.values() if t['package'] == 20)
    count_30 = sum(1 for t in tasks.values() if t['package'] == 30)
    total_likes_sent_20 = sum(t.get('sent', 0) for t in tasks.values() if t['package'] == 20)
    total_likes_sent_30 = sum(t.get('sent', 0) for t in tasks.values() if t['package'] == 30)
    
    header = f"""<blockquote><b>📊 AUTO-LIKE DATABASE 📊</b></blockquote>
<blockquote><b>📈 SYSTEM OVERVIEW:</b>
├─ 👥 TOTAL ACTIVE TASKS : {len(tasks)}
├─ 💙 20 LIKES TASKS : {count_20}
├─ ❤️‍🔥 30 LIKES TASKS : {count_30}
├─ 📊 Total 20 Likes Sent: {total_likes_sent_20}
├─ 📊 Total 30 Likes Sent: {total_likes_sent_30}
└─ ⏰ NEXT RUN TIME : {db.get('time', 'Not Set')} (BD)</blockquote>\n"""

    msg_body = header
    if tasks:
        # Separate tasks by package type
        tasks_20 = [(s, t) for s, t in tasks.items() if t['package'] == 20]
        tasks_30 = [(s, t) for s, t in tasks.items() if t['package'] == 30]
        
        if tasks_20:
            msg_body += "\n<blockquote><b>💙 20 LIKES TASKS</b></blockquote>\n"
            # FIX: Build message incrementally and split if needed - handle unlimited entries
            tasks_20_added = 0
            for serial, data in tasks_20:
                nickname = data.get('nickname', 'Unknown')
                progress = int((data['sent'] / data['total_target']) * 100) if data['total_target'] > 0 else 0
                task_block = f"""<blockquote>🎓 <b>TASK {serial}</b>
├─ 👤 {nickname}
├─ 🆔 <code>{data['uid']}</code> | {data['region']}
├─ 💳 {data['package']} LIKES/DAY
├─ 📊 SENT: {data['sent']} | REMAIN: {data['remain']}
├─ 📈 PROGRESS: {progress}%
└─ ⏳ DAYS LEFT: {data['days'] - data['days_completed']}</blockquote>\n"""
                # Check if adding this block would exceed limit
                if len(msg_body) + len(task_block) > 3500:  # Leave buffer for safety
                    # Send current message and start new one
                    bot.reply_to(message, msg_body, parse_mode="HTML")
                    msg_body = header + "\n<blockquote><b>💙 20 LIKES TASKS (Continued)</b></blockquote>\n"
                msg_body += task_block
                tasks_20_added += 1
        
        if tasks_30:
            # Add separator if we already sent 20 tasks
            if tasks_20:
                msg_body += "\n<blockquote><b>❤️‍🔥 30 LIKES TASKS</b></blockquote>\n"
            else:
                msg_body += "\n<blockquote><b>❤️‍🔥 30 LIKES TASKS</b></blockquote>\n"
            
            for serial, data in tasks_30:
                nickname = data.get('nickname', 'Unknown')
                progress = int((data['sent'] / data['total_target']) * 100) if data['total_target'] > 0 else 0
                task_block = f"""<blockquote>🎓 <b>TASK {serial}</b>
├─ 👤 {nickname}
├─ 🆔 <code>{data['uid']}</code> | {data['region']}
├─ 💳 {data['package']} LIKES/DAY
├─ 📊 SENT: {data['sent']} | REMAIN: {data['remain']}
├─ 📈 PROGRESS: {progress}%
└─ ⏳ DAYS LEFT: {data['days'] - data['days_completed']}</blockquote>\n"""
                # Check if adding this block would exceed limit
                if len(msg_body) + len(task_block) > 3500:  # Leave buffer for safety
                    # Send current message and start new one
                    bot.reply_to(message, msg_body, parse_mode="HTML")
                    msg_body = header + "\n<blockquote><b>❤️‍🔥 30 LIKES TASKS (Continued)</b></blockquote>\n"
                msg_body += task_block
    else:
        msg_body += "<i>✨ No active auto tasks currently. Use /likeauto to add tasks!</i>"

    # Send final message part
    if msg_body:
        bot.reply_to(message, msg_body, parse_mode="HTML")

@bot.message_handler(commands=['autostats'])
def handle_autostats(message):
    """Show detailed statistics about auto tasks"""
    if not admin_full_control(message.from_user.id): return
    db = load_auto_db()
    stats = db.get('stats', {})
    tasks = db.get('tasks', {})
    
    total_20_sent = stats.get('total_likes_sent_20', 0)
    total_30_sent = stats.get('total_likes_sent_30', 0)
    
    text = f"""╭━〔 📊 **AUTO-LIKE STATISTICS** 〕━⬣
┃
├─ 📈 **TASK OVERVIEW**
├─ 👥 Active Tasks: `{len(tasks)}`
├─ 💙 20-Likes Tasks: `{stats.get('total_20_tasks', 0)}`
├─ ❤️‍🔥 30-Likes Tasks: `{stats.get('total_30_tasks', 0)}`
┃
├─ 📊 **LIKES SENT (ALL TIME)**
├─ 💙 Total 20-Likes: `{total_20_sent}`
├─ ❤️‍🔥 Total 30-Likes: `{total_30_sent}`
├─ 🎯 Total Combined: `{total_20_sent + total_30_sent}`
┃
├─ ⏰ **SCHEDULE**
├─ 🕐 Next Run Time: `{db.get('time', 'Not Set')}`
├─ 📅 Last Run Date: `{db.get('last_run', 'Never')}`
┃
╰━━━━━━━━━━━━━━━━━━⬣"""
    bot.reply_to(message, text, parse_mode="Markdown")

# ==========================================
# 🎯 VIP & GROUP COMMANDS
# ==========================================
@bot.message_handler(commands=['vipadd', 'removevip', 'listvip', 'allow', 'disallow', 'remains'])
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
        chat_id_str = str(message.chat.id)
        dur = args[1].lower()
        if dur == "unlimited": 
            groups[chat_id_str] = "unlimited"
        else:
            try:
                val, unit = int(dur[:-1]), dur[-1]
                mult = {'d': 86400, 'm': 2592000, 'y': 31536000}.get(unit, 0)
                if not mult: raise ValueError
                groups[chat_id_str] = time.time() + (val * mult)
            except: 
                return bot.reply_to(message, "❌ Invalid format. Use: `/allow 7d` or `/allow unlimited`", parse_mode="Markdown")
        save_groups(groups)
        bot.reply_to(message, f"✅ This group has been allowed to use the bot!", parse_mode="Markdown")
    elif cmd == '/disallow':
        groups = load_groups()
        chat_id_str = str(message.chat.id)
        if chat_id_str in groups: 
            del groups[chat_id_str]
            save_groups(groups)
            bot.reply_to(message, "🚫 This group has been disallowed from using the bot.", parse_mode="Markdown")
        else:
            bot.reply_to(message, "ℹ️ This group was not in the allowed list.", parse_mode="Markdown")

# ==========================================
# ⏰ BACKGROUND CRON JOB (BD TIMEZONE) - PERSISTENT WITH PACKAGE TRACKING
# ==========================================
def execute_auto_tasks():
    db = load_auto_db()
    tasks = db.get("tasks", {})
    if not tasks: 
        print("📭 No auto tasks to execute")
        return

    print(f"🚀 Executing {len(tasks)} auto tasks...")
    
    for serial, task in list(tasks.items()):
        uid = task['uid']
        region = task['region']
        package = task['package']
        chat_id = task['chat_id']
        
        print(f"📌 Processing Task {serial}: UID={uid}, Package={package}")
        
        # 🔄 DYNAMIC API SELECTION BASED ON PACKAGE
        if package == 20:
            base_api = API_20_URL
            api_key = API_20_KEY
            url = f"{base_api}/like?uid={uid}&server_name={region.lower()}&key={api_key}"
        else:  # package == 30
            base_api = API_30_URL
            api_key = API_30_KEY
            url = f"{base_api}/like?api_key={api_key}&server_name={region.lower()}&uid={uid}"
        
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
                
                # Update package-wise statistics
                if package == 20:
                    db['stats']['total_likes_sent_20'] = db['stats'].get('total_likes_sent_20', 0) + added
                else:
                    db['stats']['total_likes_sent_30'] = db['stats'].get('total_likes_sent_30', 0) + added
                
                msg_text = auto_report_ui(True, package, response_time, nickname, uid, region, before, added, after, serial)
                bot.send_message(chat_id, msg_text, parse_mode="HTML")
                print(f"✅ Task {serial} SUCCESS: Sent {added} likes")
            else:
                msg_text = auto_report_ui(False, package, response_time, nickname, uid, region, before, 0, after, serial, "ALREADY MAX")
                bot.send_message(chat_id, msg_text, parse_mode="HTML")
                print(f"⚠️ Task {serial} FAILED: Status {status}")
                
        except Exception as e:
            print(f"❌ Task {serial} ERROR: {e}")
            bot.send_message(chat_id, f"⚠️ Auto Task Failed for Task No: {serial} (Timeout/Error).")

        # Save progress after each task
        save_auto_db(db)
        
        # Check if task is completed
        if task['remain'] <= 0:
            task['days_completed'] = task['days']
            bot.send_message(chat_id, f"✅ <b>Task {serial} Completed!</b> Target likes reached. Removed from DB.", parse_mode="HTML")
            # Remove completed task
            db = load_auto_db()  # Reload to get latest
            if serial in db.get('tasks', {}):
                # Update stats before removing
                if db['tasks'][serial]['package'] == 20:
                    db['stats']['total_20_tasks'] = max(0, db['stats'].get('total_20_tasks', 0) - 1)
                else:
                    db['stats']['total_30_tasks'] = max(0, db['stats'].get('total_30_tasks', 0) - 1)
                del db['tasks'][serial]
                save_auto_db(db)
        
        time.sleep(5)  # Delay between tasks to avoid rate limits

def cron_worker():
    """Persistent cron worker that survives bot restarts"""
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
                # Update last_run immediately to prevent duplicate runs
                db['last_run'] = current_date_str
                save_auto_db(db) 
                
                execute_auto_tasks()
                
        except Exception as e:
            print(f"Cron Worker Error: {e}")
            
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    print("🚀 Premium Bot is starting securely...")
    print(f"📌 Master Admin: 7603719412")
    print(f"📌 Total Admins: {len(ADMIN_IDS)}")
    print(f"📌 User Daily Limit: {USER_LIMIT}")
    print("📌 Admin Commands:")
    print("   - /admin add <user_id> - Add new admin")
    print("   - /admin remove <user_id> - Remove admin")
    print("   - /admin list - List all admins")
    print("   - /limit <number> - Set user daily limit")
    print("📌 Auto-Like Commands (Package Wise):")
    print("   - /likeauto {region} {uid} {20/30} {days} - Add auto task")
    print("   - /listauto - List all auto tasks (grouped by package)")
    print("   - /autoremove {uid} - Remove auto tasks")
    print("   - /autostats - Show package-wise statistics")
    print("   - /autotime HH:MM AM/PM - Set execution time")
    print("📌 Other Commands:")
    print("   - /p0 (Turn ON) | /p02 (Turn OFF)")
    print("   - /freeon (Temporary ON)")
    print("   - /vipadd (Add VIP)")
    print("   - /like (20 Likes) | /like30 (30 Likes)")
    print("   - /allow (Allow current group)")
    print("   - /disallow (Disallow current group)")
    print("   - /remainreset (Reset global limits)")
    
    # Start Cron Worker in background
    cron_thread = threading.Thread(target=cron_worker, daemon=True)
    cron_thread.start()
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Bot crashed, restarting in 5 seconds... Error: {e}")
            time.sleep(5)
