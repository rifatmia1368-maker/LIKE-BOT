import os
import json
import time
import telebot
import requests
import threading
import logging
import pytz
from datetime import datetime, date, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8488122911:AAHU6tmSSGDA5KWCuiCE0hDyS6bcuHapgUY")
OWNER_ID = int(os.getenv("OWNER_ID", "7603719412"))
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "2"))
GROUP_DAILY_LIMIT = int(os.getenv("GROUP_DAILY_LIMIT", "50"))
GROUP_JOIN_LINK = os.getenv("GROUP_JOIN_LINK", "https://t.me/riyadob52likegroup")

# Channel Config
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@riyadalhasanbackupchanel")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/riyadalhasanbackupchanel")

# Required Group Config
REQUIRED_GROUP_USERNAME = os.getenv("REQUIRED_GROUP_USERNAME", "@riyadautolikegroup")
REQUIRED_GROUP_LINK = os.getenv("REQUIRED_GROUP_LINK", "https://t.me/riyadautolikegroup")
REQUIRED_GROUP_ID = int(os.getenv("REQUIRED_GROUP_ID", "-1003764299339"))

# Task Groups
TASK_GROUP_1 = int(os.getenv("TASK_GROUP_1", "-1003764299339"))
TASK_GROUP_2 = int(os.getenv("TASK_GROUP_2", "-1003809015521"))
TASK_GROUPS = [TASK_GROUP_1, TASK_GROUP_2]

# API Configuration
API_KEY = "SAIFUL1"
API_BASE_URL = "http://2.56.246.128:30264"

# Supported Regions
SUPPORTED_REGIONS = ["ME", "ID", "TH", "VN", "SG", "BD", "PK", "MY", "PH", "RU", "AFR"]

# Auto Like Time
AUTO_LIKE_HOUR = int(os.getenv("AUTO_LIKE_HOUR", "4"))
AUTO_LIKE_MINUTE = int(os.getenv("AUTO_LIKE_MINUTE", "0"))

# Rate limiting
RATE_LIMIT = 10
REQUEST_TIMEOUT = 60
# =========================================

# ================= TIMEZONE CONFIG =================
BANGLADESH_TZ = pytz.timezone('Asia/Dhaka')
# ==================================================

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)
lock = threading.Lock()

