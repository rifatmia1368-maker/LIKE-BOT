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
# ⚙️ CONFIGURATION
# ==========================================
TOKEN = '8926868360:AAGb9kvjfxrdbritVWvYTC7m751lKU6Hg0c'

# APIs
API_20_URL = 'https://riyad-like-api-ob-52.vercel.app'
API_20_KEY = 'RIYADAH' 
API_30_URL = 'http://2.56.246.128:30264'
API_30_KEY = '1SAIFUL1'

# Admin Settings
ADMIN_IDS_FILE = 'admin_ids.json'
DEFAULT_ADMINS = [7603719412]

# ==========================================
# 📁 FILE PATH FOR RAILWAY
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'bot_data')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"📁 Created data directory: {DATA_DIR}")

# ফাইলের পাথ
REMAIN_FILE = os.path.join(DATA_DIR, 'remain_syreo.json')
GROUPS_FILE = os.path.join(DATA_DIR, 'group_ids.json')
VIP_FILE = os.path.join(DATA_DIR, 'vip.json')
AUTO_DB_FILE = os.path.join(DATA_DIR, 'auto_likes.json')
ADMIN_IDS_FILE_PATH = os.path.join(DATA_DIR, 'admin_ids.json')

# ==========================================
# 📂 DATA RECOVERY FUNCTION
# ==========================================
def recover_old_data():
    """পুরানো ডাটা রিকভার করার ফাংশন"""
    print("\n🔍 Checking for old data files...")
    
    # চেক করুন আগের লোকেশনে ফাইল আছে কিনা
    old_locations = [
        'auto_likes.json',  # রুট ডিরেক্টরি
        './auto_likes.json',
        '../auto_likes.json',
        '/app/auto_likes.json'  # Railway পুরানো পাথ
    ]
    
    recovered_tasks = {}
    found_any = False
    
    for old_path in old_locations:
        if os.path.exists(old_path):
            print(f"📄 Found old file at: {old_path}")
            try:
                with open(old_path, 'r') as f:
                    old_data = json.load(f)
                    
                # চেক করুন এতে টাস্ক আছে কিনা
                if 'tasks' in old_data and old_data['tasks']:
                    recovered_tasks.update(old_data['tasks'])
                    found_any = True
                    print(f"✅ Recovered {len(old_data['tasks'])} tasks from {old_path}")
                    
                elif isinstance(old_data, dict):
                    # যদি সরাসরি টাস্ক থাকে
                    for key, value in old_data.items():
                        if isinstance(value, dict) and 'uid' in value and 'package' in value:
                            recovered_tasks[key] = value
                            found_any = True
                    if found_any:
                        print(f"✅ Recovered {len(recovered_tasks)} tasks from {old_path}")
                
                # ব্যাকআপ তৈরি করুন
                backup_path = f"{old_path}.backup"
                with open(backup_path, 'w') as f:
                    json.dump(old_data, f, indent=4)
                print(f"📦 Backup created: {backup_path}")
                
            except Exception as e:
                print(f"❌ Error reading {old_path}: {e}")
    
    return recovered_tasks, found_any

