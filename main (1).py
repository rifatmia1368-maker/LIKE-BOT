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

# ================= AUTO LIKE USER MANAGEMENT =================
def add_auto_like_for_user(tg_user_id, uid, days, region="BD"):
    try:
        today_bd = datetime.now(BANGLADESH_TZ).date()
        expiry_date = today_bd + timedelta(days=days)
        
        tg_user_id_str = str(tg_user_id)
        if tg_user_id_str not in AUTO_LIKE_USERS:
            AUTO_LIKE_USERS[tg_user_id_str] = {}
        
        if uid in AUTO_LIKE_USERS[tg_user_id_str]:
            old_expiry = AUTO_LIKE_USERS[tg_user_id_str][uid].get('expiry_date')
            if old_expiry and old_expiry >= today_bd:
                return False, f"⚠️ UID {uid} already has auto like until {old_expiry}"
        
        AUTO_LIKE_USERS[tg_user_id_str][uid] = {
            "added_date": today_bd.isoformat(),
            "expiry_date": expiry_date,
            "days": days,
            "region": region.upper(),
            "added_by": "admin"
        }
        
        AUTO_LIKE_UIDS.add(uid)
        save_all_data()
        return True, f"✅ Auto like added for UID {uid}\n📅 Expires: {expiry_date}\n🌍 Region: {region.upper()}\n👤 User ID: {tg_user_id}"
    except Exception as e:
        logger.error(f"Error adding auto like for user {tg_user_id}: {e}")
        return False, f"❌ Error: {str(e)}"

def remove_auto_like_for_user(tg_user_id, uid):
    try:
        tg_user_id_str = str(tg_user_id)
        if tg_user_id_str in AUTO_LIKE_USERS and uid in AUTO_LIKE_USERS[tg_user_id_str]:
            del AUTO_LIKE_USERS[tg_user_id_str][uid]
            
            uid_exists = False
            for user_data in AUTO_LIKE_USERS.values():
                if uid in user_data:
                    uid_exists = True
                    break
            
            if not uid_exists:
                AUTO_LIKE_UIDS.discard(uid)
            
            save_all_data()
            return True, f"✅ Auto like removed for UID {uid}"
        else:
            return False, f"❌ UID {uid} not found for user {tg_user_id}"
    except Exception as e:
        logger.error(f"Error removing auto like for user {tg_user_id}: {e}")
        return False, f"❌ Error: {str(e)}"

def get_user_auto_likes(tg_user_id):
    tg_user_id_str = str(tg_user_id)
    if tg_user_id_str in AUTO_LIKE_USERS:
        return AUTO_LIKE_USERS[tg_user_id_str]
    return {}

def get_all_active_auto_likes():
    today_bd = datetime.now(BANGLADESH_TZ).date()
    active_likes = {}
    
    for tg_user_id, uids in AUTO_LIKE_USERS.items():
        for uid, uid_data in uids.items():
            expiry_date = uid_data.get('expiry_date')
            if isinstance(expiry_date, str):
                expiry_parts = expiry_date.split('-')
                expiry_date = date(int(expiry_parts[0]), int(expiry_parts[1]), int(expiry_parts[2]))
            
            if expiry_date and expiry_date >= today_bd:
                if tg_user_id not in active_likes:
                    active_likes[tg_user_id] = {}
                active_likes[tg_user_id][uid] = uid_data
    
    return active_likes

def get_remaining_days(expiry_date):
    today_bd = datetime.now(BANGLADESH_TZ).date()
    if isinstance(expiry_date, str):
        expiry_parts = expiry_date.split('-')
        expiry_date = date(int(expiry_parts[0]), int(expiry_parts[1]), int(expiry_parts[2]))
    days_left = (expiry_date - today_bd).days
    return days_left

def cleanup_expired_auto_likes():
    today_bd = datetime.now(BANGLADESH_TZ).date()
    removed_count = 0
    expired_notifications = {}
    
    for tg_user_id in list(AUTO_LIKE_USERS.keys()):
        for uid in list(AUTO_LIKE_USERS[tg_user_id].keys()):
            expiry_date = AUTO_LIKE_USERS[tg_user_id][uid].get('expiry_date')
            if isinstance(expiry_date, str):
                expiry_parts = expiry_date.split('-')
                expiry_date = date(int(expiry_parts[0]), int(expiry_parts[1]), int(expiry_parts[2]))
            
            if expiry_date and expiry_date < today_bd:
                if tg_user_id not in expired_notifications:
                    expired_notifications[tg_user_id] = []
                
                expired_notifications[tg_user_id].append({
                    "uid": uid,
                    "expiry_date": expiry_date,
                    "region": AUTO_LIKE_USERS[tg_user_id][uid].get('region', 'BD'),
                    "added_date": AUTO_LIKE_USERS[tg_user_id][uid].get('added_date', 'N/A')
                })
                
                del AUTO_LIKE_USERS[tg_user_id][uid]
                removed_count += 1
        
        if len(AUTO_LIKE_USERS[tg_user_id]) == 0:
            del AUTO_LIKE_USERS[tg_user_id]
    
    AUTO_LIKE_UIDS.clear()
    for user_data in AUTO_LIKE_USERS.values():
        for uid in user_data.keys():
            AUTO_LIKE_UIDS.add(uid)
    
    for tg_user_id, expired_uids in expired_notifications.items():
        try:
            user_id_int = int(tg_user_id)
            for expired in expired_uids:
                expiry_msg = format_expiry_notification(expired)
                bot.send_message(user_id_int, expiry_msg)
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"Failed to send expiry notification to {tg_user_id}: {e}")
    
    if removed_count > 0:
        save_all_data()
        logger.info(f"Removed {removed_count} expired auto likes")
        owner_msg = (
            "╭━━━━━━━━━━━━━━━✪\n"
            "│🗑️ EXPIRED AUTO LIKES\n"
            "╰━━━━━━━━━━━━━━━✪\n\n"
            f"📊 Total Expired: {removed_count}\n"
            f"👤 Affected Users: {len(expired_notifications)}\n\n"
            "✨ Auto cleanup completed! ✨"
        )
        try:
            bot.send_message(OWNER_ID, owner_msg)
        except:
            pass
    
    return removed_count

def format_expiry_notification(expired_data):
    uid = expired_data.get("uid")
    expiry_date = expired_data.get("expiry_date")
    region = expired_data.get("region", "BD")
    added_date = expired_data.get("added_date", "N/A")
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│⏰ AUTO LIKE EXPIRED\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ❌ EXPIRED UID ✦ ⟯\n"
        f"│🆔 UID: {uid}\n"
        f"│🌍 REGION: {region}\n"
        f"│📅 ADDED: {added_date}\n"
        f"│📆 EXPIRED ON: {expiry_date}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 💡 RENEWAL PACKAGES ✦ ⟯\n"
        "│⚠️ Your auto like has expired!\n"
        "│🌟 Buy again to continue service:\n"
        "│   • 30 Days = 30৳\n"
        "│   • 60 Days = 50৳\n"
        "│   • 90 Days = 70৳\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📞 HOW TO BUY ✦ ⟯\n"
        "│📲 Inbox: @riyadalhasan11\n"
        "│💬 Send your UID and package\n"
        "│✅ Payment: bKash/Nagad/Rocket\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Thank you for using our service! ✨"
    )
    return text