# ================= DATA STORAGE FILES =================
DATA_DIR = "bot_data"
VIP_FILE = os.path.join(DATA_DIR, "vip_users.json")
AUTO_LIKE_FILE = os.path.join(DATA_DIR, "auto_like.json")
ALLOWED_GROUPS_FILE = os.path.join(DATA_DIR, "allowed_groups.json")
LIKE_TRACKER_FILE = os.path.join(DATA_DIR, "like_tracker.json")
GROUP_TRACKER_FILE = os.path.join(DATA_DIR, "group_tracker.json")
BROADCAST_FILE = os.path.join(DATA_DIR, "broadcast.json")
AUTO_TIME_FILE = os.path.join(DATA_DIR, "auto_time.json")
ADMIN_FILE = os.path.join(DATA_DIR, "admin_users.json")
SYSTEM_STATUS_FILE = os.path.join(DATA_DIR, "system_status.json")
AUTO_LIKE_USERS_FILE = os.path.join(DATA_DIR, "auto_like_users.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ================= DATA LOAD/SAVE FUNCTIONS =================
def load_json_data(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if filename == LIKE_TRACKER_FILE or filename == GROUP_TRACKER_FILE:
                    converted_data = {}
                    for key, value in data.items():
                        if isinstance(value, dict) and 'date' in value:
                            year, month, day = map(int, value['date'].split('-'))
                            value['date'] = date(year, month, day)
                        try:
                            converted_data[int(key)] = value
                        except:
                            converted_data[key] = value
                    return converted_data
                if filename == AUTO_LIKE_USERS_FILE:
                    converted_data = {}
                    for key, value in data.items():
                        converted_data[key] = {}
                        for uid, uid_data in value.items():
                            converted_data[key][uid] = uid_data
                            if 'expiry_date' in uid_data and uid_data['expiry_date']:
                                expiry_parts = uid_data['expiry_date'].split('-')
                                if len(expiry_parts) == 3:
                                    converted_data[key][uid]['expiry_date'] = date(int(expiry_parts[0]), int(expiry_parts[1]), int(expiry_parts[2]))
                    return converted_data
                return data
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
    return default

def save_json_data(filename, data):
    try:
        if filename == LIKE_TRACKER_FILE or filename == GROUP_TRACKER_FILE:
            serializable_data = {}
            for key, value in data.items():
                if isinstance(value, dict) and 'date' in value:
                    serializable_data[str(key)] = {
                        'used': value['used'],
                        'date': value['date'].isoformat()
                    }
                else:
                    serializable_data[str(key)] = value
        elif filename == AUTO_LIKE_USERS_FILE:
            serializable_data = {}
            for tg_user_id, uids in data.items():
                serializable_data[tg_user_id] = {}
                for uid, uid_data in uids.items():
                    serializable_data[tg_user_id][uid] = uid_data.copy()
                    if 'expiry_date' in uid_data and uid_data['expiry_date']:
                        serializable_data[tg_user_id][uid]['expiry_date'] = uid_data['expiry_date'].isoformat()
            data = serializable_data
        else:
            if isinstance(data, set):
                serializable_data = list(data)
            else:
                serializable_data = data
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")

# Load all data
VIP_USERS = set(load_json_data(VIP_FILE, []))
AUTO_LIKE_UIDS = set(load_json_data(AUTO_LIKE_FILE, []))
ALLOWED_GROUP_IDS = set(load_json_data(ALLOWED_GROUPS_FILE, []))
like_tracker = load_json_data(LIKE_TRACKER_FILE, {})
GROUP_LIMIT_TRACKER = load_json_data(GROUP_TRACKER_FILE, {})
broadcast_data = load_json_data(BROADCAST_FILE, {"messages": [], "stats": {"total": 0, "sent": 0, "failed": 0}})
auto_time_data = load_json_data(AUTO_TIME_FILE, {"hour": AUTO_LIKE_HOUR, "minute": AUTO_LIKE_MINUTE})
ADMIN_USERS = set(load_json_data(ADMIN_FILE, []))
SYSTEM_STATUS = load_json_data(SYSTEM_STATUS_FILE, {"like_system": True})
AUTO_LIKE_USERS = load_json_data(AUTO_LIKE_USERS_FILE, {})
rate_limiter = {}

def save_all_data():
    save_json_data(VIP_FILE, list(VIP_USERS))
    save_json_data(AUTO_LIKE_FILE, list(AUTO_LIKE_UIDS))
    save_json_data(ALLOWED_GROUPS_FILE, list(ALLOWED_GROUP_IDS))
    save_json_data(LIKE_TRACKER_FILE, like_tracker)
    save_json_data(GROUP_TRACKER_FILE, GROUP_LIMIT_TRACKER)
    save_json_data(BROADCAST_FILE, broadcast_data)
    save_json_data(AUTO_TIME_FILE, auto_time_data)
    save_json_data(ADMIN_FILE, list(ADMIN_USERS))
    save_json_data(SYSTEM_STATUS_FILE, SYSTEM_STATUS)
    save_json_data(AUTO_LIKE_USERS_FILE, AUTO_LIKE_USERS)
    logger.info("All data saved to files")

def get_display_username(message):
    if message.from_user.username:
        return f"@{message.from_user.username}"
    else:
        return message.from_user.first_name

# ================= FIXED API FUNCTION =================
def call_api(uid, region="BD"):
    """API Call - http://2.56.246.128:30264/like?api_key=SAIFUL1&server_name={region}&uid={uid}"""
    if not uid or not uid.isdigit():
        return {"status": 0, "error": "Invalid UID format"}
    
    url = f"{API_BASE_URL}/like"
    params = {
        "uid": uid,
        "server_name": region.lower(),
        "api_key": API_KEY
    }
    
    try:
        logger.info(f"📡 API Call: {url}?api_key={API_KEY}&server_name={region.lower()}&uid={uid}")
        
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT, verify=False)
        
        logger.info(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"✅ API Response: {data}")
                
                # Response format check
                if 'status' in data:
                    if str(data['status']) == '1' or data['status'] == 1:
                        data['status'] = 1
                    elif str(data['status']) == '2' or data['status'] == 2:
                        data['status'] = 2
                    else:
                        data['status'] = 1
                else:
                    data['status'] = 1
                
                return data
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON Error: {e}")
                return {"status": 0, "error": f"Invalid JSON: {response.text[:100]}"}
        else:
            logger.error(f"❌ HTTP Error: {response.status_code}")
            return {"status": 0, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.Timeout:
        logger.error(f"⏰ Timeout")
        return {"status": 0, "error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        logger.error(f"🔌 Connection Error")
        return {"status": 0, "error": "Connection error"}
    except Exception as e:
        logger.error(f"💥 Error: {e}")
        return {"status": 0, "error": str(e)[:50]}

# ================= TEST COMMAND =================
@bot.message_handler(commands=['testapi'])
def test_api_command(message):
    """Test API connection"""
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Owner only!")
        return
    
    try:
        args = message.text.split()
        uid = args[1] if len(args) > 1 else "2004537688"
        region = args[2].upper() if len(args) > 2 else "BD"
        
        msg = bot.reply_to(message, "🔍 Testing API...")
        
        result = call_api(uid, region)
        
        if result.get("status") == 0:
            text = f"❌ API FAILED\nError: {result.get('error', 'Unknown')}"
        else:
            name = result.get('PlayerNickname', result.get('nickname', 'N/A'))
            likes = result.get('LikesGivenByAPI', result.get('likes_given', 'N/A'))
            text = f"✅ API WORKING!\n\n🌍 Region: {region}\n👤 Name: {name}\n🆔 UID: {uid}\n❤️ Likes: {likes}"
        
        bot.edit_message_text(text, msg.chat.id, msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ================= SIMPLE START COMMAND =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, """
╭━━━━━━━━━━━━━━━✪
│🤖 RIYAD OB52 LIKE BOT
╰━━━━━━━━━━━━━━━✪

✅ Bot is online and working!

📌 Commands:
• /like BD <UID> - Send likes
• /testapi <UID> - Test API
• /help - All commands

🔰 Example: /like BD 2004537688
    """)

@bot.message_handler(commands=['like'])
def like_cmd(message):
    try:
        args = message.text.split()
        
        if len(args) != 3:
            bot.reply_to(message, "❌ Usage: /like BD 123456789")
            return
        
        region = args[1].upper()
        uid = args[2]
        
        msg = bot.reply_to(message, f"⏳ Processing UID {uid}...")
        
        result = call_api(uid, region)
        
        if result.get("status") == 0:
            text = f"❌ API Error: {result.get('error', 'Unknown')}"
        elif result.get("status") == 2:
            name = result.get('PlayerNickname', 'N/A')
            text = f"⚠️ {name} - Already reached max limit!"
        else:
            name = result.get('PlayerNickname', 'N/A')
            likes = result.get('LikesGivenByAPI', 'N/A')
            text = f"✅ Like sent to {name}!\n➕ Given: {likes} likes"
        
        bot.edit_message_text(text, msg.chat.id, msg.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = """
╭━━━━━━━━━━━━━━━✪
│📋 COMMANDS
╰━━━━━━━━━━━━━━━✪

📌 /like <region> <UID> - Send likes
📌 /testapi <UID> - Test API
📌 /start - Start bot
📌 /help - Help menu

🌍 Regions: BD, ID, SG, MY, TH, VN, PK, PH, RU, ME, AFR
    """
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, f"Send /like BD UID to get likes!\nYour message: {message.text}")

# ================= MAIN =================
if __name__ == "__main__":
    print("="*50)
    print("🤖 BOT STARTING")
    print("="*50)
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print(f"Owner ID: {OWNER_ID}")
    print(f"API URL: {API_BASE_URL}")
    print("="*50)
    
    # Remove webhook
    try:
        bot.remove_webhook()
        print("✅ Webhook removed")
    except:
        pass
    
    print("\n🚀 Bot is running!")
    print("📱 Open Telegram and send /start\n")
    
    try:
        bot.infinity_polling(timeout=60, skip_pending=True)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(5)
