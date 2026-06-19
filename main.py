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
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    TOKEN = '8702944221:AAGBbL8pgfC5GZiFEIrOmCD2DZoXQ37W-r8'

# 🌐 20 LIKES API CONFIG (Sends 20 likes)
API_20_URL = 'https://riyad-like-api-ob-52.vercel.app'
API_20_KEY = 'RIYADAH' 

# 🌐 50 LIKES API CONFIG (Sends 50 likes)
API_50_URL = 'http://92.118.206.4:30026'
API_50_KEY = 'SAIFUL'

# 🔗 FORCE JOIN CHANNELS
FORCE_CHANNELS = [
    {"username": "@riyadautolikegroup", "link": "https://t.me/riyadautolikegroup", "name": "Riyad Auto Like Group"},
    {"username": "@riyadalhasanbackupchanel", "link": "https://t.me/riyadalhasanbackupchanel", "name": "Riyad Al Hasan Backup Channel"}
]

# 👑 Admin Settings
ADMIN_IDS_FILE = 'admin_ids.json'
DEFAULT_ADMINS = [7603719412]

# ==========================================
# ✨ PREMIUM ANIMATED EMOJI SYSTEM
# ==========================================
def pe(name):
    """Premium Animated Emoji - সব ইউজার Animated দেখবে"""
    emojis = {
        # Status Emojis
        "check": '<emoji id="5368324170671202286">✅</emoji>',
        "cross": '<emoji id="5368324170671202287">❌</emoji>',
        "warning": '<emoji id="5368324170671202288">⚠️</emoji>',
        "info": '<emoji id="5368324170671202320">ℹ️</emoji>',
        
        # Action Emojis
        "fire": '<emoji id="5368324170671202289">🔥</emoji>',
        "bolt": '<emoji id="5368324170671202291">⚡</emoji>',
        "rocket": '<emoji id="5368324170671202292">🚀</emoji>',
        "refresh": '<emoji id="5368324170671202303">🔄</emoji>',
        "search": '<emoji id="5368324170671202325">🔍</emoji>',
        "pause": '<emoji id="5368324170671202326">⏸️</emoji>',
        "play": '<emoji id="5368324170671202327">▶️</emoji>',
        "ban": '<emoji id="5368324170671202328">🚫</emoji>',
        
        # Object Emojis
        "diamond": '<emoji id="5368324170671202290">💎</emoji>',
        "crown": '<emoji id="5368324170671202293">👑</emoji>',
        "star": '<emoji id="5368324170671202316">🌟</emoji>',
        "trophy": '<emoji id="5368324170671202312">🏆</emoji>',
        "gold": '<emoji id="5368324170671202313">🥇</emoji>',
        "silver": '<emoji id="5368324170671202314">🥈</emoji>',
        "bronze": '<emoji id="5368324170671202315">🥉</emoji>',
        "key": '<emoji id="5368324170671202322">🔑</emoji>',
        "save": '<emoji id="5368324170671202324">💾</emoji>',
        "mobile": '<emoji id="5368324170671202323">📱</emoji>',
        "money": '<emoji id="5368324170671202330">💰</emoji>',
        "note": '<emoji id="5368324170671202329">📝</emoji>',
        "pin": '<emoji id="5368324170671202318">📌</emoji>',
        
        # Chart Emojis
        "chart": '<emoji id="5368324170671202294">📊</emoji>',
        "chart_up": '<emoji id="5368324170671202295">📈</emoji>',
        "chart_down": '<emoji id="5368324170671202296">📉</emoji>',
        
        # Heart Emojis
        "heart": '<emoji id="5368324170671202297">❤️</emoji>',
        "blue_heart": '<emoji id="5368324170671202298">💙</emoji>',
        "heart_fire": '<emoji id="5368324170671202297">❤️‍🔥</emoji>',
        
        # Circle Emojis
        "green_circle": '<emoji id="5368324170671202299">🟢</emoji>',
        "red_circle": '<emoji id="5368324170671202300">🔴</emoji>',
        
        # People/User Emojis
        "user": '<emoji id="5368324170671202306">👤</emoji>',
        "users": '<emoji id="5368324170671202306">👥</emoji>',
        "graduate": '<emoji id="5368324170671202301">🎓</emoji>',
        "bot": '<emoji id="5368324170671202321">🤖</emoji>',
        
        # UI Emojis
        "id": '<emoji id="5368324170671202307">🆔</emoji>',
        "globe": '<emoji id="5368324170671202308">🌍</emoji>',
        "card": '<emoji id="5368324170671202309">💳</emoji>',
        "clock": '<emoji id="5368324170671202305">⏰</emoji>',
        "calendar": '<emoji id="5368324170671202304">📅</emoji>',
        "hourglass": '<emoji id="5368324170671202310">⏳</emoji>',
        "target": '<emoji id="5368324170671202311">🎯</emoji>',
        "speaker": '<emoji id="5368324170671202302">📢</emoji>',
        "empty": '<emoji id="5368324170671202319">📭</emoji>',
        "diamond2": '<emoji id="5368324170671202317">💠</emoji>',
    }
    return emojis.get(name, name)

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
GROUPS_FILE = 'group_ids.json'
VIP_FILE = 'vip.json'
AUTO_DB_FILE = 'auto_likes.json'
GROUP_STATUS_FILE = 'group_status.json'
ALL_GROUPS_FILE = 'all_groups.json'

# Global State Variables
bot_is_on = True
USER_LIMIT = 1
user_usage = {}