# ================= API FUNCTION =================
def call_api(uid, region="BD"):
    if not uid or not uid.isdigit():
        return {"status": 0, "error": "Invalid UID format"}
    
    url = f"{API_BASE_URL}/like"
    params = {
        "uid": uid,
        "server_name": region.lower(),
        "api_key": API_KEY
    }
    
    try:
        logger.info(f"Calling API for UID: {uid}, Region: {region}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT, verify=False)
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"API Response for UID {uid}: {data}")
                if 'status' not in data:
                    data['status'] = 1
                return data
            except ValueError as e:
                logger.error(f"JSON decode error for UID {uid}: {e}")
                return {"status": 0, "error": "Invalid JSON response"}
        else:
            logger.error(f"HTTP error for UID {uid}: {response.status_code}")
            return {"status": 0, "error": f"HTTP Error: {response.status_code}"}
            
    except requests.exceptions.Timeout:
        return {"status": 0, "error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        return {"status": 0, "error": "Connection error"}
    except Exception as e:
        logger.error(f"Unexpected error for UID {uid}: {e}")
        return {"status": 0, "error": f"Error: {str(e)[:50]}"}

# ================= BOX STYLE RESPONSE FORMATTER =================

def format_like_success(data, user_type="👤 FREE", used="1", total_limit="1", username=None):
    name = data.get('PlayerNickname', data.get('nickname', 'N/A'))
    uid = data.get('UID', data.get('uid', 'N/A'))
    region = data.get('Region', data.get('region', 'BD')).upper()
    likes_given = data.get('LikesGivenByAPI', data.get('likes_given', data.get('like', '74')))
    likes_before = data.get('LikesbeforeCommand', data.get('likes_before', data.get('old', '20447')))
    likes_after = data.get('LikesafterCommand', data.get('likes_after', data.get('new', '20521')))
    
    user_display = username if username else "User"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│💝 LIKE SENT SUCCESSFULLY ☺️\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 PLAYER INFO ✦ ⟯\n"
        f"│👤 NAME: {name}\n"
        f"│🆔 UID: {uid}\n"
        f"│🌍 REGION: {region}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ❤️ LIKE DETAILS ✦ ⟯\n"
        f"│➕ LIKES GIVEN: {likes_given}\n"
        f"│👍 LIKES BEFORE: {likes_before}\n"
        f"│❤️ LIKES AFTER: {likes_after}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Thank you for using our service! ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
        f"│♻️ REMAINS: ({used}/{total_limit})\n"
        f"│🙋🏻User: {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_max_reached(data, username=None):
    name = data.get('PlayerNickname', data.get('nickname', 'N/A'))
    uid = data.get('UID', data.get('uid', 'N/A'))
    region = data.get('Region', data.get('region', 'BD')).upper()
    likes_before = data.get('LikesbeforeCommand', data.get('likes_before', data.get('old', 'N/A')))
    likes_after = data.get('LikesafterCommand', data.get('likes_after', data.get('new', 'N/A')))
    
    user_display = username if username else "User"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│⚠️ LIKE LIMIT REACHED ❌\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 PLAYER INFO ✦ ⟯\n"
        f"│👤 NAME: {name}\n"
        f"│🆔 UID: {uid}\n"
        f"│🌍 REGION: {region}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ❤️ LIKE DETAILS ✦ ⟯\n"
        f"│👍 LIKES BEFORE: {likes_before}\n"
        f"│❤️ LIKES AFTER: {likes_after}\n"
        f"│📊 STATUS: MAX REACHED\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Thank you for using our service! ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"      
        f"│🙋🏻User: {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_error(uid, error_msg, username=None):
    user_display = username if username else "User"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│❌ ERROR OCCURRED ⚠️\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ❌ ERROR DETAILS ✦ ⟯\n"
        f"│🆔 UID: {uid}\n"
        f"│⚠️ ERROR: {error_msg[:50]}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Please try again later! ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
        f"│🙋🏻User: {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_start(user_name, user_type, daily_limit, group_limit, auto_hour, auto_min, username=None, system_status=True):
    time_suffix = "AM" if auto_hour < 12 else "PM"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    user_display = username if username else user_name
    system_status_text = "🟢 ON" if system_status else "🔴 OFF"
    regions_str = ", ".join(SUPPORTED_REGIONS)
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🤖 RIYAD OB52 LIKE BOT\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 USER INFO ✦ ⟯\n"
        f"│👤 NAME: {user_name}\n"
        f"│👑 STATUS: {user_type}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📋 COMMANDS ✦ ⟯\n"
        "│• /like <region> <UID> – SEND LIKE\n"
        "│• /remain – DAILY LIMIT\n"
        "│• /myid – YOUR ID\n"
        "│• /status – BOT STATUS\n"
        "│• /myauto – YOUR AUTO LIKES\n"
        "│• /regions – SUPPORTED REGIONS\n"
        "│• /help – HELP MENU\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⚙️ LIMITS ✦ ⟯\n"
        f"│📊 USER: {daily_limit}/DAY\n"
        f"│👥 GROUP: {group_limit}/DAY\n"
        f"│⏰ AUTO: {time_str} (BDT)\n"
        f"│🔘 SYSTEM: {system_status_text}\n"
        f"│🌍 REGIONS: {regions_str}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📢 REQUIRED TO JOIN ✦ ⟯\n"
        f"│📢 CHANNEL: {CHANNEL_USERNAME}\n"
        f"│👥 GROUP: {REQUIRED_GROUP_USERNAME}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Thank you for using our service! ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
        "│👑 OWNER: @riyadalhasan11\n"
        "│🔰 EXAMPLE: /like BD 123456789\n"
        f"│🙋🏻User: {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_remain(user_name, user_type, used, total, group_info="", username=None):
    user_display = username if username else user_name
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│📊 DAILY STATUS\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 USER INFO ✦ ⟯\n"
        f"│👤 NAME: {user_name}\n"
        f"│👑 STATUS: {user_type}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📊 LIMIT DETAILS ✦ ⟯\n"
        f"│✅ USED: {used}/{total}\n"
        f"│⏳ LEFT: {max(0, total - used) if isinstance(used, int) else '∞'}\n"
        f"{group_info}"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Thank you for using our service! ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
        f"│🙋🏻User: {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_myid(user_id, user_name, user_type, username=None):
    user_display = username if username else user_name
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🆔 YOUR INFORMATION\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 USER INFO ✦ ⟯\n"
        f"│🆔 ID: {user_id}\n"
        f"│📛 NAME: {user_name}\n"
        f"│👑 STATUS: {user_type}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Thank you for using our service! ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
        f"│🙋🏻User: {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_processing(uid, region, user_type):
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│⏳ PROCESSING...\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 REQUEST INFO ✦ ⟯\n"
        f"│👤 STATUS: {user_type}\n"
        f"│🆔 UID: {uid}\n"
        f"│🌍 REGION: {region.upper()}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Please wait... ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
        "│🙋🏻User: Processing\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_auto_time_changed(old_hour, old_min, new_hour, new_min, username=None):
    old_suffix = "AM" if old_hour < 12 else "PM"
    old_display = old_hour if old_hour <= 12 else old_hour - 12
    if old_display == 0:
        old_display = 12
    old_time = f"{old_display}:{old_min:02d} {old_suffix}"
    
    new_suffix = "AM" if new_hour < 12 else "PM"
    new_display = new_hour if new_hour <= 12 else new_hour - 12
    if new_display == 0:
        new_display = 12
    new_time = f"{new_display}:{new_min:02d} {new_suffix}"
    
    user_display = username if username else "Owner"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│⏰ AUTO TIME UPDATED\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⏰ TIME CHANGE ✦ ⟯\n"
        f"│📊 OLD: {old_time}\n"
        f"│📊 NEW: {new_time} (BDT)\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Auto like will run at this time daily! ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
        f"│🙋🏻User: {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_system_status(user_type, status_on):
    status_text = "🟢 ON" if status_on else "🔴 OFF"
    action = "TURNED ON" if status_on else "TURNED OFF"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        f"│⚙️ LIKE SYSTEM {action}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📊 STATUS ✦ ⟯\n"
        f"│👑 BY: {user_type}\n"
        f"│🔘 SYSTEM: {status_text}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ System updated successfully! ✨"
    )
    return text

def format_system_off_message(username=None):
    user_display = username if username else "User"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🔴 SYSTEM IS OFF\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⚠️ INFO ✦ ⟯\n"
        "│🔘 The like system is currently OFF\n"
        "│⏰ Please try again later\n"
        "│👑 Contact owner for more info\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Thank you for understanding! ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
        f"│🙋🏻User: {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_auto_like_list(user_auto_likes):
    if not user_auto_likes:
        return "╭━━━━━━━━━━━━━━━✪\n│📭 NO ACTIVE AUTO LIKES\n╰━━━━━━━━━━━━━━━✪"
    
    today_bd = datetime.now(BANGLADESH_TZ).date()
    text = "╭━━━━━━━━━━━━━━━✪\n│🌟 YOUR AUTO LIKES\n╰━━━━━━━━━━━━━━━✪\n\n"
    
    for uid, data in user_auto_likes.items():
        expiry = data.get('expiry_date')
        if isinstance(expiry, str):
            expiry_parts = expiry.split('-')
            expiry = date(int(expiry_parts[0]), int(expiry_parts[1]), int(expiry_parts[2]))
        
        days_left = (expiry - today_bd).days if expiry else 0
        region = data.get('region', 'BD')
        
        if days_left < 0:
            status = "❌ EXPIRED"
        elif days_left == 0:
            status = "⚠️ EXPIRES TODAY"
        elif days_left <= 3:
            status = f"⚠️ {days_left} DAYS LEFT"
        else:
            status = f"✅ {days_left} DAYS LEFT"
        
        text += f"╭━⟮ 🆔 UID: {uid} ⟯\n"
        text += f"│🌍 REGION: {region}\n"
        text += f"│📅 ADDED: {data.get('added_date', 'N/A')}\n"
        text += f"│📆 EXPIRES: {expiry}\n"
        text += f"│📊 STATUS: {status}\n"
        text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    return text

def format_all_auto_likes():
    active_likes = get_all_active_auto_likes()
    
    if not active_likes:
        return "╭━━━━━━━━━━━━━━━✪\n│📭 NO ACTIVE AUTO LIKES\n╰━━━━━━━━━━━━━━━✪"
    
    today_bd = datetime.now(BANGLADESH_TZ).date()
    text = "╭━━━━━━━━━━━━━━━✪\n│📋 ALL ACTIVE AUTO LIKES\n╰━━━━━━━━━━━━━━━✪\n\n"
    
    for tg_user_id, uids in active_likes.items():
        text += f"╭━⟮ 👤 TG USER: {tg_user_id} ⟯\n"
        for uid, data in uids.items():
            expiry = data.get('expiry_date')
            if isinstance(expiry, str):
                expiry_parts = expiry.split('-')
                expiry = date(int(expiry_parts[0]), int(expiry_parts[1]), int(expiry_parts[2]))
            
            days_left = (expiry - today_bd).days if expiry else 0
            region = data.get('region', 'BD')
            
            if days_left < 0:
                status = "EXPIRED"
            elif days_left == 0:
                status = "EXPIRES TODAY"
            elif days_left <= 3:
                status = f"{days_left} DAYS LEFT ⚠️"
            else:
                status = f"{days_left} DAYS LEFT ✅"
            
            text += f"│   🆔 UID: {uid}\n"
            text += f"│   🌍 REGION: {region}\n"
            text += f"│   📅 EXPIRES: {expiry} ({status})\n"
        text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    total_uids = sum(len(uids) for uids in active_likes.values())
    text += f"╭━⟮ ✦ 📊 TOTAL ✦ ⟯\n"
    text += f"│📌 USERS: {len(active_likes)}\n"
    text += f"│📌 UIDs: {total_uids}\n"
    text += "╰━━━━━━━━━━━━━━━✪"
    
    return text

def format_region_list():
    text = "╭━━━━━━━━━━━━━━━✪\n│🌍 SUPPORTED REGIONS\n╰━━━━━━━━━━━━━━━✪\n\n"
    for i, region in enumerate(SUPPORTED_REGIONS, 1):
        text += f"╭━⟮ {i}. {region} ⟯\n"
    text += f"\n╭━⟮ ✦ 📝 USAGE ✦ ⟯\n"
    text += f"│📌 /like <region> <UID>\n"
    text += f"│🔰 EXAMPLE: /like BD 123456789\n"
    text += "╰━━━━━━━━━━━━━━━✪"
    return text

def format_auto_like_dm_box(results):
    now_bd = datetime.now(BANGLADESH_TZ)
    
    text = "╭━━━━━━━━━━━━━━━✪\n"
    text += "│🤖 AUTO LIKE REPORT\n"
    text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    text += "╭━⟮ ✦ ⏰ TIME ✦ ⟯\n"
    text += f"│🕒 {now_bd.strftime('%I:%M %p')}\n"
    text += f"│📅 {now_bd.strftime('%d-%m-%Y')}\n"
    text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    for res in results:
        uid = res.get("uid")
        name = res.get("name", "N/A")
        region = res.get("region", "BD")
        status = res.get("status")
        status_text = res.get("status_text", "")
        status_emoji = res.get("status_emoji", "❓")
        result_data = res.get("result", {})
        expiry_date = res.get("expiry_date")
        days_left = res.get("days_left")
        added_date = res.get("added_date", "N/A")
        
        uid_num = result_data.get('UID', result_data.get('uid', uid))
        likes_given = result_data.get('LikesGivenByAPI', result_data.get('likes_given', result_data.get('like', 'N/A')))
        likes_before = result_data.get('LikesbeforeCommand', result_data.get('likes_before', result_data.get('old', 'N/A')))
        likes_after = result_data.get('LikesafterCommand', result_data.get('likes_after', result_data.get('new', 'N/A')))
        
        expiry_status = ""
        if days_left is not None:
            if days_left < 0:
                expiry_status = f"\n│📅 EXPIRY: EXPIRED ❌"
            elif days_left == 0:
                expiry_status = f"\n│📅 EXPIRY: EXPIRES TODAY ⚠️"
            elif days_left <= 3:
                expiry_status = f"\n│📅 EXPIRY: {days_left} DAYS LEFT ⚠️"
            else:
                expiry_status = f"\n│📅 EXPIRY: {days_left} DAYS LEFT ✅"
        
        text += f"\n╭━⟮ 🆔 UID: {uid_num} ⟯\n"
        text += f"│🌍 REGION: {region}\n"
        text += f"│{status_emoji} STATUS: {status_text}\n"
        text += f"│👤 NAME: {name[:35]}\n"
        
        if status == 0:
            error_msg = result_data.get('error', 'Unknown error')[:50]
            text += f"│⚠️ ERROR: {error_msg}\n"
        else:
            text += f"│👍 BEFORE: {likes_before}\n"
            text += f"│❤️ AFTER: {likes_after}\n"
            text += f"│➕ GIVEN: {likes_given}\n"
        
        if added_date and added_date != 'N/A':
            text += f"│📅 ADDED: {added_date}\n"
        if expiry_date:
            text += f"│📆 EXPIRES: {expiry_date}"
        text += expiry_status
        text += f"\n╰━━━━━━━━━━━━━━━✪"
    
    text += "\n\n✨ Thank you for using our service! ✨"
    
    return text