def fix_and_load_database():
    """ডাটাবেস ফিক্স এবং লোড করা"""
    print("\n" + "="*50)
    print("🔧 FIXING DATABASE...")
    print("="*50)
    
    # পুরানো ডাটা রিকভার করুন
    recovered_tasks, found_old = recover_old_data()
    
    # বর্তমান ডাটাবেস লোড করুন
    current_db = {}
    if os.path.exists(AUTO_DB_FILE):
        try:
            with open(AUTO_DB_FILE, 'r') as f:
                current_db = json.load(f)
            print(f"\n📖 Current DB has {len(current_db.get('tasks', {}))} tasks")
        except:
            current_db = {}
    
    # ম্যানুয়ালি টাস্ক যোগ করার অপশন
    if not recovered_tasks and not current_db.get('tasks'):
        print("\n⚠️ No automatic recovery found!")
        print("Please add tasks manually using: /likeauto BD UID 20 7")
        
        # একটি ডেমো টাস্ক দেখানো
        print("\n📝 Example command:")
        print("   /likeauto BD 1234567890 20 7")
        
    else:
        # রিকভার করা টাস্ক মার্জ করুন
        if recovered_tasks:
            if 'tasks' not in current_db:
                current_db['tasks'] = {}
            current_db['tasks'].update(recovered_tasks)
            
            # স্ট্যাটাস আপডেট করুন
            if 'stats' not in current_db:
                current_db['stats'] = {"total_20_tasks": 0, "total_30_tasks": 0, "total_likes_sent_20": 0, "total_likes_sent_30": 0}
            
            # কাউন্ট আপডেট
            count_20 = sum(1 for t in current_db['tasks'].values() if t.get('package') == 20)
            count_30 = sum(1 for t in current_db['tasks'].values() if t.get('package') == 30)
            current_db['stats']['total_20_tasks'] = count_20
            current_db['stats']['total_30_tasks'] = count_30
            
            if 'next_serial' not in current_db:
                current_db['next_serial'] = len(current_db['tasks']) + 1
            if 'time' not in current_db:
                current_db['time'] = "08:57 AM"
            if 'last_run' not in current_db:
                current_db['last_run'] = ""
            
            # সেভ করুন
            with open(AUTO_DB_FILE, 'w') as f:
                json.dump(current_db, f, indent=4)
            
            print(f"\n✅ SUCCESS! Recovered {len(recovered_tasks)} tasks")
            print(f"   Total tasks now: {len(current_db['tasks'])}")
            print(f"   💙 20 Likes tasks: {count_20}")
            print(f"   ❤️ 30 Likes tasks: {count_30}")
            
            # টাস্কগুলো দেখান
            print("\n📋 Recovered Tasks:")
            for serial, task in recovered_tasks.items():
                print(f"   🎓 {serial}: {task.get('uid')} - {task.get('package')} likes")
            
            return current_db
    
    return current_db

# ==========================================
# LOAD FUNCTIONS WITH FIX
# ==========================================
def load_admin_ids():
    if os.path.exists(ADMIN_IDS_FILE_PATH):
        try:
            with open(ADMIN_IDS_FILE_PATH, 'r') as f:
                data = json.load(f)
                return data.get('admin_ids', DEFAULT_ADMINS.copy())
        except Exception as e:
            print(f"Error loading admin IDs: {e}")
            return DEFAULT_ADMINS.copy()
    else:
        save_admin_ids(DEFAULT_ADMINS)
    return DEFAULT_ADMINS.copy()