# ==========================================
# 🔗 FORCE JOIN CHECKER
# ==========================================
def check_force_join(user_id):
    """Check if user has joined all required channels"""
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
    """Generate inline keyboard for joining channels"""
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in not_joined:
        markup.add(InlineKeyboardButton(f"{pe('speaker')} Join {channel['name']}", url=channel['link']))
    markup.add(InlineKeyboardButton(f"{pe('refresh')} Try Again", callback_data="check_join"))
    return markup

# ==========================================
# 🔄 CALLBACK FOR CHECK JOIN
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    user_id = call.from_user.id
    not_joined = check_force_join(user_id)
    
    if not not_joined:
        bot.answer_callback_query(call.id, f"{pe('check')} Verification Successful! You can now use the bot.")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"<b>{pe('check')} Verification Successful!</b>\n\nYou have joined all required channels. You can now use the bot commands.",
            parse_mode="HTML"
        )
    else:
        bot.answer_callback_query(call.id, f"{pe('cross')} You still haven't joined all channels!")
        channels_text = "\n".join([f"{pe('cross')} {ch['name']}" for ch in not_joined])
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"""<b>{pe('warning')} ACCESS DENIED!</b>

<b>{pe('cross')} You haven't joined:</b>
{channels_text}

<i>Please join all channels and click Try Again.</i>""",
            parse_mode="HTML",
            reply_markup=force_join_keyboard(not_joined)
        )

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

def load_all_groups():
    return load_json(ALL_GROUPS_FILE, {})

def save_all_groups(data):
    save_json(ALL_GROUPS_FILE, data)

def load_auto_db(): 
    default = {
        "time": "08:57 AM", 
        "last_run": "", 
        "tasks": {}, 
        "next_serial": 1,
        "stats": {
            "total_20_tasks": 0,
            "total_50_tasks": 0,
            "total_20_likes_sent": 0,
            "total_50_likes_sent": 0
        }
    }
    return load_json(AUTO_DB_FILE, default)

def save_auto_db(data): 
    save_json(AUTO_DB_FILE, data)

def load_group_status():
    return load_json(GROUP_STATUS_FILE, {})

def save_group_status(data):
    save_json(GROUP_STATUS_FILE, data)

def get_group_status(chat_id):
    group_status = load_group_status()
    chat_id_str = str(chat_id)
    return group_status.get(chat_id_str, True)

def set_group_status(chat_id, status):
    group_status = load_group_status()
    chat_id_str = str(chat_id)
    group_status[chat_id_str] = status
    save_group_status(group_status)

def is_bot_on_for_chat(chat_id):
    if chat_id > 0:
        return bot_is_on
    else:
        return get_group_status(chat_id)

def is_group_allowed(chat_id):
    groups = load_groups()
    chat_id_str = str(chat_id)
    if chat_id_str in groups:
        expiration = groups[chat_id_str]
        if expiration == "unlimited": 
            return True
        if time.time() < expiration: 
            return True
        del groups[chat_id_str]
        save_groups(groups)
    return False

# ==========================================
# 🎨 PREMIUM EMOJI UI TEMPLATES
# ==========================================
def report_ui(data, region, status, response_time, remain_requests, likes_sent):
    nickname = html.escape(str(data.get('PlayerNickname', 'Unknown')))
    uid = data.get('UID', 'Unknown')
    added = data.get('LikesGivenByAPI', 0)
    before = data.get('LikesbeforeCommand', 0)
    after = data.get('LikesafterCommand', 0)

    if status in [1, 2]:
        api_time = round(response_time * 0.8, 2)
        return f"""<blockquote><b>{pe('check')} Likes Sent Successfully!</b>
━━━━━━━━━━━━━━━━━━━━━━━
<i>{pe('bolt')} Speed: {response_time}s</i>
<i>{pe('clock')} API Time: {api_time}s</i>
<b>{pe('diamond')} Likes Sent:</b> <code>{likes_sent}</code>

<b>{pe('user')} Account:</b> <code>{nickname}</code>
<b>{pe('id')} UID:</b> <code>{uid}</code>
<b>{pe('globe')} Region:</b> <code>{region.upper()}</code>

<b>{pe('chart_up')} Before:</b> <code>{before}</code>
<b>{pe('heart')} Likes Added:</b> <code>{added}</code>
<b>{pe('chart_down')} After:</b> <code>{after}</code>

<i>{pe('diamond')} Your Remaining: {remain_requests}</i></blockquote>"""
    else:
        return f"""<blockquote><b>{pe('cross')} Failed to process.</b>
━━━━━━━━━━━━━━━━━━━━━━━
<i>{pe('warning')} Reason: Target reached max or invalid.</i>
<b>{pe('chart_down')} Before:</b> <code>{before}</code>
<b>{pe('chart_up')} After:</b> <code>{after}</code>
<i>{pe('bolt')} Speed: {response_time}s</i></blockquote>"""