# ================= RATE LIMITING =================
def check_rate_limit(user_id):
    now = time.time()
    minute_ago = now - 60
    
    with lock:
        if user_id in rate_limiter:
            rate_limiter[user_id] = [t for t in rate_limiter[user_id] if t > minute_ago]
            if len(rate_limiter[user_id]) >= RATE_LIMIT:
                return False
            rate_limiter[user_id].append(now)
        else:
            rate_limiter[user_id] = [now]
    return True

# ================= CHANNEL & GROUP CHECK =================
def check_channel_membership(user_id):
    try:
        if user_id == OWNER_ID:
            return True
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Channel check error for user {user_id}: {e}")
        return False

def check_group_membership(user_id):
    try:
        if user_id == OWNER_ID:
            return True
        member = bot.get_chat_member(REQUIRED_GROUP_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Group check error for user {user_id}: {e}")
        return False

def both_required(func):
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        if user_id == OWNER_ID:
            return func(message, *args, **kwargs)
        
        channel_ok = check_channel_membership(user_id)
        group_ok = check_group_membership(user_id)
        
        if not channel_ok or not group_ok:
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton("1️⃣ JOIN CHANNEL", url=CHANNEL_LINK))
            keyboard.add(InlineKeyboardButton("2️⃣ JOIN GROUP", url=REQUIRED_GROUP_LINK))
            keyboard.add(InlineKeyboardButton("✅ VERIFY", callback_data="check_both_membership"))
            
            channel_status = "✅ JOINED" if channel_ok else "❌ NOT JOINED"
            group_status = "✅ JOINED" if group_ok else "❌ NOT JOINED"
            
            msg = (
                "╭━━━━━━━━━━━━━━━✪\n"
                "│🔒 JOIN CHANNEL & GROUP\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "✨ Click the buttons below ✨\n\n"
                "1️⃣ First, join the channel\n"
                "2️⃣ Then, join the group\n"
                "3️⃣ Finally, click VERIFY\n\n"
                "╭━⟮ ✦ 📢 CHANNEL ✦ ⟯\n"
                f"│📢 Name: {CHANNEL_USERNAME}\n"
                f"│📊 Status: {channel_status}\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "╭━⟮ ✦ 👥 GROUP ✦ ⟯\n"
                f"│👥 Name: {REQUIRED_GROUP_USERNAME}\n"
                f"│📊 Status: {group_status}\n"
                "╰━━━━━━━━━━━━━━━✪"
            )
            bot.reply_to(message, msg, parse_mode=None, reply_markup=keyboard)
            return
        return func(message, *args, **kwargs)
    return wrapper

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "check_both_membership":
        user_id = call.from_user.id
        channel_ok = check_channel_membership(user_id)
        group_ok = check_group_membership(user_id)
        
        if channel_ok and group_ok:
            user_type = get_user_type(user_id)
            bot.answer_callback_query(call.id, "✅ ACCESS GRANTED!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
            welcome_text = (
                "╭━━━━━━━━━━━━━━━✪\n"
                "│✅ ACCESS GRANTED\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                f"╭━⟮ ✦ 👤 WELCOME ✦ ⟯\n"
                f"│👋 Welcome {call.from_user.first_name}!\n"
                f"│👑 Status: {user_type}\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "✨ You can now use the bot! ✨\n\n"
                "╭━⟮ ✦ 📢 VERIFIED ✦ ⟯\n"
                "│✅ Channel: JOINED\n"
                "│✅ Group: JOINED\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
                "│🔰 Use: /like BD UID\n"
                f"│🙋🏻User: {get_display_username(call.message)}\n"
                "╰━━━━━━━━━━━━━━━✪"
            )
            
            if user_type == "👤 FREE":
                welcome_text += (
                    "\n\n╭━⟮ ✦ 👑 VIP OFFER ✦ ⟯\n"
                    "│🌟 Want unlimited likes?\n"
                    "│📲 Contact @riyadalhasan11\n"
                    "╰━━━━━━━━━━━━━━━✪"
                )
            
            bot.send_message(call.message.chat.id, welcome_text)
        else:
            channel_status = "✅ JOINED" if channel_ok else "❌ NOT JOINED"
            group_status = "✅ JOINED" if group_ok else "❌ NOT JOINED"
            bot.answer_callback_query(call.id, f"Channel: {channel_status} | Group: {group_status}", show_alert=True)
    
    elif call.data.startswith('broadcast_'):
        handle_broadcast_callback(call)

# ================= HELPERS =================
def get_user_type(user_id):
    if user_id == OWNER_ID:
        return "👑 OWNER"
    elif user_id in ADMIN_USERS:
        return "🛡️ ADMIN"
    elif user_id in VIP_USERS:
        return "🌟 VIP"
    else:
        return "👤 FREE"

def is_allowed(message):
    if message.from_user.id == OWNER_ID or message.from_user.id in ADMIN_USERS:
        return True
    return message.chat.id in ALLOWED_GROUP_IDS

def is_unlimited(user_id):
    return user_id == OWNER_ID or user_id in ADMIN_USERS or user_id in VIP_USERS

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    return user_id == OWNER_ID or user_id in ADMIN_USERS

def get_daily_usage(user_id):
    today_bd = datetime.now(BANGLADESH_TZ).date()
    with lock:
        if user_id in like_tracker and like_tracker[user_id]["date"] == today_bd:
            return like_tracker[user_id]["used"]
        like_tracker[user_id] = {"used": 0, "date": today_bd}
        save_json_data(LIKE_TRACKER_FILE, like_tracker)
        return 0

def increment_daily_usage(user_id):
    today_bd = datetime.now(BANGLADESH_TZ).date()
    with lock:
        if user_id in like_tracker and like_tracker[user_id]["date"] == today_bd:
            like_tracker[user_id]["used"] += 1
        else:
            like_tracker[user_id] = {"used": 1, "date": today_bd}
        save_json_data(LIKE_TRACKER_FILE, like_tracker)

def get_group_daily_usage(group_id):
    today_bd = datetime.now(BANGLADESH_TZ).date()
    with lock:
        if group_id in GROUP_LIMIT_TRACKER and GROUP_LIMIT_TRACKER[group_id]["date"] == today_bd:
            return GROUP_LIMIT_TRACKER[group_id]["used"]
        GROUP_LIMIT_TRACKER[group_id] = {"used": 0, "date": today_bd}
        save_json_data(GROUP_TRACKER_FILE, GROUP_LIMIT_TRACKER)
        return 0

def increment_group_daily_usage(group_id):
    today_bd = datetime.now(BANGLADESH_TZ).date()
    with lock:
        if group_id in GROUP_LIMIT_TRACKER and GROUP_LIMIT_TRACKER[group_id]["date"] == today_bd:
            GROUP_LIMIT_TRACKER[group_id]["used"] += 1
        else:
            GROUP_LIMIT_TRACKER[group_id] = {"used": 1, "date": today_bd}
        save_json_data(GROUP_TRACKER_FILE, GROUP_LIMIT_TRACKER)

def is_like_system_on():
    return SYSTEM_STATUS.get("like_system", True)

def set_like_system(status):
    global SYSTEM_STATUS
    SYSTEM_STATUS["like_system"] = status
    save_json_data(SYSTEM_STATUS_FILE, SYSTEM_STATUS)

# ================= AUTO TASK SENDER =================
def send_auto_task():
    cleanup_expired_auto_likes()
    
    now_bd = datetime.now(BANGLADESH_TZ)
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    time_suffix = "AM" if auto_hour < 12 else "PM"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    auto_time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    print(f"\n{'='*60}")
    print(f"📊 AUTO TASK STARTED at {now_bd.strftime('%H:%M:%S')}")
    print(f"⏰ Auto Time: {auto_time_str}")
    print(f"📅 Date: {now_bd.strftime('%d-%m-%Y')}")
    print(f"📊 Total UIDs: {len(AUTO_LIKE_UIDS)}")
    print(f"{'='*60}\n")
    
    if not AUTO_LIKE_UIDS:
        for group_id in TASK_GROUPS:
            try:
                bot.send_message(group_id, 
                    "╭━━━━━━━━━━━━━━━✪\n"
                    "│📭 AUTO LIKE REPORT\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    "╭━⟮ ✦ ⏰ SCHEDULE INFO ✦ ⟯\n"
                    f"│🕒 Auto Time: {auto_time_str}\n"
                    f"│📅 Date: {now_bd.strftime('%d-%m-%Y')}\n"
                    f"│🌏 Timezone: BDT (UTC+6)\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    "╭━⟮ ✦ 📊 STATUS ✦ ⟯\n"
                    "│📭 Auto like list is EMPTY!\n"
                    "│➡️ Add UIDs with /autolike command\n"
                    "╰━━━━━━━━━━━━━━━✪"
                )
            except:
                continue
        return
    
    processing_messages = []
    for group_id in TASK_GROUPS:
        try:
            msg = bot.send_message(
                group_id,
                "╭━━━━━━━━━━━━━━━✪\n"
                "│⏳ AUTO TASK IN PROGRESS\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "╭━⟮ ✦ ⏰ SCHEDULE INFO ✦ ⟯\n"
                f"│🕒 Auto Time: {auto_time_str}\n"
                f"│📅 Date: {now_bd.strftime('%d-%m-%Y')}\n"
                f"│🌏 Timezone: BDT (UTC+6)\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "╭━⟮ ✦ 📊 PROCESSING ✦ ⟯\n"
                f"│📊 Total UIDs: {len(AUTO_LIKE_UIDS)}\n"
                f"│🔄 Status: Processing each UID...\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "✨ Please wait... ✨"
            )
            processing_messages.append((group_id, msg.message_id))
        except Exception as e:
            logger.error(f"Error sending to group {group_id}: {e}")
    
    all_results = []
    success_count = 0
    max_count = 0
    fail_count = 0
    region_stats = {}
    user_results = {}
    
    uids_to_process = list(AUTO_LIKE_UIDS)
    
    for idx, uid in enumerate(uids_to_process, 1):
        assigned_user = None
        assigned_region = "BD"
        expiry_date = None
        days_left = None
        added_date = None
        
        for tg_user_id, uids in AUTO_LIKE_USERS.items():
            if uid in uids:
                assigned_user = tg_user_id
                assigned_region = uids[uid].get('region', 'BD')
                expiry_date = uids[uid].get('expiry_date')
                added_date = uids[uid].get('added_date', 'N/A')
                days_left = get_remaining_days(expiry_date) if expiry_date else None
                break
        
        if days_left is not None and days_left < 0:
            print(f"   ⚠️ UID {uid} is expired - skipping")
            continue
        
        print(f"[{idx}/{len(uids_to_process)}] Processing UID: {uid} (Region: {assigned_region})")
        
        try:
            res = call_api(uid, assigned_region)
            status = res.get("status")
            name = res.get('PlayerNickname', res.get('nickname', 'N/A'))
            uid_num = res.get('UID', res.get('uid', uid))
            region = res.get('Region', res.get('region', assigned_region)).upper()
            likes_given = res.get('LikesGivenByAPI', res.get('likes_given', res.get('like', 'N/A')))
            likes_before = res.get('LikesbeforeCommand', res.get('likes_before', res.get('old', 'N/A')))
            likes_after = res.get('LikesafterCommand', res.get('likes_after', res.get('new', 'N/A')))
            
            region_stats[region] = region_stats.get(region, 0) + 1
            
            if status == 2:
                status_emoji = "⚠️"
                status_text = "MAX REACHED"
                given_text = "0"
                max_count += 1
            elif status == 0:
                status_emoji = "❌"
                status_text = "FAILED"
                error_msg = res.get('error', 'Unknown error')[:35]
                given_text = "0"
                fail_count += 1
            else:
                status_emoji = "✅"
                status_text = "SUCCESS"
                given_text = str(likes_given)
                success_count += 1
            
            expiry_status = ""
            if days_left is not None:
                if days_left < 0:
                    expiry_status = f"\n│📅 EXPIRY: EXPIRED ❌"
                elif days_left == 0:
                    expiry_status = f"\n│📅 EXPIRY: EXPIRES TODAY ⚠️"
                elif days_left <= 3:
                    expiry_status = f"\n│📅 EXPIRY: {days_left} DAYS LEFT ⚠️"
                else:
                    expiry_status = f"\n│📅 EXPIRY: {days_left} DAYS LEFT ✅"
            
            result_text = (
                f"\n╭━⟮ 🆔 UID: {uid_num} ⟯\n"
                f"│🌍 REGION: {region}\n"
                f"│{status_emoji} STATUS: {status_text}\n"
                f"│👤 NAME: {name[:35]}\n"
                f"│👍 BEFORE: {likes_before}\n"
                f"│❤️ AFTER: {likes_after}\n"
                f"│➕ GIVEN: {given_text}"
            )
            
            if status == 0:
                result_text += f"\n│⚠️ ERROR: {error_msg}"
            
            if added_date and added_date != 'N/A':
                result_text += f"\n│📅 ADDED: {added_date}"
            if expiry_date:
                result_text += f"\n│📆 EXPIRES: {expiry_date}"
            result_text += expiry_status
            result_text += f"\n╰━━━━━━━━━━━━━━━✪"
            
            all_results.append(result_text)
            
            if assigned_user:
                if assigned_user not in user_results:
                    user_results[assigned_user] = []
                user_results[assigned_user].append({
                    "uid": uid,
                    "result": res,
                    "region": region,
                    "status": status,
                    "expiry_date": expiry_date,
                    "days_left": days_left,
                    "added_date": added_date,
                    "name": name,
                    "status_text": status_text,
                    "status_emoji": status_emoji
                })
            
            time.sleep(2)
            
        except Exception as e:
            fail_count += 1
            result_text = (
                f"\n╭━⟮ 🆔 UID: {uid} ⟯\n"
                f"│❌ STATUS: ERROR\n"
                f"│⚠️ ERROR: {str(e)[:50]}\n"
                f"╰━━━━━━━━━━━━━━━✪"
            )
            all_results.append(result_text)
            print(f"   ❌ ERROR - {str(e)[:40]}")
            
            if assigned_user:
                if assigned_user not in user_results:
                    user_results[assigned_user] = []
                user_results[assigned_user].append({
                    "uid": uid,
                    "result": {"status": 0, "error": str(e)},
                    "region": assigned_region,
                    "status": 0,
                    "expiry_date": expiry_date,
                    "days_left": days_left,
                    "added_date": added_date,
                    "name": "N/A",
                    "status_text": "ERROR",
                    "status_emoji": "❌"
                })
    
    total = len(uids_to_process)
    success_rate = (success_count / total * 100) if total > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"📊 AUTO TASK SUMMARY")
    print(f"📌 Total UIDs: {total}")
    print(f"✅ Success: {success_count}")
    print(f"⚠️ Max Reached: {max_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"{'='*60}\n")
    
    report = "╭━━━━━━━━━━━━━━━✪\n"
    report += "│📋 AUTO LIKE TASK REPORT\n"
    report += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    report += "╭━⟮ ✦ ⏰ SCHEDULE INFO ✦ ⟯\n"
    report += f"│🕒 Auto Time: {auto_time_str}\n"
    report += f"│📅 Date: {now_bd.strftime('%d-%m-%Y')}\n"
    report += f"│🌏 Timezone: BDT (UTC+6)\n"
    report += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    report += "╭━⟮ ✦ 📊 SUMMARY ✦ ⟯\n"
    report += f"│📌 Total UIDs: {total}\n"
    report += f"│✅ Success: {success_count}\n"
    report += f"│⚠️ Max Reached: {max_count}\n"
    report += f"│❌ Failed: {fail_count}\n"
    report += f"│📈 Success Rate: {success_rate:.1f}%\n"
    report += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    if region_stats:
        report += "╭━⟮ ✦ 🌍 REGION STATS ✦ ⟯\n"
        for region, count in sorted(region_stats.items(), key=lambda x: x[1], reverse=True):
            report += f"│{region}: {count}\n"
        report += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    report += "╭━⟮ ✦ 🔍 DETAILED RESULTS ✦ ⟯\n"
    for res in all_results:
        report += res
    report += "\n╰━━━━━━━━━━━━━━━✪\n\n"
    report += "✨ Thank you for using our service! ✨\n\n"
    report += "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
    report += "│🤖 Bot: @riyadob52likebot\n"
    report += "│👑 Owner: @riyadalhasan11\n"
    report += "╰━━━━━━━━━━━━━━━✪"
    
    for group_id, msg_id in processing_messages:
        try:
            bot.edit_message_text(report, group_id, msg_id, parse_mode=None)
            print(f"✅ Report sent to group: {group_id}")
        except Exception as e:
            logger.error(f"Error editing message in group {group_id}: {e}")
            try:
                if len(report) > 4096:
                    chunks = [report[i:i+4096] for i in range(0, len(report), 4096)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            bot.edit_message_text(chunk, group_id, msg_id, parse_mode=None)
                        else:
                            bot.send_message(group_id, chunk, parse_mode=None)
                else:
                    bot.send_message(group_id, report, parse_mode=None)
                print(f"✅ Report sent to group: {group_id} (as new message)")
            except:
                pass
    
    dm_sent = 0
    dm_failed = 0
    for tg_user_id, results in user_results.items():
        try:
            user_id_int = int(tg_user_id)
            dm_text = format_auto_like_dm_box(results)
            bot.send_message(user_id_int, dm_text)
            dm_sent += 1
            print(f"📨 DM sent to user {tg_user_id} ({len(results)} reports)")
            time.sleep(0.5)
        except Exception as e:
            dm_failed += 1
            logger.error(f"Failed to send DM to {tg_user_id}: {e}")
    
    summary_report = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│📊 AUTO TASK COMPLETE\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        f"📌 Total: {total}\n"
        f"✅ Success: {success_count}\n"
        f"⚠️ Max: {max_count}\n"
        f"❌ Failed: {fail_count}\n"
        f"📈 Rate: {success_rate:.1f}%\n\n"
        f"📨 DM Sent: {dm_sent} users\n"
        f"❌ DM Failed: {dm_failed}\n\n"
        "✨ Task completed successfully! ✨"
    )
    bot.send_message(OWNER_ID, summary_report)
    
    save_all_data()
    print(f"✅ Auto task fully completed at {now_bd.strftime('%H:%M:%S')}")

# ================= AUTO LIKE SCHEDULER =================
def auto_scheduler():
    global auto_time_data
    last_run_date = None
    error_count = 0
    check_count = 0
    
    print("\n🕐 AUTO SCHEDULER STARTED")
    print("⏰ Checking every 30 seconds for scheduled time\n")
    
    while True:
        try:
            auto_time_data = load_json_data(AUTO_TIME_FILE, {"hour": AUTO_LIKE_HOUR, "minute": AUTO_LIKE_MINUTE})
            now_bd = datetime.now(BANGLADESH_TZ)
            auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
            auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
            
            current_hour = now_bd.hour
            current_minute = now_bd.minute
            
            check_count += 1
            if check_count % 2 == 0:
                print(f"⏰ [{now_bd.strftime('%H:%M:%S')}] Scheduler Check #{check_count} - Target: {auto_hour:02d}:{auto_min:02d} | UIDs: {len(AUTO_LIKE_UIDS)}")
            
            if current_hour == auto_hour and current_minute == auto_min:
                if last_run_date != now_bd.date():
                    print(f"\n{'='*60}")
                    print(f"✅✅✅ AUTO TASK TRIGGERED at {now_bd.strftime('%H:%M:%S')} ✅✅✅")
                    print(f"📅 Date: {now_bd.strftime('%Y-%m-%d')}")
                    print(f"🎯 Target Time: {auto_hour:02d}:{auto_min:02d}")
                    print(f"📊 UIDs to process: {len(AUTO_LIKE_UIDS)}")
                    print(f"{'='*60}\n")
                    logger.info(f"✅ AUTO TASK TRIGGERED at {now_bd.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    try:
                        if AUTO_LIKE_UIDS:
                            send_auto_task()
                        else:
                            print(f"⚠️ No UIDs in auto list - skipping")
                            for group_id in TASK_GROUPS:
                                try:
                                    bot.send_message(group_id, 
                                        "╭━━━━━━━━━━━━━━━✪\n"
                                        "│⚠️ AUTO TASK SKIPPED\n"
                                        "╰━━━━━━━━━━━━━━━✪\n\n"
                                        f"⏰ Time: {auto_hour:02d}:{auto_min:02d}\n"
                                        f"📅 Date: {now_bd.strftime('%d-%m-%Y')}\n\n"
                                        "📭 No UIDs in auto list!\n"
                                        "➡️ Add UIDs with /autolike command"
                                    )
                                except:
                                    pass
                        
                        last_run_date = now_bd.date()
                        error_count = 0
                        save_all_data()
                        
                        print(f"✅ Last run date updated to: {last_run_date}")
                        print(f"⏱️ Waiting 2 minutes to avoid duplicate runs...\n")
                        
                        time.sleep(120)
                        
                    except Exception as e:
                        logger.error(f"❌ Error in auto task execution: {e}")
                        print(f"❌❌❌ Error in auto task execution: {e}")
                        error_count += 1
                        
                        if error_count > 3:
                            print("⚠️ Multiple errors detected, waiting 5 minutes...")
                            time.sleep(300)
            
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ Critical error in auto_scheduler: {e}")
            print(f"❌❌❌ CRITICAL ERROR: {e}")
            error_count += 1
            time.sleep(60)

# ================= COMMAND HANDLERS =================

@bot.message_handler(commands=['start'])
@both_required
def start_cmd(message):
    if not is_allowed(message) and message.from_user.id != OWNER_ID:
        bot.reply_to(message, 
            "╭━━━━━━━━━━━━━━━✪\n"
            "│❌ NOT ALLOWED\n"
            "╰━━━━━━━━━━━━━━━✪\n\n"
            "❌ This bot works only in allowed groups!"
        )
        return
    
    user_type = get_user_type(message.from_user.id)
    user_name = message.from_user.first_name
    username = get_display_username(message)
    
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    
    text = format_start(user_name, user_type, DAILY_LIMIT, GROUP_DAILY_LIMIT, auto_hour, auto_min, username, is_like_system_on())
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📢 CHANNEL", url=CHANNEL_LINK),
        InlineKeyboardButton("👥 GROUP", url=REQUIRED_GROUP_LINK)
    )
    
    bot.reply_to(message, text, reply_markup=keyboard)

@bot.message_handler(commands=['help'])
@both_required
def help_cmd(message):
    if not is_allowed(message) and message.from_user.id != OWNER_ID:
        return
    
    user_type = get_user_type(message.from_user.id)
    username = get_display_username(message)
    
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    time_suffix = "AM" if auto_hour < 12 else "PM"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    system_status = "🟢 ON" if is_like_system_on() else "🔴 OFF"
    regions_str = ", ".join(SUPPORTED_REGIONS)
    
    if is_admin(message.from_user.id):
        text = (
            "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n"
            f"│{user_type} COMMAND LIST\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 👤 USER COMMANDS ✦ ⟯\n"
            "│📌 /like <region> <UID> – Send likes to any UID\n"
            "│📌 /remain – Check your daily remaining limit\n"
            "│📌 /myid – Get your Telegram ID\n"
            "│📌 /status – Check bot status and statistics\n"
            "│📌 /myauto – View your auto like list with expiry\n"
            "│📌 /regions – Show all supported regions\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 👑 ADMIN/OWNER COMMANDS ✦ ⟯\n"
            "│📌 /task – View auto task information\n"
            "│📌 /autolike list – List all auto likes with expiry\n"
            "│📌 /autolike <days> <uid> <tg_userid> [region] – Add auto like\n"
            "│📌 /removeauto <uid> <tg_userid> – Remove auto like\n"
            "│📌 /listauto – List all active auto likes\n"
            "│📌 /userauto <tg_userid> – Check auto likes for a user\n"
            "│📌 /alt <time> – Change auto task time\n"
            "│📌 /scheduler – Check scheduler status\n"
            "│📌 /on – Turn like system ON\n"
            "│📌 /off – Turn like system OFF\n"
            "│📌 /addadmin <user_id> – Add new admin (Owner only)\n"
            "│📌 /removeadmin <user_id> – Remove admin (Owner only)\n"
            "│📌 /admins – List all admins (Owner only)\n"
            "│📌 /allow <group_id> – Allow a group (Owner only)\n"
            "│📌 /addvip <user_id> – Add VIP user (Owner only)\n"
            "│📌 /removevip <user_id> – Remove VIP user (Owner only)\n"
            "│📌 /limit <number> – Set user daily limit (Owner only)\n"
            "│📌 /glimit <number> – Set group daily limit (Owner only)\n"
            "│📌 /limits – Show all current limits (Owner only)\n"
            "│📌 /testapi [uid] [region] – Test API connection (Owner only)\n"
            "│📌 /broadcast <message> – Broadcast message (Owner only)\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ ⚙️ CURRENT SETTINGS ✦ ⟯\n"
            f"│👤 USER LIMIT: {DAILY_LIMIT}/day\n"
            f"│👥 GROUP LIMIT: {GROUP_DAILY_LIMIT}/day\n"
            f"│⏰ AUTO TIME: {time_str} (BDT)\n"
            f"│🔘 SYSTEM: {system_status}\n"
            f"│🌍 REGIONS: {regions_str}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 📢 REQUIRED TO JOIN ✦ ⟯\n"
            f"│📢 CHANNEL: {CHANNEL_USERNAME}\n"
            f"│👥 GROUP: {REQUIRED_GROUP_USERNAME}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "✨ Thank you for using our service! ✨\n\n"
            "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
            f"│🙋🏻 USER: {username}\n"
            "│👑 OWNER: @riyadalhasan11\n"
            "│🤖 BOT: @riyadob52likebot\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪"
        )
    else:
        text = (
            "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n"
            "│📚 USER COMMAND LIST\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 📋 AVAILABLE COMMANDS ✦ ⟯\n"
            "│📌 /like <region> <UID> – Send likes\n"
            "│📌 /remain – Check daily limit\n"
            "│📌 /myid – Get your ID\n"
            "│📌 /status – Bot status\n"
            "│📌 /myauto – Your auto likes\n"
            "│📌 /regions – Supported regions\n"
            "│📌 /help – Help menu\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ ⚙️ CURRENT LIMITS ✦ ⟯\n"
            f"│👤 USER: {DAILY_LIMIT}/day\n"
            f"│👥 GROUP: {GROUP_DAILY_LIMIT}/day\n"
            f"│⏰ AUTO: {time_str} (BDT)\n"
            f"│🔘 SYSTEM: {system_status}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "✨ Thank you for using our service! ✨\n\n"
            "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
            f"│🙋🏻 USER: {username}\n"
            "│👑 OWNER: @riyadalhasan11\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪"
        )
    
    bot.reply_to(message, text)

@bot.message_handler(commands=['regions'])
@both_required
def regions_cmd(message):
    text = format_region_list()
    bot.reply_to(message, text)

@bot.message_handler(commands=['myauto'])
@both_required
def myauto_cmd(message):
    if not is_allowed(message) and message.from_user.id != OWNER_ID:
        return
    
    user_id = message.from_user.id
    user_auto_likes = get_user_auto_likes(user_id)
    
    text = format_auto_like_list(user_auto_likes)
    bot.reply_to(message, text)

@bot.message_handler(commands=['like'])
@both_required
def like_cmd(message):
    try:
        if not is_like_system_on():
            username = get_display_username(message)
            text = format_system_off_message(username)
            bot.reply_to(message, text)
            return
        
        if not is_allowed(message) and message.from_user.id != OWNER_ID:
            bot.reply_to(message, 
                "╭━━━━━━━━━━━━━━━✪\n"
                "│❌ NOT ALLOWED\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "❌ This bot works only in allowed groups!"
            )
            return

        if not check_rate_limit(message.from_user.id):
            bot.reply_to(
                message,
                "╭━━━━━━━━━━━━━━━✪\n"
                "│⚠️ RATE LIMIT\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "⚠️ Too many requests! Please wait a minute."
            )
            return

        args = message.text.split()

        if len(args) != 3:
            bot.reply_to(
                message,
                "╭━━━━━━━━━━━━━━━✪\n"
                "│⚠️ INVALID FORMAT\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                f"📌 /like <region> <UID>\n"
                f"🌍 Supported: {', '.join(SUPPORTED_REGIONS)}\n"
                "🔰 Example: /like BD 123456789"
            )
            return

        region = args[1].upper()
        uid = args[2]

        if region not in SUPPORTED_REGIONS:
            bot.reply_to(
                message,
                "╭━━━━━━━━━━━━━━━✪\n"
                "│❌ UNSUPPORTED REGION\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                f"🌍 {region} is not supported!\n\n"
                f"✅ Supported: {', '.join(SUPPORTED_REGIONS)}"
            )
            return

        if not uid.isdigit() or len(uid) < 5 or len(uid) > 15:
            bot.reply_to(
                message,
                "╭━━━━━━━━━━━━━━━✪\n"
                "│⚠️ INVALID UID\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "📏 UID must be 5-15 digits"
            )
            return

        user_id = message.from_user.id
        user_type = get_user_type(user_id)
        username = get_display_username(message)

        if not is_unlimited(user_id):
            used = get_daily_usage(user_id)
            if used >= DAILY_LIMIT:
                bot.reply_to(
                    message,
                    "╭━━━━━━━━━━━━━━━✪\n"
                    "│🚫 DAILY LIMIT REACHED\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    f"📊 Used: {used}/{DAILY_LIMIT}\n\n"
                    "🌟 Get VIP for unlimited likes!\n"
                    "📲 Contact @riyadalhasan11"
                )
                return

        if message.chat.type in ['group', 'supergroup']:
            group_used = get_group_daily_usage(message.chat.id)
            if group_used >= GROUP_DAILY_LIMIT and not is_unlimited(user_id):
                bot.reply_to(
                    message,
                    "╭━━━━━━━━━━━━━━━✪\n"
                    "│🚫 GROUP LIMIT REACHED\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    f"📊 Group Used: {group_used}/{GROUP_DAILY_LIMIT}"
                )
                return

        proc = bot.reply_to(message, format_processing(uid, region, user_type))

        logger.info(f"Calling API for UID: {uid}, Region: {region}")
        res = call_api(uid, region)

        status = res.get("status")
        
        if status == 2:
            text = format_max_reached(res, username)
        elif status == 0:
            error_msg = res.get('error', res.get('msg', 'Unknown error'))
            text = format_error(uid, error_msg, username)
        else:
            if not is_unlimited(user_id):
                increment_daily_usage(user_id)
                if message.chat.type in ['group', 'supergroup']:
                    increment_group_daily_usage(message.chat.id)

            used = get_daily_usage(user_id) if not is_unlimited(user_id) else "∞"
            total = DAILY_LIMIT if not is_unlimited(user_id) else "∞"
            
            text = format_like_success(res, user_type, str(used), str(total), username)
            save_all_data()

        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("📢 CHANNEL", url=CHANNEL_LINK),
            InlineKeyboardButton("👥 GROUP", url=REQUIRED_GROUP_LINK)
        )
        
        try:
            bot.edit_message_text(text, proc.chat.id, proc.message_id, reply_markup=kb)
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            bot.send_message(message.chat.id, text, reply_markup=kb)
        
    except Exception as e:
        logger.error(f"Error in like command: {e}")
        error_text = format_error("Error", str(e)[:50], get_display_username(message))
        bot.reply_to(message, error_text)