def save_admin_ids(admin_ids):
    try:
        with open(ADMIN_IDS_FILE_PATH, 'w') as f:
            json.dump({'admin_ids': admin_ids}, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving admin IDs: {e}")
        return False

ADMIN_IDS = load_admin_ids()
bot = telebot.TeleBot(TOKEN)

ALLOWED_REGIONS = ['ME', 'ID', 'TH', 'VN', 'SG', 'BD', 'PK', 'MY', 'PH', 'RU', 'AFR']

# Global State
bot_is_on = True
USER_LIMIT = 1
user_usage = {}
pending_requests = {}

def is_admin(user_id):
    return user_id in ADMIN_IDS

def admin_full_control(user_id):
    return is_admin(user_id)

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return default
    return default

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

def load_vip(): 
    return load_json(VIP_FILE, {})

def save_vip(data): 
    return save_json(VIP_FILE, data)

def load_groups(): 
    return load_json(GROUPS_FILE, {})

def save_groups(data): 
    return save_json(GROUPS_FILE, data)

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
    
    data = load_json(AUTO_DB_FILE, default)
    
    # Fix data structure if needed
    if 'stats' not in data:
        data['stats'] = default['stats']
    if 'tasks' not in data:
        data['tasks'] = {}
    if 'next_serial' not in data:
        data['next_serial'] = 1
    if 'time' not in data:
        data['time'] = "08:57 AM"
    if 'last_run' not in data:
        data['last_run'] = ""
    
    # Recalculate stats based on actual tasks
    if data['tasks']:
        count_20 = sum(1 for t in data['tasks'].values() if t.get('package') == 20)
        count_30 = sum(1 for t in data['tasks'].values() if t.get('package') == 30)
        data['stats']['total_20_tasks'] = count_20
        data['stats']['total_30_tasks'] = count_30
    
    return data

def save_auto_db(data): 
    return save_json(AUTO_DB_FILE, data)

def load_remain():
    data = load_json(REMAIN_FILE, {})
    return data.get('bot_remain', 15)

def save_remain(remain_value):
    save_json(REMAIN_FILE, {'bot_remain': remain_value})

bot_remain = load_remain()

REQUIRED_CHATS = [
    {"id": -1003880872686, "url": "https://t.me/Syreo_212", "name": "SYREO CENTER"},
]

def get_missing_chats(user_id):
    if is_admin(user_id): return []
    missing = []
    for chat in REQUIRED_CHATS:
        try:
            member = bot.get_chat_member(chat['id'], user_id)
            if member.status in ['left', 'kicked']:
                missing.append(chat)
        except Exception:
            missing.append(chat)
    return missing

# ==========================================
# UI TEMPLATES
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

def error_ui(title, message):
    return f"╭━〔 ⚠️ **{title}** 〕━⬣\n┃ ❌ {message}\n╰━━━━━━━━━━━━━━━━━━⬣"

def info_ui(title, message):
    return f"╭━〔 ℹ️ **{title}** 〕━⬣\n┃ 💠 {message}\n╰━━━━━━━━━━━━━━━━━━⬣"

# ==========================================
# COMMANDS
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    help_text = """🤖 **Bot Commands:**

📌 **Like Commands:**
`/like {region} {uid}` - Send 20 likes
`/like30 {region} {uid}` - Send 30 likes

🔧 **Admin Commands:**
`/likeauto {region} {uid} {20/30} {days}` - Add auto task
`/listauto` - List all auto tasks
`/autoremove {serial}` - Remove auto task
`/checkdb` - Check database status
`/fixdb` - Fix and recover database
`/limit {number}` - Set user daily limit
`/remains` - Check your remaining limit

📊 **Info:**
`/admin list` - List all admins

Example: `/like BD 1234567890`"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['fixdb'])
def handle_fixdb(message):
    if not admin_full_control(message.from_user.id):
        bot.reply_to(message, "❌ Admin only!", parse_mode="Markdown")
        return
    
    bot.reply_to(message, "🔧 **Fixing database...**", parse_mode="Markdown")
    
    # Run database fix
    fixed_db = fix_and_load_database()
    tasks_count = len(fixed_db.get('tasks', {}))
    
    if tasks_count > 0:
        bot.reply_to(message, f"✅ **Database Fixed!**\n\nRecovered {tasks_count} tasks.\nUse `/listauto` to see them.", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ **No tasks found to recover.**\n\nPlease add tasks manually using:\n`/likeauto BD UID 20 7`", parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ You are not authorized!", parse_mode="Markdown")
        return
    
    args = message.text.split()
    
    if len(args) == 3 and args[1].lower() == 'add':
        try:
            new_admin_id = int(args[2])
            if new_admin_id in ADMIN_IDS:
                bot.reply_to(message, f"❌ User already admin!", parse_mode="Markdown")
                return
            
            ADMIN_IDS.append(new_admin_id)
            save_admin_ids(ADMIN_IDS)
            bot.reply_to(message, f"✅ Admin Added: `{new_admin_id}`", parse_mode="Markdown")
        except ValueError:
            bot.reply_to(message, "❌ Invalid User ID!", parse_mode="Markdown")
    
    elif len(args) == 3 and args[1].lower() == 'remove':
        try:
            remove_admin_id = int(args[2])
            if remove_admin_id == 7603719412:
                bot.reply_to(message, "❌ Cannot remove master admin!", parse_mode="Markdown")
                return
            
            if remove_admin_id in ADMIN_IDS:
                ADMIN_IDS.remove(remove_admin_id)
                save_admin_ids(ADMIN_IDS)
                bot.reply_to(message, f"✅ Admin Removed: `{remove_admin_id}`", parse_mode="Markdown")
        except ValueError:
            bot.reply_to(message, "❌ Invalid User ID!", parse_mode="Markdown")
    
    elif len(args) == 2 and args[1].lower() == 'list':
        admin_list = ""
        for idx, admin_id in enumerate(ADMIN_IDS, 1):
            master_tag = " 👑 MASTER" if admin_id == 7603719412 else ""
            admin_list += f"{idx}. `{admin_id}`{master_tag}\n"
        
        text = f"""╭━〔 👑 ADMIN LIST 〕━⬣
├─ Total Admins: {len(ADMIN_IDS)}
{admin_list}
╰━━━━━━━━━━━━━━━━━━⬣"""
        bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['limit'])
def handle_limit_command(message):
    if not admin_full_control(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "Usage: `/limit <number>`", parse_mode="Markdown")
        return
    
    try:
        new_limit = int(args[1])
        global USER_LIMIT
        USER_LIMIT = new_limit
        bot.reply_to(message, f"✅ User limit set to: {USER_LIMIT}", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Invalid number!", parse_mode="Markdown")

@bot.message_handler(commands=['p0', 'p02', 'remainreset'])
def handle_admin_commands(message):
    global bot_is_on, bot_remain, user_usage
    if not admin_full_control(message.from_user.id): return 
    command = message.text.split()[0].lower()
    
    if command == '/p0':
        bot_is_on = True
        bot.reply_to(message, "✅ Bot is ON", parse_mode="Markdown")
    elif command == '/p02':
        bot_is_on = False
        bot.reply_to(message, "❌ Bot is OFF", parse_mode="Markdown")
    elif command == '/remainreset':
        bot_remain = 15
        save_remain(bot_remain)
        user_usage.clear()
        bot.reply_to(message, "✅ Global limits reset", parse_mode="Markdown")

@bot.message_handler(commands=['like', 'like30'])
def handle_like(message):
    global bot_remain, user_usage

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    vips = load_vip()
    is_vip = str(user_id) in vips
    
    likes_count = 30 if message.text.startswith('/like30') else 20

    if not is_admin(user_id):
        if not bot_is_on:
            return

    if not is_admin(user_id):
        if is_vip:
            vip_limit = vips[str(user_id)]['limit']
            if user_usage.get(user_id, 0) >= vip_limit:
                bot.reply_to(message, error_ui("LIMIT REACHED", f"You have used your VIP limit."), parse_mode="Markdown")
                return
        else:
            if bot_remain <= 0:
                bot.reply_to(message, error_ui("SYSTEM EMPTY", "Global limit exhausted."), parse_mode="Markdown")
                return
            if user_usage.get(user_id, 0) >= USER_LIMIT:
                bot.reply_to(message, error_ui("LIMIT REACHED", f"You have used your daily limit."), parse_mode="Markdown")
                return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, error_ui("INVALID", f"Use: `{message.text.split()[0]} {{region}} {{uid}}`"), parse_mode="Markdown")
        return

    region = args[1].upper()
    uid = args[2]

    if region not in ALLOWED_REGIONS:
        bot.reply_to(message, error_ui("INVALID REGION", f"Allowed: {', '.join(ALLOWED_REGIONS)}"), parse_mode="Markdown")
        return

    process_like_request(message, region, uid, user_id, user_name, likes_count)

def process_like_request(message, region, uid, user_id, user_name, likes_count=20):
    global bot_remain, user_usage
    
    if likes_count == 30:
        base_api = API_30_URL
        api_key = API_30_KEY
    else:
        base_api = API_20_URL
        api_key = API_20_KEY
    
    wait_msg = bot.reply_to(message, "⏳ Processing...")

    try:
        start_time = time.time()
        
        if likes_count == 30:
            url = f"{base_api}/like?api_key={api_key}&server_name={region.lower()}&uid={uid}"
        else:
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
            
            remain_requests = "♾️" if is_admin(user_id) else (USER_LIMIT - user_usage.get(user_id, 0))
            final_text = report_ui(data, region, status, response_time, remain_requests, likes_count)
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=final_text, parse_mode="HTML")
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("FAILED", "Could not process UID."), parse_mode="Markdown")

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=error_ui("ERROR", str(e)), parse_mode="Markdown")

@bot.message_handler(commands=['likeauto'])
def handle_likeauto(message):
    if not admin_full_control(message.from_user.id): 
        bot.reply_to(message, "❌ Admin only!", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 5:
        bot.reply_to(message, "⚠️ Usage: `/likeauto {region} {uid} {20/30} {days}`\nExample: `/likeauto BD 123456 20 7`", parse_mode="Markdown")
        return

    region, uid, package_str, days_str = args[1].upper(), args[2], args[3], args[4]
    
    if region not in ALLOWED_REGIONS:
        bot.reply_to(message, f"❌ Invalid region!", parse_mode="Markdown")
        return
    
    if package_str not in ['20', '30']:
        bot.reply_to(message, "❌ Package must be 20 or 30!", parse_mode="Markdown")
        return

    try:
        package, days = int(package_str), int(days_str)
        total_likes = package * days
    except ValueError:
        bot.reply_to(message, "❌ Invalid numbers!", parse_mode="Markdown")
        return

    db = load_auto_db()
    serial_num = str(db['next_serial']).zfill(4)
    db['next_serial'] += 1
    
    if package == 20:
        db['stats']['total_20_tasks'] = db['stats'].get('total_20_tasks', 0) + 1
    else:
        db['stats']['total_30_tasks'] = db['stats'].get('total_30_tasks', 0) + 1

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
        "nickname": "Waiting...",
        "created_at": time.time(),
        "status": "active"
    }
    
    if save_auto_db(db):
        bot.reply_to(message, f"""✅ **Auto Task Added!**
━━━━━━━━━━━━━━━━━━━━━━━
🎓 Task No: `{serial_num}`
🆔 UID: `{uid}`
💳 Package: {package} Likes/Day
📅 Duration: {days} Days
🎯 Total: {total_likes} Likes

📊 Total Tasks: {len(db['tasks'])}""", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Failed to save task!", parse_mode="Markdown")

@bot.message_handler(commands=['listauto'])
def handle_listauto(message):
    if not admin_full_control(message.from_user.id):
        return
    
    db = load_auto_db()
    tasks = db.get('tasks', {})
    
    if not tasks:
        bot.reply_to(message, "📭 **No auto tasks found!**\n\nUse `/likeauto` to add tasks.\nOr use `/fixdb` to recover old tasks.", parse_mode="Markdown")
        return
    
    msg = f"📊 **AUTO TASKS** ({len(tasks)} active)\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for serial, task in tasks.items():
        package_type = "💙 20 Likes" if task['package'] == 20 else "❤️ 30 Likes"
        progress = int((task['sent'] / task['total_target']) * 100) if task['total_target'] > 0 else 0
        msg += f"""🎓 **Task {serial}**
├─ UID: `{task['uid']}`
├─ {package_type}
├─ Sent: {task['sent']}/{task['total_target']} ({progress}%)
└─ Remain: {task['remain']}\n\n"""
    
    if len(msg) > 4000:
        for i in range(0, len(msg), 4000):
            bot.reply_to(message, msg[i:i+4000], parse_mode="Markdown")
    else:
        bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['autoremove'])
def handle_autoremove(message):
    if not admin_full_control(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ Usage: `/autoremove {serial}`\nExample: `/autoremove 0001`", parse_mode="Markdown")
        return
    
    serial = args[1].zfill(4)
    db = load_auto_db()
    
    if serial in db['tasks']:
        task = db['tasks'][serial]
        if task['package'] == 20:
            db['stats']['total_20_tasks'] = max(0, db['stats'].get('total_20_tasks', 0) - 1)
        else:
            db['stats']['total_30_tasks'] = max(0, db['stats'].get('total_30_tasks', 0) - 1)
        
        del db['tasks'][serial]
        save_auto_db(db)
        bot.reply_to(message, f"✅ Task {serial} removed!", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ Task {serial} not found!", parse_mode="Markdown")

@bot.message_handler(commands=['autotime'])
def handle_autotime(message):
    if not admin_full_control(message.from_user.id):
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        bot.reply_to(message, "⚠️ Usage: `/autotime HH:MM AM/PM`\nExample: `/autotime 08:57 AM`", parse_mode="Markdown")
        return
    
    db = load_auto_db()
    db['time'] = args[1].upper()
    save_auto_db(db)
    bot.reply_to(message, f"✅ Auto time set to: {args[1].upper()}", parse_mode="Markdown")

@bot.message_handler(commands=['checkdb'])
def handle_checkdb(message):
    if not admin_full_control(message.from_user.id):
        return
    
    db = load_auto_db()
    tasks = db.get('tasks', {})
    
    info = f"""📊 **Database Status**
━━━━━━━━━━━━━━━━━━━━━━━
📁 Data Directory: `{DATA_DIR}`
📄 Auto DB File: `{AUTO_DB_FILE}`
📁 File exists: `{os.path.exists(AUTO_DB_FILE)}`

📊 Tasks in DB: `{len(tasks)}`
💙 20 Likes Tasks: `{db['stats'].get('total_20_tasks', 0)}`
❤️ 30 Likes Tasks: `{db['stats'].get('total_30_tasks', 0)}`

⏰ Auto Time: `{db.get('time', 'Not Set')}`
📅 Last Run: `{db.get('last_run', 'Never')}`

📋 Task List: {list(tasks.keys()) if tasks else 'Empty'}"""
    
    bot.reply_to(message, info, parse_mode="Markdown")

@bot.message_handler(commands=['remains'])
def handle_remains(message):
    vips = load_vip()
    user_id = message.from_user.id
    
    if is_admin(user_id):
        uses_left = "♾️ Unlimited"
    elif str(user_id) in vips:
        uses_left = f"{vips[str(user_id)]['limit'] - user_usage.get(user_id, 0)}/{vips[str(user_id)]['limit']}"
    else:
        uses_left = f"{USER_LIMIT - user_usage.get(user_id, 0)}/{USER_LIMIT}"
    
    text = f"""╭━〔 📊 SYSTEM REMAINS 〕━⬣
├─ Global Bot: {bot_remain}/15
├─ Your Limit: {uses_left}
╰━━━━━━━━━━━━━━━━━━⬣"""
    bot.reply_to(message, text, parse_mode="Markdown")

# ==========================================
# AUTO TASK EXECUTOR
# ==========================================
auto_task_running = False

def execute_auto_tasks():
    global auto_task_running
    if auto_task_running:
        return
    
    auto_task_running = True
    print("🔍 Executing auto tasks...")
    
    db = load_auto_db()
    tasks = db.get('tasks', {})
    
    if not tasks:
        auto_task_running = False
        return
    
    for serial, task in list(tasks.items()):
        if task['package'] == 20:
            url = f"{API_20_URL}/like?uid={task['uid']}&server_name={task['region'].lower()}&key={API_20_KEY}"
        else:
            url = f"{API_30_URL}/like?api_key={API_30_KEY}&server_name={task['region'].lower()}&uid={task['uid']}"
        
        try:
            response = requests.get(url, timeout=15)
            data = response.json()
            
            if data.get('status') in [1, 2]:
                added = data.get('LikesGivenByAPI', 0)
                task['sent'] += added
                task['remain'] -= added
                task['days_completed'] += 1
                
                msg = f"✅ Auto Task {serial}\nUID: {task['uid']}\nSent: {added} likes\nTotal: {task['sent']}/{task['total_target']}"
                bot.send_message(task['chat_id'], msg)
            
            save_auto_db(db)
            
            if task['remain'] <= 0:
                bot.send_message(task['chat_id'], f"✅ Task {serial} completed!")
                db = load_auto_db()
                if serial in db.get('tasks', {}):
                    del db['tasks'][serial]
                    save_auto_db(db)
            
            time.sleep(3)
            
        except Exception as e:
            print(f"Task {serial} error: {e}")
    
    auto_task_running = False

def cron_worker():
    print("⏳ Cron worker started...")
    tz = pytz.timezone('Asia/Dhaka')
    last_date = ""
    
    while True:
        try:
            now = datetime.datetime.now(tz)
            current_time = now.strftime("%I:%M %p")
            current_date = now.strftime("%Y-%m-%d")
            
            db = load_auto_db()
            target_time = db.get('time', '08:57 AM')
            tasks = db.get('tasks', {})
            
            if tasks and current_time == target_time and last_date != current_date:
                print(f"🎌 Running tasks at {current_time}")
                last_date = current_date
                execute_auto_tasks()
            
        except Exception as e:
            print(f"Cron error: {e}")
        
        time.sleep(30)

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    print("🚀 Bot starting on Railway...")
    print(f"📂 Data directory: {DATA_DIR}")
    
    # Try to fix and recover database on startup
    print("\n🔧 Running database recovery...")
    fixed_db = fix_and_load_database()
    tasks_count = len(fixed_db.get('tasks', {}))
    
    if tasks_count > 0:
        print(f"\n✅ Successfully loaded {tasks_count} tasks!")
        for serial, task in fixed_db['tasks'].items():
            print(f"   🎓 {serial}: {task['uid']} - {task['package']} likes")
    else:
        print("\n⚠️ No tasks found. Use /likeauto to add tasks.")
    
    print("\n" + "="*50)
    print("🤖 Bot is ready!")
    print("Commands:")
    print("  /likeauto - Add auto task")
    print("  /listauto - List tasks")
    print("  /fixdb - Fix database")
    print("  /checkdb - Check status")
    print("="*50)
    
    # Start cron thread
    cron_thread = threading.Thread(target=cron_worker, daemon=True)
    cron_thread.start()
    
    # Start bot
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)