def auto_report_ui(success, package, speed, nickname, uid, region, before, added, after, serial, reason="ALREADY MAX"):
    if success:
        return f"""<blockquote><b>{pe('check')} Auto Likes Sent Successfully! {pe('bolt')}</b>
━━━━━━━━━━━━━━━━━━━━━━━
{pe('card')} Auto Like : {package} Likes
{pe('bolt')} Speed: {speed}s

{pe('user')} Account: {nickname}
{pe('id')} UID: {uid}
{pe('globe')} Region: {region.upper()}

{pe('chart_up')} Before: {before}
{pe('heart')} Likes Added: {added}
{pe('chart_down')} After: {after}

{pe('graduate')} TASK NO : {serial}</blockquote>"""
    else:
        return f"""<blockquote><b>{pe('cross')} Auto Likes Sent Failed ! {pe('bolt')} {{ {reason} }} ❗️</b>
━━━━━━━━━━━━━━━━━━━━━━━
{pe('card')} Auto Like : {package} Likes
{pe('bolt')} Speed: {speed}s

{pe('user')} Account: {nickname}
{pe('id')} UID: {uid}
{pe('globe')} Region: {region.upper()}

{pe('chart_up')} Before: {before}
{pe('heart')} Likes Added: {added}
{pe('chart_down')} After: {after}

{pe('graduate')} TASK NO : {serial}</blockquote>"""

def error_ui(title, message):
    return f"╭━〔 {pe('warning')} **{title}** 〕━⬣\n┃ {pe('cross')} {message}\n╰━━━━━━━━━━━━━━━━━━⬣"

def info_ui(title, message):
    return f"╭━〔 {pe('info')} **{title}** 〕━⬣\n┃ {pe('diamond2')} {message}\n╰━━━━━━━━━━━━━━━━━━⬣"

# ==========================================
# 🤖 BOT ADDED TO GROUP - TRACK ALL GROUPS
# ==========================================
@bot.message_handler(content_types=['new_chat_members'])
def on_bot_added(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            chat_id = str(message.chat.id)
            chat_title = message.chat.title or "Unknown Group"
            
            all_groups = load_all_groups()
            all_groups[chat_id] = {
                "title": chat_title,
                "added_date": time.time(),
                "status": get_group_status(message.chat.id)
            }
            save_all_groups(all_groups)
            
            groups = load_groups()
            groups[chat_id] = "unlimited"
            save_groups(groups)
            
            print(f"{pe('bot')} Bot added to group: {chat_title} ({chat_id})")

@bot.message_handler(content_types=['left_chat_member'])
def on_bot_removed(message):
    if message.left_chat_member.id == bot.get_me().id:
        chat_id = str(message.chat.id)
        
        all_groups = load_all_groups()
        if chat_id in all_groups:
            del all_groups[chat_id]
            save_all_groups(all_groups)
        
        groups = load_groups()
        if chat_id in groups:
            del groups[chat_id]
            save_groups(groups)
        
        print(f"{pe('bot')} Bot removed from group: {chat_id}")

# ==========================================
# 🤖 ADMIN MANAGEMENT COMMAND
# ==========================================
@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, f"{pe('cross')} You are not authorized to use this command!", parse_mode="Markdown")
        return
    
    args = message.text.split()
    
    if len(args) == 3 and args[1].lower() == 'add':
        try:
            new_admin_id = int(args[2])
            if new_admin_id in ADMIN_IDS:
                bot.reply_to(message, f"{pe('cross')} User `{new_admin_id}` is already an admin!", parse_mode="Markdown")
                return
            
            ADMIN_IDS.append(new_admin_id)
            save_admin_ids(ADMIN_IDS)
            bot.reply_to(message, f"{pe('check')} **New Admin Added!**\n{pe('crown')} User ID: `{new_admin_id}`\n{pe('pin')} This user now has full control over the bot.", parse_mode="Markdown")
            
            try:
                bot.send_message(new_admin_id, f"{pe('star')} **Congratulations!** You have been granted Admin access to the bot.\nYou now have full control over all bot functions.", parse_mode="Markdown")
            except:
                pass
                
        except ValueError:
            bot.reply_to(message, f"{pe('cross')} Invalid User ID! Please provide a valid numeric ID.", parse_mode="Markdown")
    
    elif len(args) == 3 and args[1].lower() == 'remove':
        try:
            remove_admin_id = int(args[2])
            if remove_admin_id not in ADMIN_IDS:
                bot.reply_to(message, f"{pe('cross')} User `{remove_admin_id}` is not an admin!", parse_mode="Markdown")
                return
            
            if remove_admin_id == 7603719412:
                bot.reply_to(message, f"{pe('cross')} Cannot remove the master admin (7603719412)!", parse_mode="Markdown")
                return
            
            ADMIN_IDS.remove(remove_admin_id)
            save_admin_ids(ADMIN_IDS)
            bot.reply_to(message, f"{pe('check')} **Admin Removed!**\n{pe('crown')} User ID: `{remove_admin_id}`\n{pe('pin')} This user no longer has admin access.", parse_mode="Markdown")
            
            try:
                bot.send_message(remove_admin_id, f"{pe('warning')} **Admin Access Revoked!**\nYou are no longer an admin of this bot.", parse_mode="Markdown")
            except:
                pass
                
        except ValueError:
            bot.reply_to(message, f"{pe('cross')} Invalid User ID! Please provide a valid numeric ID.", parse_mode="Markdown")
    
    elif len(args) == 2 and args[1].lower() == 'list':
        admin_list = ""
        for idx, admin_id in enumerate(ADMIN_IDS, 1):
            master_tag = f" {pe('crown')} MASTER" if admin_id == 7603719412 else ""
            try:
                user_info = bot.get_chat(admin_id)
                name = user_info.first_name or user_info.username or str(admin_id)
                admin_list += f"{idx}. `{admin_id}` - {name}{master_tag}\n"
            except:
                admin_list += f"{idx}. `{admin_id}`{master_tag}\n"
        
        text = f"""╭━〔 {pe('crown')} **ADMIN LIST** 〕━⬣
├─ {pe('chart')} Total Admins: `{len(ADMIN_IDS)}`
{admin_list}
╰━━━━━━━━━━━━━━━━━━⬣"""
        bot.reply_to(message, text, parse_mode="Markdown")
    
    else:
        bot.reply_to(message, f"""{pe('warning')} **Admin Command Usage:**

`/admin add <user_id>` - Add new admin
`/admin remove <user_id>` - Remove admin
`/admin list` - List all admins

{pe('pin')} **Note:** Only existing admins can use these commands.
{pe('crown')} Master Admin (7603719412) cannot be removed.""", parse_mode="Markdown")