@bot.message_handler(commands=['remain'])
@both_required
def remain_cmd(message):
    if not is_allowed(message) and message.from_user.id != OWNER_ID:
        return
    
    uid = message.from_user.id
    user_type = get_user_type(uid)
    user_name = message.from_user.first_name
    username = get_display_username(message)
    
    if is_unlimited(uid):
        text = format_remain(user_name, user_type, "∞", "∞", "", username)
    else:
        used = get_daily_usage(uid)
        
        group_info = ""
        if message.chat.type in ['group', 'supergroup']:
            group_used = get_group_daily_usage(message.chat.id)
            group_info = f"│👥 GROUP: {group_used}/{GROUP_DAILY_LIMIT}\n"
        
        text = format_remain(user_name, user_type, used, DAILY_LIMIT, group_info, username)
    
    bot.reply_to(message, text)

@bot.message_handler(commands=['myid'])
@both_required
def myid_cmd(message):
    if not is_allowed(message) and message.from_user.id != OWNER_ID:
        return
    
    user_type = get_user_type(message.from_user.id)
    user_name = message.from_user.first_name
    username = get_display_username(message)
    
    text = format_myid(message.from_user.id, user_name, user_type, username)
    bot.reply_to(message, text)

@bot.message_handler(commands=['status'])
@both_required
def status_cmd(message):
    if not is_allowed(message) and message.from_user.id != OWNER_ID:
        return
    
    user_type = get_user_type(message.from_user.id)
    username = get_display_username(message)
    
    now_bd = datetime.now(BANGLADESH_TZ)
    
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    time_suffix = "AM" if auto_hour < 12 else "PM"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    today_bd = now_bd.date()
    total_users_today = sum(1 for data in like_tracker.values() 
                           if isinstance(data, dict) and data.get("date") == today_bd)
    total_likes_today = sum(data["used"] for data in like_tracker.values() 
                           if isinstance(data, dict) and data.get("date") == today_bd)
    
    system_status_text = "🟢 ON" if is_like_system_on() else "🔴 OFF"
    active_auto = len(get_all_active_auto_likes())
    
    expiring_soon = 0
    for user_data in AUTO_LIKE_USERS.values():
        for uid_data in user_data.values():
            days_left = get_remaining_days(uid_data.get('expiry_date'))
            if 0 <= days_left <= 3:
                expiring_soon += 1
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🤖 BOT STATUS\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 YOUR STATUS ✦ ⟯\n"
        f"│👤 {user_type}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 🤖 BOT INFO ✦ ⟯\n"
        "│✅ Status: ONLINE\n"
        f"│👑 Owner: {OWNER_ID}\n"
        f"│📊 User Limit: {DAILY_LIMIT}\n"
        f"│👥 Group Limit: {GROUP_DAILY_LIMIT}\n"
        f"│⏰ Auto: {time_str}\n"
        f"│🔘 System: {system_status_text}\n"
        f"│🌏 Timezone: BDT (UTC+6)\n"
        f"│🌍 Regions: {len(SUPPORTED_REGIONS)}\n"
        f"│🌟 VIP: {len(VIP_USERS)}\n"
        f"│🛡️ Admins: {len(ADMIN_USERS)}\n"
        f"│⚡ Auto UIDs: {len(AUTO_LIKE_UIDS)}\n"
        f"│👤 Auto Users: {active_auto}\n"
        f"│⚠️ Expiring Soon: {expiring_soon}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📈 TODAY'S STATS ✦ ⟯\n"
        f"│👤 Active: {total_users_today}\n"
        f"│❤️ Likes: {total_likes_today}\n"
        f"│🕒 Current: {now_bd.strftime('%I:%M %p')}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Thank you for using our service! ✨\n\n"
        "╭━⟮ ✦ 🧾 DETAILS ✦ ⟯\n"
        f"│🙋🏻User: {username}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    
    bot.reply_to(message, text)