# ==========================================
# 🔧 USER LIMIT COMMAND
# ==========================================
@bot.message_handler(commands=['limit'])
def handle_limit_command(message):
    if not admin_full_control(message.from_user.id):
        bot.reply_to(message, f"{pe('cross')} You are not authorized to use this command!", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, f"{pe('warning')} **Usage:** `/limit <number>`\nExample: `/limit 5`\n\n{pe('pin')} This sets the daily limit for normal users.", parse_mode="Markdown")
        return
    
    try:
        new_limit = int(args[1])
        if new_limit < 1:
            bot.reply_to(message, f"{pe('cross')} Limit must be at least 1!", parse_mode="Markdown")
            return
        
        global USER_LIMIT
        USER_LIMIT = new_limit
        bot.reply_to(message, f"{pe('check')} **User Daily Limit Updated!**\n{pe('chart')} New limit: `{USER_LIMIT}` requests per day for normal users.", parse_mode="Markdown")
        
    except ValueError:
        bot.reply_to(message, f"{pe('cross')} Please provide a valid number!", parse_mode="Markdown")

# ==========================================
# 📊 GROUP LIST COMMAND
# ==========================================
@bot.message_handler(commands=['glist'])
def handle_glist_command(message):
    if not admin_full_control(message.from_user.id):
        bot.reply_to(message, f"{pe('cross')} You are not authorized to use this command!", parse_mode="Markdown")
        return
    
    all_groups = load_all_groups()
    
    if not all_groups:
        bot.reply_to(message, f"{pe('empty')} **No groups found!**\nBot hasn't been added to any groups yet.", parse_mode="Markdown")
        return
    
    text = f"╭━〔 {pe('chart')} **ALL GROUPS LIST** 〕━⬣\n┃\n"
    text += f"┃ {pe('pin')} **Total Groups:** `{len(all_groups)}`\n┃\n"
    
    on_count = 0
    off_count = 0
    
    for idx, (chat_id, data) in enumerate(all_groups.items(), 1):
        title = data.get('title', 'Unknown')
        is_on = get_group_status(int(chat_id))
        status_emoji = f"{pe('green_circle')} ON" if is_on else f"{pe('red_circle')} OFF"
        
        if is_on:
            on_count += 1
        else:
            off_count += 1
        
        text += f"┃ {idx}. **{title}**\n"
        text += f"┃    ├─ ID: `{chat_id}`\n"
        text += f"┃    └─ Status: {status_emoji}\n"
        
        if idx < len(all_groups):
            text += "┃\n"
    
    text += f"┃\n┃ {pe('chart')} **Summary:**\n"
    text += f"┃ ├─ {pe('green_circle')} ON: `{on_count}`\n"
    text += f"┃ └─ {pe('red_circle')} OFF: `{off_count}`\n"
    text += "╰━━━━━━━━━━━━━━━━━━⬣"
    
    bot.reply_to(message, text, parse_mode="Markdown")

# ==========================================
# 🤖 BOT ON/OFF COMMANDS
# ==========================================
@bot.message_handler(commands=['p0', 'p02', 'remainreset'])
def handle_admin_commands(message):
    global bot_is_on, user_usage
    if not admin_full_control(message.from_user.id): 
        return
    
    command = message.text.split()[0].lower()
    chat_id = message.chat.id
    
    if command == '/p0':
        if chat_id < 0:
            set_group_status(chat_id, True)
            all_groups = load_all_groups()
            chat_id_str = str(chat_id)
            if chat_id_str in all_groups:
                all_groups[chat_id_str]['status'] = True
                save_all_groups(all_groups)
            bot.reply_to(message, info_ui("GROUP BOT ON", "Bot has been turned **ON** for this group only. Other groups are unaffected."), parse_mode="Markdown")
        else:
            bot_is_on = True
            bot.reply_to(message, info_ui("SYSTEM ALIVE", "Bot has been turned **ON** globally."), parse_mode="Markdown")
    
    elif command == '/p02':
        if chat_id < 0:
            set_group_status(chat_id, False)
            all_groups = load_all_groups()
            chat_id_str = str(chat_id)
            if chat_id_str in all_groups:
                all_groups[chat_id_str]['status'] = False
                save_all_groups(all_groups)
            bot.reply_to(message, info_ui("GROUP BOT OFF", "Bot has been turned **OFF** for this group only. Other groups are unaffected."), parse_mode="Markdown")
        else:
            bot_is_on = False
            bot.reply_to(message, info_ui("SYSTEM SLEEP", "Bot has been turned **OFF** globally."), parse_mode="Markdown")
    
    elif command == '/remainreset':
        user_usage.clear()
        bot.reply_to(message, info_ui("USER LIMITS RESET", "All user daily limits have been reset."), parse_mode="Markdown")

# ==========================================
# 🎯 50 LIKES COMMAND - WITH FORCE JOIN
# ==========================================
@bot.message_handler(commands=['like'])
def handle_like(message):
    global user_usage

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chat_id = message.chat.id
    vips = load_vip()
    is_vip = str(user_id) in vips

    # FORCE JOIN CHECK (Admins skip)
    if not is_admin(user_id):
        not_joined = check_force_join(user_id)
        if not_joined:
            channels_text = "\n".join([f"{pe('cross')} {ch['name']}" for ch in not_joined])
            bot.reply_to(
                message,
                f"""<b>{pe('warning')} ACCESS DENIED!</b>

<b>{pe('user')} Hello {user_name}!</b>

You must join our channels first to use this bot.

<b>{pe('speaker')} Required Channels:</b>
├─ Riyad Auto Like Group
├─ Riyad Al Hasan Backup Channel

<b>{pe('cross')} You haven't joined:</b>
{channels_text}

<i>Please join all channels and try again.</i>""",
                parse_mode="HTML",
                reply_markup=force_join_keyboard(not_joined)
            )
            return

    # Check if bot is ON
    if not is_admin(user_id):
        if not is_bot_on_for_chat(chat_id): 
            bot.reply_to(message, error_ui("BOT OFFLINE", "Bot is currently turned OFF for this group."), parse_mode="Markdown")
            return

    if not is_admin(user_id):
        if is_vip:
            vip_limit = vips[str(user_id)]['limit']
            if user_usage.get(user_id, 0) >= vip_limit:
                bot.reply_to(message, error_ui("LIMIT REACHED", f"Sorry {user_name}, you have used your VIP daily limit."), parse_mode="Markdown")
                return
        else:
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

    process_like_request(message, region, uid, user_id, user_name, likes_count=50)

def process_like_request(message, region, uid, user_id, user_name, likes_count=50):
    global user_usage
    
    base_api = API_50_URL
    api_key = API_50_KEY
    api_endpoint = f"{base_api}/like"
    
    wait_msg = bot.reply_to(message, f"{pe('rocket')} Processing likes Sending.....{pe('rocket')}")

    try:
        start_time = time.time() 
        url = f"{api_endpoint}?api_key={api_key}&server_name={region.lower()}&uid={uid}"
        
        response = requests.get(url, timeout=45) 
        data = response.json()
        
        response_time = round(time.time() - start_time, 2)
        status = data.get('status')

        if status in [1, 2]:
            vips = load_vip()
            if not is_admin(user_id):
                user_usage[user_id] = user_usage.get(user_id, 0) + 1
            
            remain_requests = "♾️" if is_admin(user_id) else (vips[str(user_id)]['limit'] - user_usage.get(user_id, 0) if str(user_id) in vips else USER_LIMIT - user_usage.get(user_id, 0))
            final_text = report_ui(data, region, status, response_time, remain_requests, likes_count)
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=final_text, parse_mode="HTML")

        elif status == 0:
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("FAILED", "Could not process UID. It may be invalid or maxed."), parse_mode="Markdown")
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("ERROR", "Service is temporarily unavailable."), parse_mode="Markdown")

    except requests.exceptions.Timeout:
        print(f"Timeout error for UID: {uid}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("TIMEOUT", "Server is taking too long. Please try again later."), parse_mode="Markdown")
    except requests.exceptions.ConnectionError:
        print(f"Connection error for UID: {uid}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("CONNECTION ERROR", "Cannot connect to server. Please check your internet."), parse_mode="Markdown")
    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("ERROR", f"An error occurred: {str(e)[:50]}"), parse_mode="Markdown")

# ==========================================
# 🚀 AUTO-TASK COMMANDS
# ==========================================
@bot.message_handler(commands=['autotime'])
def handle_autotime(message):
    if not admin_full_control(message.from_user.id): 
        return
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        bot.reply_to(message, f"{pe('warning')} **Usage:** `/autotime HH:MM AM/PM`\nExample: `/autotime 04:30 AM`", parse_mode="Markdown")
        return
    
    time_str = args[1].upper()
    db = load_auto_db()
    db['time'] = time_str
    save_auto_db(db)
    bot.reply_to(message, f"{pe('check')} Auto-task time set to **{time_str}** (BD TimeZone).", parse_mode="Markdown")

@bot.message_handler(commands=['likeauto'])
def handle_likeauto(message):
    if not admin_full_control(message.from_user.id): 
        return
    args = message.text.split()
    if len(args) != 5:
        bot.reply_to(message, f"{pe('warning')} **Usage:** `/likeauto {{region}} {{uid}} {{20/50}} {{days}}`\nExample: `/likeauto BD 123456 20 7` or `/likeauto BD 123456 50 5`", parse_mode="Markdown")
        return

    region, uid, package_str, days_str = args[1].upper(), args[2], args[3], args[4]
    
    if region not in ALLOWED_REGIONS:
        bot.reply_to(message, error_ui("INVALID REGION", f"Allowed: `{', '.join(ALLOWED_REGIONS)}`"), parse_mode="Markdown")
        return
    
    if package_str not in ['20', '50']:
        bot.reply_to(message, error_ui("INVALID PACKAGE", "Package must be 20 or 50."), parse_mode="Markdown")
        return

    try:
        package, days = int(package_str), int(days_str)
        total_likes = package * days
    except ValueError:
        bot.reply_to(message, f"{pe('cross')} Package and Days must be numbers.", parse_mode="Markdown")
        return

    db = load_auto_db()
    serial_num = str(db['next_serial']).zfill(4) 
    db['next_serial'] += 1
    
    if package == 20:
        db['stats']['total_20_tasks'] = db['stats'].get('total_20_tasks', 0) + 1
    else:
        db['stats']['total_50_tasks'] = db['stats'].get('total_50_tasks', 0) + 1

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
    
    bot.reply_to(message, f"""{pe('check')} **Auto Task Added Successfully!**
━━━━━━━━━━━━━━━━━━━━━━━
{pe('graduate')} Task No: `{serial_num}`
{pe('id')} UID: `{uid}`
{pe('globe')} Region: `{region}`
{pe('card')} Package: `{package}` Likes/Day
{pe('calendar')} Duration: `{days}` Days
{pe('target')} Total Likes: `{total_likes}`

{pe('chart')} Package Statistics:
├─ 20 Likes Tasks: `{db['stats'].get('total_20_tasks', 0)}`
├─ 50 Likes Tasks: `{db['stats'].get('total_50_tasks', 0)}`
├─ Total 20 Likes Sent: `{db['stats'].get('total_20_likes_sent', 0)}`
└─ Total 50 Likes Sent: `{db['stats'].get('total_50_likes_sent', 0)}`""", parse_mode="Markdown")

@bot.message_handler(commands=['autoremove'])
def handle_autoremove(message):
    if not admin_full_control(message.from_user.id): 
        return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, f"{pe('warning')} **Usage:** `/autoremove {{uid}}`\nExample: `/autoremove 1234567890`\nOr use: `/autoremove task_{{serial}}`", parse_mode="Markdown")
        return
    
    remove_param = args[1]
    db = load_auto_db()
    tasks = db.get('tasks', {})
    
    found = False
    removed_tasks = []
    
    if remove_param.startswith('task_'):
        serial = remove_param.replace('task_', '')
        if serial in tasks:
            task = tasks[serial]
            removed_tasks.append((serial, task))
            del db['tasks'][serial]
            found = True
            if task['package'] == 20:
                db['stats']['total_20_tasks'] = max(0, db['stats'].get('total_20_tasks', 0) - 1)
            else:
                db['stats']['total_50_tasks'] = max(0, db['stats'].get('total_50_tasks', 0) - 1)
    else:
        for serial, task in list(tasks.items()):
            if task['uid'] == remove_param:
                removed_tasks.append((serial, task))
                del db['tasks'][serial]
                found = True
                if task['package'] == 20:
                    db['stats']['total_20_tasks'] = max(0, db['stats'].get('total_20_tasks', 0) - 1)
                else:
                    db['stats']['total_50_tasks'] = max(0, db['stats'].get('total_50_tasks', 0) - 1)
    
    if found:
        save_auto_db(db)
        msg = f"{pe('check')} **Removed {len(removed_tasks)} task(s)**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
        for serial, task in removed_tasks:
            msg += f"""{pe('graduate')} Task No: `{serial}`
├─ {pe('id')} UID: `{task['uid']}`
├─ {pe('card')} Package: `{task['package']}` Likes
├─ {pe('chart')} Sent: `{task['sent']}/{task['total_target']}`
└─ Status: Removed\n\n"""
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, f"{pe('cross')} No auto task found with identifier: `{remove_param}`", parse_mode="Markdown")