# ================= ADMIN/OWNER ONLY COMMANDS =================

@bot.message_handler(commands=['task'])
def task_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for bot owner and admins!")
        return
    
    if not AUTO_LIKE_UIDS:
        bot.reply_to(message, "📭 Auto like list is empty!")
        return
    
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    now_bd = datetime.now(BANGLADESH_TZ)
    
    next_run = now_bd.replace(hour=auto_hour, minute=auto_min, second=0, microsecond=0)
    if next_run <= now_bd:
        next_run = next_run + timedelta(days=1)
    
    time_diff = next_run - now_bd
    hours_until = int(time_diff.total_seconds() // 3600)
    minutes_until = int((time_diff.total_seconds() % 3600) // 60)
    
    time_suffix = "AM" if auto_hour < 12 else "PM"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    uid_list_text = ""
    for i, uid in enumerate(list(AUTO_LIKE_UIDS)[:15], 1):
        region = "BD"
        expiry_info = ""
        for user_data in AUTO_LIKE_USERS.values():
            if uid in user_data:
                region = user_data[uid].get('region', 'BD')
                expiry = user_data[uid].get('expiry_date')
                days_left = get_remaining_days(expiry) if expiry else None
                if days_left is not None:
                    if days_left < 0:
                        expiry_info = " [EXPIRED]"
                    elif days_left == 0:
                        expiry_info = " [EXPIRES TODAY]"
                    elif days_left <= 3:
                        expiry_info = f" [{days_left} DAYS LEFT]"
                break
        uid_list_text += f"│{i}. {uid} ({region}){expiry_info}\n"
    if len(AUTO_LIKE_UIDS) > 15:
        uid_list_text += f"│... and {len(AUTO_LIKE_UIDS) - 15} more\n"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│📋 AUTO LIKE INFORMATION\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⏰ SCHEDULE INFO ✦ ⟯\n"
        f"│🕒 Auto Time: {time_str} (daily)\n"
        f"│⏳ Next Run: in {hours_until}h {minutes_until}m\n"
        f"│📊 Total UIDs: {len(AUTO_LIKE_UIDS)}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 🆔 UID LIST ✦ ⟯\n"
        f"{uid_list_text}"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ Admin/Owner only command ✨"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['autolike'])
def add_auto_like_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for bot owner and admins!")
        return
    
    args = message.text.split()
    
    if len(args) >= 2 and args[1].lower() == 'list':
        show_auto_like_list(message)
        return
    
    if len(args) < 4 or len(args) > 5:
        bot.reply_to(
            message,
            "╭━━━━━━━━━━━━━━━✪\n"
            "│⚠️ AUTO LIKE USAGE\n"
            "╰━━━━━━━━━━━━━━━✪\n\n"
            "📌 /autolike list - View all auto likes\n\n"
            "📌 /autolike <days> <uid> <tg_user_id> [region]\n\n"
            "🔰 Examples:\n"
            "• /autolike 30 123456789 7603719412 BD\n"
            "• /autolike 7 987654321 1234567890 ID\n\n"
            f"🌍 Regions: {', '.join(SUPPORTED_REGIONS)}\n"
            "📅 Days: Number of days auto like will work"
        )
        return
    
    try:
        days = int(args[1])
        uid = args[2]
        tg_user_id = int(args[3])
        region = args[4].upper() if len(args) == 5 else "BD"
        
        if days <= 0:
            bot.reply_to(message, "❌ Days must be greater than 0!")
            return
        
        if not uid.isdigit() or len(uid) < 5 or len(uid) > 15:
            bot.reply_to(message, "❌ Invalid UID! Must be 5-15 digits.")
            return
        
        if region not in SUPPORTED_REGIONS:
            bot.reply_to(message, f"❌ Invalid region! Supported: {', '.join(SUPPORTED_REGIONS)}")
            return
        
        success, msg = add_auto_like_for_user(tg_user_id, uid, days, region)
        bot.reply_to(message, msg)
        
        if success:
            try:
                auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
                auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
                time_suffix = "AM" if auto_hour < 12 else "PM"
                display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
                if display_hour == 0:
                    display_hour = 12
                auto_time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
                
                expiry_date = datetime.now(BANGLADESH_TZ).date() + timedelta(days=days)
                
                notify_text = (
                    "╭━━━━━━━━━━━━━━━✪\n"
                    "│✨ AUTO LIKE ASSIGNED\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    f"🆔 UID: {uid}\n"
                    f"🌍 Region: {region}\n"
                    f"📅 Days: {days}\n"
                    f"📆 Expires: {expiry_date}\n"
                    f"⏰ Time: {auto_time_str} BDT\n\n"
                    "✨ Auto like will run daily!\n"
                    "📊 Check with /myauto"
                )
                bot.send_message(tg_user_id, notify_text)
            except:
                pass
                
    except ValueError:
        bot.reply_to(message, "❌ Invalid input! Days and User ID must be numbers.")
    except IndexError:
        bot.reply_to(message, "❌ Usage: /autolike <days> <uid> <tg_user_id> [region]")

def show_auto_like_list(message):
    if not AUTO_LIKE_USERS:
        bot.reply_to(message, "📭 No auto likes configured yet!\n\nUse: /autolike <days> <uid> <tg_user_id> [region]")
        return
    
    today_bd = datetime.now(BANGLADESH_TZ).date()
    
    total_uids = 0
    expired_count = 0
    expiring_soon = 0
    region_stats = {}
    
    for tg_user_id, uids in AUTO_LIKE_USERS.items():
        for uid, data in uids.items():
            total_uids += 1
            expiry = data.get('expiry_date')
            days_left = get_remaining_days(expiry) if expiry else None
            
            if days_left is not None:
                if days_left < 0:
                    expired_count += 1
                elif days_left <= 3:
                    expiring_soon += 1
            
            region = data.get('region', 'BD')
            region_stats[region] = region_stats.get(region, 0) + 1
    
    text = "╭━━━━━━━━━━━━━━━✪\n"
    text += "│📋 AUTO LIKE LIST\n"
    text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    text += "╭━⟮ ✦ 📊 STATISTICS ✦ ⟯\n"
    text += f"│📌 Total UIDs: {total_uids}\n"
    text += f"│👤 Total Users: {len(AUTO_LIKE_USERS)}\n"
    text += f"│⚠️ Expiring soon (≤3 days): {expiring_soon}\n"
    text += f"│❌ Expired: {expired_count}\n"
    text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    if region_stats:
        text += "╭━⟮ ✦ 🌍 REGION WISE ✦ ⟯\n"
        for region, count in sorted(region_stats.items(), key=lambda x: x[1], reverse=True):
            text += f"│{region}: {count} UID(s)\n"
        text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    text += "╭━⟮ ✦ 📋 DETAILED LIST ✦ ⟯\n"
    
    for tg_user_id, uids in AUTO_LIKE_USERS.items():
        try:
            chat = bot.get_chat(int(tg_user_id))
            user_name = chat.first_name if chat.first_name else f"User {tg_user_id}"
            if chat.username:
                user_name += f" (@{chat.username})"
        except:
            user_name = f"User {tg_user_id}"
        
        text += f"\n╭━⟮ 👤 {user_name} ⟯\n"
        text += f"│🆔 ID: {tg_user_id}\n"
        
        for uid, data in uids.items():
            expiry = data.get('expiry_date')
            days_left = get_remaining_days(expiry) if expiry else None
            region = data.get('region', 'BD')
            added_date = data.get('added_date', 'N/A')
            
            if days_left is not None:
                if days_left < 0:
                    status = "❌ EXPIRED"
                elif days_left == 0:
                    status = "⚠️ EXPIRES TODAY"
                elif days_left <= 3:
                    status = f"⚠️ {days_left} DAYS LEFT"
                else:
                    status = f"✅ {days_left} DAYS LEFT"
            else:
                status = "✅ ACTIVE"
            
            text += f"│\n"
            text += f"│   🆔 UID: {uid}\n"
            text += f"│   🌍 Region: {region}\n"
            text += f"│   📅 Added: {added_date}\n"
            text += f"│   📆 Expires: {expiry}\n"
            text += f"│   📊 Status: {status}\n"
            text += f"│   {'─' * 25}\n"
        
        text += "╰━━━━━━━━━━━━━━━✪\n"
    
    text += "\n✨ Use /removeauto <uid> <tg_user_id> to remove\n"
    text += "📊 Users can check their auto likes with /myauto"
    
    if len(text) > 4096:
        for i in range(0, len(text), 4096):
            bot.send_message(message.chat.id, text[i:i+4096])
    else:
        bot.reply_to(message, text)

@bot.message_handler(commands=['removeauto'])
def remove_auto_like_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for bot owner and admins!")
        return
    
    args = message.text.split()
    
    if len(args) != 3:
        bot.reply_to(message, "❌ Usage: /removeauto <uid> <tg_user_id>")
        return
    
    uid = args[1]
    
    try:
        tg_user_id = int(args[2])
        success, msg = remove_auto_like_for_user(tg_user_id, uid)
        bot.reply_to(message, msg)
        
        if success:
            try:
                bot.send_message(tg_user_id, 
                    "╭━━━━━━━━━━━━━━━✪\n"
                    "│❌ AUTO LIKE REMOVED\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    f"🆔 UID: {uid}\n\n"
                    "✨ Auto like has been removed! ✨")
            except:
                pass
    except ValueError:
        bot.reply_to(message, "❌ Invalid TG User ID!")

@bot.message_handler(commands=['listauto'])
def list_auto_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for bot owner and admins!")
        return
    
    text = format_all_auto_likes()
    bot.reply_to(message, text)

@bot.message_handler(commands=['userauto'])
def user_auto_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for bot owner and admins!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "❌ Usage: /userauto <tg_user_id>")
        return
    
    try:
        tg_user_id = args[1]
        user_auto_likes = get_user_auto_likes(int(tg_user_id))
        
        if not user_auto_likes:
            bot.reply_to(message, f"📭 No auto likes found for user {tg_user_id}")
            return
        
        today_bd = datetime.now(BANGLADESH_TZ).date()
        
        text = f"╭━━━━━━━━━━━━━━━✪\n"
        text += f"│👤 AUTO LIKES FOR USER\n"
        text += f"╰━━━━━━━━━━━━━━━✪\n\n"
        text += f"🆔 User ID: {tg_user_id}\n\n"
        
        for uid, data in user_auto_likes.items():
            expiry = data.get('expiry_date')
            days_left = get_remaining_days(expiry) if expiry else None
            region = data.get('region', 'BD')
            
            if days_left is not None:
                if days_left < 0:
                    status = "❌ EXPIRED"
                elif days_left == 0:
                    status = "⚠️ EXPIRES TODAY"
                elif days_left <= 3:
                    status = f"⚠️ {days_left} DAYS LEFT"
                else:
                    status = f"✅ {days_left} DAYS LEFT"
            else:
                status = "✅ ACTIVE"
            
            text += f"╭━⟮ 🆔 UID: {uid} ⟯\n"
            text += f"│🌍 Region: {region}\n"
            text += f"│📅 Added: {data.get('added_date', 'N/A')}\n"
            text += f"│📆 Expires: {expiry}\n"
            text += f"│📊 Status: {status}\n"
            text += "╰━━━━━━━━━━━━━━━✪\n\n"
        
        bot.reply_to(message, text)
        
    except ValueError:
        bot.reply_to(message, "❌ Invalid User ID! Must be a number.")

@bot.message_handler(commands=['alt'])
def auto_time_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for bot owner and admins!")
        return
    
    if len(message.text.split()) < 2:
        bot.reply_to(
            message,
            "╭━━━━━━━━━━━━━━━✪\n"
            "│⏰ AUTO TIME HELP\n"
            "╰━━━━━━━━━━━━━━━✪\n\n"
            "📌 /alt 4am   - Set to 4:00 AM\n"
            "📌 /alt 6pm   - Set to 6:00 PM\n"
            "📌 /alt 12am  - Set to 12:00 AM\n"
            "📌 /alt 12pm  - Set to 12:00 PM\n"
            "📌 /alt 8     - Set to 8:00 AM"
        )
        return
    
    try:
        time_arg = message.text.split()[1].lower().strip()
        old_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
        old_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
        
        if time_arg.endswith('am'):
            hour_str = time_arg.replace('am', '')
            if hour_str:
                new_hour = int(hour_str)
                if new_hour == 12:
                    new_hour = 0
                elif 1 <= new_hour <= 11:
                    pass
                else:
                    raise ValueError
                new_min = 0
            else:
                raise ValueError
        elif time_arg.endswith('pm'):
            hour_str = time_arg.replace('pm', '')
            if hour_str:
                new_hour = int(hour_str)
                if new_hour == 12:
                    new_hour = 12
                elif 1 <= new_hour <= 11:
                    new_hour += 12
                else:
                    raise ValueError
                new_min = 0
            else:
                raise ValueError
        else:
            new_hour = int(time_arg)
            if new_hour == 12:
                new_hour = 0
            elif new_hour < 0 or new_hour > 23:
                raise ValueError
            new_min = 0
        
        if new_hour < 0 or new_hour > 23:
            bot.reply_to(message, "❌ Invalid hour! Use 0-23")
            return
        
        auto_time_data["hour"] = new_hour
        auto_time_data["minute"] = new_min
        save_json_data(AUTO_TIME_FILE, auto_time_data)
        
        text = format_auto_time_changed(old_hour, old_min, new_hour, new_min, get_display_username(message))
        bot.reply_to(message, text)
        
    except (ValueError, IndexError):
        bot.reply_to(message, "❌ Invalid format! Use: /alt 4am, /alt 6pm, /alt 8")

@bot.message_handler(commands=['scheduler'])
def scheduler_check_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for bot owner and admins!")
        return
    
    now_bd = datetime.now(BANGLADESH_TZ)
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    
    next_run = now_bd.replace(hour=auto_hour, minute=auto_min, second=0, microsecond=0)
    if next_run <= now_bd:
        next_run = next_run + timedelta(days=1)
    
    time_diff = next_run - now_bd
    hours_until = int(time_diff.total_seconds() // 3600)
    minutes_until = int((time_diff.total_seconds() % 3600) // 60)
    
    scheduler_alive = False
    for thread in threading.enumerate():
        if thread.name == "AutoScheduler":
            scheduler_alive = True
            break
    
    expiring_soon = 0
    for user_data in AUTO_LIKE_USERS.values():
        for uid_data in user_data.values():
            days_left = get_remaining_days(uid_data.get('expiry_date'))
            if 0 <= days_left <= 3:
                expiring_soon += 1
    
    status_text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🤖 SCHEDULER STATUS\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        f"📅 Current Time: {now_bd.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"🌏 Timezone: Bangladesh (UTC+6)\n"
        f"⏰ Auto Time: {auto_hour:02d}:{auto_min:02d}\n"
        f"⏳ Next Run: in {hours_until}h {minutes_until}m\n"
        f"📊 Total UIDs: {len(AUTO_LIKE_UIDS)}\n"
        f"👤 Auto Users: {len(AUTO_LIKE_USERS)}\n"
        f"⚠️ Expiring Soon: {expiring_soon}\n"
        f"🔄 Scheduler Thread: {'✅ Alive' if scheduler_alive else '❌ Dead'}\n"
        f"📢 Channel: {CHANNEL_USERNAME}\n"
        f"👥 Required Group: {REQUIRED_GROUP_USERNAME}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    
    bot.reply_to(message, status_text)

@bot.message_handler(commands=['on'])
def turn_on_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for bot owner and admins!")
        return
    
    if is_like_system_on():
        bot.reply_to(message, "⚠️ Like system is already ON!")
        return
    
    set_like_system(True)
    text = format_system_status(get_user_type(message.from_user.id), True)
    bot.reply_to(message, text)

@bot.message_handler(commands=['off'])
def turn_off_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for bot owner and admins!")
        return
    
    if not is_like_system_on():
        bot.reply_to(message, "⚠️ Like system is already OFF!")
        return
    
    set_like_system(False)
    text = format_system_status(get_user_type(message.from_user.id), False)
    bot.reply_to(message, text)

# ================= ADMIN MANAGEMENT (OWNER ONLY) =================

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for the bot owner!")
        return
    
    try:
        uid = int(message.text.split()[1])
        if uid == OWNER_ID:
            bot.reply_to(message, "❌ Owner cannot be added as admin!")
            return
        if uid in ADMIN_USERS:
            bot.reply_to(message, f"⚠️ User {uid} is already an admin!")
            return
        ADMIN_USERS.add(uid)
        save_json_data(ADMIN_FILE, list(ADMIN_USERS))
        bot.reply_to(message, f"✅ User {uid} is now an ADMIN!")
        logger.info(f"Admin added: {uid} by owner {message.from_user.id}")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Usage: /addadmin user_id")

@bot.message_handler(commands=['removeadmin'])
def remove_admin(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for the bot owner!")
        return
    
    try:
        uid = int(message.text.split()[1])
        if uid in ADMIN_USERS:
            ADMIN_USERS.discard(uid)
            save_json_data(ADMIN_FILE, list(ADMIN_USERS))
            bot.reply_to(message, f"✅ Removed admin from user {uid}")
            logger.info(f"Admin removed: {uid} by owner {message.from_user.id}")
        else:
            bot.reply_to(message, f"❌ User {uid} is not an admin")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Usage: /removeadmin user_id")

@bot.message_handler(commands=['admins'])
def list_admins(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ This command is only for the bot owner!")
        return
    
    if not ADMIN_USERS:
        bot.reply_to(message, "📭 No admin users configured!")
        return
    
    admin_list = ""
    for i, uid in enumerate(sorted(ADMIN_USERS), 1):
        admin_list += f"│{i}. {uid}\n"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🛡️ ADMIN USERS LIST\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👑 ADMINS ✦ ⟯\n"
        f"{admin_list}"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        f"📊 Total Admins: {len(ADMIN_USERS)}\n\n"
        "✨ Owner only command ✨"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['allow'])
def allow_group(message):
    if not is_owner(message.from_user.id):
        return
    
    try:
        gid = int(message.text.split()[1])
        ALLOWED_GROUP_IDS.add(gid)
        save_json_data(ALLOWED_GROUPS_FILE, list(ALLOWED_GROUP_IDS))
        bot.reply_to(message, f"✅ Group {gid} allowed!")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Usage: /allow group_id")

@bot.message_handler(commands=['addvip'])
def add_vip(message):
    if not is_owner(message.from_user.id):
        return
    
    try:
        uid = int(message.text.split()[1])
        if uid in VIP_USERS:
            bot.reply_to(message, "⚠️ Already VIP!")
            return
        VIP_USERS.add(uid)
        save_json_data(VIP_FILE, list(VIP_USERS))
        bot.reply_to(message, f"✅ User {uid} is now VIP!")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Usage: /addvip user_id")

@bot.message_handler(commands=['removevip'])
def remove_vip(message):
    if not is_owner(message.from_user.id):
        return
    
    try:
        uid = int(message.text.split()[1])
        if uid in VIP_USERS:
            VIP_USERS.discard(uid)
            save_json_data(VIP_FILE, list(VIP_USERS))
            bot.reply_to(message, f"✅ Removed VIP from user {uid}")
        else:
            bot.reply_to(message, f"❌ User {uid} is not VIP")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Usage: /removevip user_id")

@bot.message_handler(commands=['limit'])
def set_daily_limit(message):
    if not is_owner(message.from_user.id):
        return
    
    global DAILY_LIMIT
    try:
        new_limit = int(message.text.split()[1])
        if new_limit < 0:
            bot.reply_to(message, "❌ Limit cannot be negative!")
            return
        old_limit = DAILY_LIMIT
        DAILY_LIMIT = new_limit
        bot.reply_to(message, f"📊 User limit changed from {old_limit} to {DAILY_LIMIT}")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Usage: /limit number")

@bot.message_handler(commands=['glimit'])
def set_group_limit(message):
    if not is_owner(message.from_user.id):
        return
    
    global GROUP_DAILY_LIMIT
    try:
        new_limit = int(message.text.split()[1])
        if new_limit < 0:
            bot.reply_to(message, "❌ Limit cannot be negative!")
            return
        old_limit = GROUP_DAILY_LIMIT
        GROUP_DAILY_LIMIT = new_limit
        bot.reply_to(message, f"👥 Group limit changed from {old_limit} to {GROUP_DAILY_LIMIT}")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Usage: /glimit number")

@bot.message_handler(commands=['limits'])
def show_all_limits(message):
    if not is_owner(message.from_user.id):
        return
    
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    time_suffix = "AM" if auto_hour < 12 else "PM"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    today_bd = datetime.now(BANGLADESH_TZ).date()
    total_users_today = sum(1 for data in like_tracker.values() 
                           if isinstance(data, dict) and data.get("date") == today_bd)
    total_likes_today = sum(data["used"] for data in like_tracker.values() 
                           if isinstance(data, dict) and data.get("date") == today_bd)
    
    total_groups_today = sum(1 for data in GROUP_LIMIT_TRACKER.values() 
                            if isinstance(data, dict) and data.get("date") == today_bd)
    total_group_likes = sum(data["used"] for data in GROUP_LIMIT_TRACKER.values() 
                           if isinstance(data, dict) and data.get("date") == today_bd)
    
    system_status_text = "🟢 ON" if is_like_system_on() else "🔴 OFF"
    
    expiring_soon = 0
    for user_data in AUTO_LIKE_USERS.values():
        for uid_data in user_data.values():
            days_left = get_remaining_days(uid_data.get('expiry_date'))
            if 0 <= days_left <= 3:
                expiring_soon += 1
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│📊 CURRENT LIMITS\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⚙️ LIMITS ✦ ⟯\n"
        f"│👤 User: {DAILY_LIMIT}\n"
        f"│👥 Group: {GROUP_DAILY_LIMIT}\n"
        f"│⏰ Auto: {time_str} (BDT)\n"
        f"│🔘 System: {system_status_text}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📈 TODAY'S STATS ✦ ⟯\n"
        f"│👤 Active Users: {total_users_today}\n"
        f"│❤️ Total Likes: {total_likes_today}\n"
        f"│👥 Active Groups: {total_groups_today}\n"
        f"│👥 Group Likes: {total_group_likes}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 🌟 OTHERS ✦ ⟯\n"
        f"│🌟 VIP: {len(VIP_USERS)}\n"
        f"│🛡️ Admins: {len(ADMIN_USERS)}\n"
        f"│⚡ Auto UIDs: {len(AUTO_LIKE_UIDS)}\n"
        f"│👤 Auto Users: {len(AUTO_LIKE_USERS)}\n"
        f"│⚠️ Expiring Soon: {expiring_soon}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['testapi'])
def test_api_cmd(message):
    if not is_owner(message.from_user.id):
        return
    
    try:
        args = message.text.split()
        uid = args[1] if len(args) > 1 else "2004537688"
        region = args[2].upper() if len(args) > 2 else "BD"
        
        testing = bot.reply_to(message, "🔍 Testing API connection...")
        result = call_api(uid, region)
        
        if result.get("status") == 0:
            text = f"❌ API TEST FAILED\nError: {result.get('error', 'Unknown')}"
        else:
            name = result.get('PlayerNickname', result.get('nickname', 'N/A'))
            likes = result.get('LikesGivenByAPI', result.get('likes_given', result.get('like', 'N/A')))
            text = f"✅ API TEST SUCCESS\n🌍 Region: {region}\n👤 Name: {name}\n🆔 UID: {uid}\n❤️ Likes: {likes}"
        
        bot.edit_message_text(text, testing.chat.id, testing.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ Test error: {e}")

# ================= PERIODIC SAVER =================
def periodic_saver():
    while True:
        time.sleep(3600)
        cleanup_expired_auto_likes()
        save_all_data()
        logger.info("Periodic data save completed")

# ================= MAIN =================
if __name__ == "__main__":
    print("╔════════════════════════════╗")
    print("║   🤖 BOT STARTING...       ║")
    print("╚════════════════════════════╝")
    
    cleanup_expired_auto_likes()
    
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    time_suffix = "AM" if auto_hour < 12 else "PM"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    now_bd = datetime.now(BANGLADESH_TZ)
    
    print(f"📊 Owner ID: {OWNER_ID}")
    print(f"📊 User Daily Limit: {DAILY_LIMIT}")
    print(f"📊 Group Daily Limit: {GROUP_DAILY_LIMIT}")
    print(f"📊 VIP Users: {len(VIP_USERS)}")
    print(f"📊 Admin Users: {len(ADMIN_USERS)}")
    print(f"📊 Auto Like UIDs: {len(AUTO_LIKE_UIDS)}")
    print(f"📊 Auto Like Users: {len(AUTO_LIKE_USERS)}")
    print(f"📊 Allowed Groups: {len(ALLOWED_GROUP_IDS)}")
    print(f"⏰ Auto Task Time: {time_str} Daily (BDT)")
    print(f"🕒 Current Time: {now_bd.strftime('%I:%M %p')} (BDT)")
    print(f"🌏 Timezone: Bangladesh Time (UTC+6)")
    print(f"📢 Channel: {CHANNEL_USERNAME}")
    print(f"👥 Required Group: {REQUIRED_GROUP_USERNAME}")
    print(f"🔘 System Status: {'ON' if is_like_system_on() else 'OFF'}")
    print("=" * 50)
    
    # Start auto scheduler
    scheduler_thread = threading.Thread(target=auto_scheduler, name="AutoScheduler", daemon=True)
    scheduler_thread.start()
    logger.info("✅ Auto scheduler started")
    print("✅ Auto scheduler started")
    
    # Start periodic saver
    saver_thread = threading.Thread(target=periodic_saver, name="DataSaver", daemon=True)
    saver_thread.start()
    logger.info("✅ Periodic saver started")
    print("✅ Periodic saver started")
    
    # Startup message to all task groups
    for group_id in TASK_GROUPS:
        try:
            bot.send_message(
                group_id,
                f"╭━━━━━━━━━━━━━━━✪\n"
                f"│🤖 BOT STARTED\n"
                f"╰━━━━━━━━━━━━━━━✪\n\n"
                f"⏰ Auto Time: {time_str} BDT\n"
                f"📊 Total UIDs: {len(AUTO_LIKE_UIDS)}\n"
                f"👤 Auto Users: {len(AUTO_LIKE_USERS)}\n"
                f"🔘 System: {'ON' if is_like_system_on() else 'OFF'}\n"
                f"🕒 Current: {now_bd.strftime('%I:%M %p')}\n"
                f"🌏 Timezone: Bangladesh (UTC+6)"
            )
        except:
            pass
    
    print("\n🚀 Bot is running! Press Ctrl+C to stop.\n")
    
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        logger.info("Bot stopped by user")
        save_all_data()
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        logger.error(f"Bot crashed: {e}")
        save_all_data()
        time.sleep(5)