@bot.message_handler(commands=['listauto'])
def handle_listauto(message):
    if not admin_full_control(message.from_user.id): 
        return
    db = load_auto_db()
    tasks = db.get('tasks', {})
    stats = db.get('stats', {"total_20_tasks": 0, "total_50_tasks": 0, "total_20_likes_sent": 0, "total_50_likes_sent": 0})
    
    count_20 = sum(1 for t in tasks.values() if t['package'] == 20)
    count_50 = sum(1 for t in tasks.values() if t['package'] == 50)
    total_likes_sent_20 = sum(t.get('sent', 0) for t in tasks.values() if t['package'] == 20)
    total_likes_sent_50 = sum(t.get('sent', 0) for t in tasks.values() if t['package'] == 50)
    
    header = f"""<blockquote><b>{pe('chart')} AUTO-LIKE DATABASE {pe('chart')}</b></blockquote>
<blockquote><b>{pe('chart_up')} SYSTEM OVERVIEW:</b>
├─ {pe('users')} TOTAL ACTIVE TASKS : {len(tasks)}
├─ {pe('blue_heart')} 20 LIKES TASKS : {count_20}
├─ {pe('heart_fire')} 50 LIKES TASKS : {count_50}
├─ {pe('chart')} Total 20 Likes Sent: {total_likes_sent_20}
├─ {pe('chart')} Total 50 Likes Sent: {total_likes_sent_50}
└─ {pe('clock')} NEXT RUN TIME : {db.get('time', 'Not Set')} (BD)</blockquote>\n"""

    msg_body = header
    if tasks:
        tasks_20 = [(s, t) for s, t in tasks.items() if t['package'] == 20]
        tasks_50 = [(s, t) for s, t in tasks.items() if t['package'] == 50]
        
        if tasks_20:
            msg_body += f"\n<blockquote><b>{pe('blue_heart')} 20 LIKES TASKS</b></blockquote>\n"
            for serial, data in tasks_20:
                nickname = data.get('nickname', 'Unknown')
                progress = int((data['sent'] / data['total_target']) * 100) if data['total_target'] > 0 else 0
                task_block = f"""<blockquote>{pe('graduate')} <b>TASK {serial}</b>
├─ {pe('user')} {nickname}
├─ {pe('id')} <code>{data['uid']}</code> | {data['region']}
├─ {pe('card')} {data['package']} LIKES/DAY
├─ {pe('chart')} SENT: {data['sent']} | REMAIN: {data['remain']}
├─ {pe('chart_up')} PROGRESS: {progress}%
└─ {pe('hourglass')} DAYS LEFT: {data['days'] - data['days_completed']}</blockquote>\n"""
                if len(msg_body) + len(task_block) > 3500:
                    bot.reply_to(message, msg_body, parse_mode="HTML")
                    msg_body = header + f"\n<blockquote><b>{pe('blue_heart')} 20 LIKES TASKS (Continued)</b></blockquote>\n"
                msg_body += task_block
        
        if tasks_50:
            if tasks_20:
                msg_body += f"\n<blockquote><b>{pe('heart_fire')} 50 LIKES TASKS</b></blockquote>\n"
            else:
                msg_body += f"\n<blockquote><b>{pe('heart_fire')} 50 LIKES TASKS</b></blockquote>\n"
            
            for serial, data in tasks_50:
                nickname = data.get('nickname', 'Unknown')
                progress = int((data['sent'] / data['total_target']) * 100) if data['total_target'] > 0 else 0
                task_block = f"""<blockquote>{pe('graduate')} <b>TASK {serial}</b>
├─ {pe('user')} {nickname}
├─ {pe('id')} <code>{data['uid']}</code> | {data['region']}
├─ {pe('card')} {data['package']} LIKES/DAY
├─ {pe('chart')} SENT: {data['sent']} | REMAIN: {data['remain']}
├─ {pe('chart_up')} PROGRESS: {progress}%
└─ {pe('hourglass')} DAYS LEFT: {data['days'] - data['days_completed']}</blockquote>\n"""
                if len(msg_body) + len(task_block) > 3500:
                    bot.reply_to(message, msg_body, parse_mode="HTML")
                    msg_body = header + f"\n<blockquote><b>{pe('heart_fire')} 50 LIKES TASKS (Continued)</b></blockquote>\n"
                msg_body += task_block
    else:
        msg_body += "<i>✨ No active auto tasks currently. Use /likeauto to add tasks!</i>"

    if msg_body:
        bot.reply_to(message, msg_body, parse_mode="HTML")

@bot.message_handler(commands=['autostats'])
def handle_autostats(message):
    if not admin_full_control(message.from_user.id): 
        return
    db = load_auto_db()
    stats = db.get('stats', {})
    tasks = db.get('tasks', {})
    
    total_20_sent = stats.get('total_20_likes_sent', 0)
    total_50_sent = stats.get('total_50_likes_sent', 0)
    
    text = f"""╭━〔 {pe('chart')} **AUTO-LIKE STATISTICS** 〕━⬣
┃
├─ {pe('chart_up')} **TASK OVERVIEW**
├─ {pe('users')} Active Tasks: `{len(tasks)}`
├─ {pe('blue_heart')} 20-Likes Tasks: `{stats.get('total_20_tasks', 0)}`
├─ {pe('heart_fire')} 50-Likes Tasks: `{stats.get('total_50_tasks', 0)}`
┃
├─ {pe('chart')} **LIKES SENT (ALL TIME)**
├─ {pe('blue_heart')} Total 20-Likes Sent: `{total_20_sent}`
├─ {pe('heart_fire')} Total 50-Likes Sent: `{total_50_sent}`
├─ {pe('target')} Total Combined: `{total_20_sent + total_50_sent}`
┃
├─ {pe('clock')} **SCHEDULE**
├─ {pe('clock')} Next Run Time: `{db.get('time', 'Not Set')}`
├─ {pe('calendar')} Last Run Date: `{db.get('last_run', 'Never')}`
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
    chat_id = message.chat.id
    
    if cmd == '/remains':
        if not is_bot_on_for_chat(chat_id): 
            bot.reply_to(message, error_ui("BOT OFFLINE", "Bot is currently turned OFF for this group."), parse_mode="Markdown")
            return
        
        # FORCE JOIN CHECK for /remains (non-admins)
        if not is_admin(user_id):
            not_joined = check_force_join(user_id)
            if not_joined:
                channels_text = "\n".join([f"{pe('cross')} {ch['name']}" for ch in not_joined])
                bot.reply_to(
                    message,
                    f"""<b>{pe('warning')} ACCESS DENIED!</b>

<b>{pe('cross')} You haven't joined:</b>
{channels_text}

<i>Please join all channels and try again.</i>""",
                    parse_mode="HTML",
                    reply_markup=force_join_keyboard(not_joined)
                )
                return
        
        vips = load_vip()
        if is_admin(user_id): 
            uses_left = f"♾️ Unlimited (Admin)"
        elif str(user_id) in vips: 
            uses_left = f"{vips[str(user_id)]['limit'] - user_usage.get(user_id, 0)}/{vips[str(user_id)]['limit']} (VIP)"
        else: 
            uses_left = f"{USER_LIMIT - user_usage.get(user_id, 0)}/{USER_LIMIT}"
        text = f"╭━〔 {pe('globe')} **YOUR LIMIT** 〕━⬣\n┃ {pe('user')} **Your Limit:** `{uses_left}`\n╰━━━━━━━━━━━━━━━━━━⬣"
        return bot.reply_to(message, text, parse_mode="Markdown")

    if not admin_full_control(user_id): 
        return
    args = message.text.split()

    if cmd == '/vipadd' and len(args) == 3:
        vips = load_vip()
        vips[args[1]] = {"name": f"User ID: {args[1]}", "limit": int(args[2])}
        save_vip(vips)
        bot.reply_to(message, f"{pe('check')} VIP Added: {args[1]} (Limit: {args[2]})")
    elif cmd == '/removevip' and len(args) == 2:
        vips = load_vip()
        if args[1] in vips: 
            del vips[args[1]]
            save_vip(vips)
            bot.reply_to(message, f"{pe('ban')} VIP Removed.")
    elif cmd == '/listvip':
        vips = load_vip()
        if not vips:
            bot.reply_to(message, f"{pe('empty')} **No VIPs found.**", parse_mode="Markdown")
            return
        text = f"╭━〔 {pe('star')} **VIP LIST** 〕━⬣\n"
        for uid, data in vips.items(): 
            text += f"┃ {pe('user')} ID: `{uid}` - Limit: `{data['limit']}`\n"
        text += "╰━━━━━━━━━━━━━━━━━━⬣"
        bot.reply_to(message, text, parse_mode="Markdown")
    elif cmd == '/allow':
        groups = load_groups()
        chat_id_str = str(message.chat.id)
        if len(args) == 2:
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
                    return bot.reply_to(message, f"{pe('cross')} Invalid format.", parse_mode="Markdown")
        else:
            groups[chat_id_str] = "unlimited"
        save_groups(groups)
        bot.reply_to(message, f"{pe('check')} This group has been allowed!", parse_mode="Markdown")
    elif cmd == '/disallow':
        groups = load_groups()
        chat_id_str = str(message.chat.id)
        if chat_id_str in groups: 
            del groups[chat_id_str]
            save_groups(groups)
            bot.reply_to(message, f"{pe('ban')} This group has been disallowed.", parse_mode="Markdown")

# ==========================================
# ⏰ BACKGROUND CRON JOB
# ==========================================
def execute_auto_tasks():
    db = load_auto_db()
    tasks = db.get("tasks", {})
    if not tasks: 
        print(f"{pe('empty')} No auto tasks to execute")
        return

    print(f"{pe('rocket')} Executing {len(tasks)} auto tasks...")
    
    for serial, task in list(tasks.items()):
        if task.get('status') == 'paused':
            continue
            
        uid = task['uid']
        region = task['region']
        package = task['package']
        chat_id = task['chat_id']
        
        if package == 20:
            base_api = API_20_URL
            api_key = API_20_KEY
            url = f"{base_api}/like?uid={uid}&server_name={region.lower()}&key={api_key}"
        else:
            base_api = API_50_URL
            api_key = API_50_KEY
            url = f"{base_api}/like?api_key={api_key}&server_name={region.lower()}&uid={uid}"
        
        start_time = time.time()
        try:
            response = requests.get(url, timeout=45)
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
                
                if package == 20:
                    db['stats']['total_20_likes_sent'] = db['stats'].get('total_20_likes_sent', 0) + added
                else:
                    db['stats']['total_50_likes_sent'] = db['stats'].get('total_50_likes_sent', 0) + added
                
                msg_text = auto_report_ui(True, package, response_time, nickname, uid, region, before, added, after, serial)
                
                try:
                    bot.send_message(chat_id, msg_text, parse_mode="HTML")
                except:
                    pass
                
                all_groups = load_all_groups()
                for group_id in all_groups:
                    if str(group_id) != str(chat_id) and is_bot_on_for_chat(int(group_id)):
                        try:
                            bot.send_message(int(group_id), msg_text, parse_mode="HTML")
                        except:
                            pass
                
                print(f"{pe('check')} Task {serial} SUCCESS: Sent {added} likes")
            else:
                msg_text = auto_report_ui(False, package, response_time, nickname, uid, region, before, 0, after, serial, "ALREADY MAX")
                
                try:
                    bot.send_message(chat_id, msg_text, parse_mode="HTML")
                except:
                    pass
                
                all_groups = load_all_groups()
                for group_id in all_groups:
                    if str(group_id) != str(chat_id) and is_bot_on_for_chat(int(group_id)):
                        try:
                            bot.send_message(int(group_id), msg_text, parse_mode="HTML")
                        except:
                            pass
                
        except Exception as e:
            print(f"{pe('cross')} Task {serial} Error: {e}")

        save_auto_db(db)
        
        if task.get('remain', 0) <= 0:
            db = load_auto_db()
            if serial in db.get('tasks', {}):
                del db['tasks'][serial]
                save_auto_db(db)
        
        time.sleep(10)

def cron_worker():
    print(f"{pe('clock')} Auto-Task Cron Started...")
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
                print(f"{pe('rocket')} Executing Auto Tasks for {current_date_str}")
                db['last_run'] = current_date_str
                save_auto_db(db) 
                execute_auto_tasks()
                
        except Exception as e:
            print(f"Cron Worker Error: {e}")
            
        time.sleep(30)

if __name__ == "__main__":
    print(f"{pe('rocket')} Premium Bot with Animated Emoji starting...")
    print(f"{pe('pin')} Master Admin: 7603719412")
    print(f"{pe('crown')} Total Admins: {len(ADMIN_IDS)}")
    print(f"{pe('chart')} User Daily Limit: {USER_LIMIT}")
    print(f"{pe('speaker')} Force Join: ENABLED (2 Channels)")
    print(f"{pe('bolt')} Premium Emoji: ENABLED")
    
    cron_thread = threading.Thread(target=cron_worker, daemon=True)
    cron_thread.start()
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Bot crashed, restarting... Error: {e}")
            time.sleep(5)
