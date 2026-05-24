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

API_KEY = "SAIFUL1"
API_BASE_URL = "http://2.56.246.128:30264"

# Supported Regions
SUPPORTED_REGIONS = ["ME", "ID", "TH", "VN", "SG", "BD", "PK", "MY", "PH", "RU", "AFR"]

# Auto Like Time
AUTO_LIKE_HOUR = int(os.getenv("AUTO_LIKE_HOUR", "4"))
AUTO_LIKE_MINUTE = int(os.getenv("AUTO_LIKE_MINUTE", "0"))

# Rate limiting
RATE_LIMIT = 10
REQUEST_TIMEOUT = 30

lock = threading.Lock()
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
            "│🗑️ 𝐄𝐗𝐏𝐈𝐑𝐄𝐃 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄𝐒\n"
            "╰━━━━━━━━━━━━━━━✪\n\n"
            f"📊 𝐓𝐨𝐭𝐚𝐥 𝐄𝐱𝐩𝐢𝐫𝐞𝐝: {removed_count}\n"
            f"👤 𝐀𝐟𝐟𝐞𝐜𝐭𝐞𝐝 𝐔𝐬𝐞𝐫𝐬: {len(expired_notifications)}\n\n"
            "✨ 𝐀𝐮𝐭𝐨 𝐜𝐥𝐞𝐚𝐧𝐮𝐩 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝! ✨"
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
        "│⏰ 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄 𝐄𝐗𝐏𝐈𝐑𝐄𝐃\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ❌ 𝐄𝐗𝐏𝐈𝐑𝐄𝐃 𝐔𝐈𝐃 ✦ ⟯\n"
        f"│🆔 𝐔𝐈𝐃: {uid}\n"
        f"│🌍 𝐑𝐄𝐆𝐈𝐎𝐍: {region}\n"
        f"│📅 𝐀𝐃𝐃𝐄𝐃: {added_date}\n"
        f"│📆 𝐄𝐗𝐏𝐈𝐑𝐄𝐃 𝐎𝐍: {expiry_date}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 💡 𝐑𝐄𝐍𝐄𝐖𝐀𝐋 𝐏𝐀𝐂𝐊𝐀𝐆𝐄𝐒 ✦ ⟯\n"
        "│⚠️ 𝐘𝐨𝐮𝐫 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐡𝐚𝐬 𝐞𝐱𝐩𝐢𝐫𝐞𝐝!\n"
        "│🌟 𝐁𝐮𝐲 𝐚𝐠𝐚𝐢𝐧 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞 𝐬𝐞𝐫𝐯𝐢𝐜𝐞:\n"
        "│   • 30 𝐃𝐚𝐲𝐬 = 30৳\n"
        "│   • 60 𝐃𝐚𝐲𝐬 = 50৳\n"
        "│   • 90 𝐃𝐚𝐲𝐬 = 70৳\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📞 𝐇𝐎𝐖 𝐓𝐎 𝐁𝐔𝐘 ✦ ⟯\n"
        "│📲 𝐈𝐧𝐛𝐨𝐱: @riyadalhasan11\n"
        "│💬 𝐒𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐔𝐈𝐃 𝐚𝐧𝐝 𝐩𝐚𝐜𝐤𝐚𝐠𝐞\n"
        "│✅ 𝐏𝐚𝐲𝐦𝐞𝐧𝐭: 𝐛𝐊𝐚𝐬𝐡/𝐍𝐚𝐠𝐚𝐝/𝐑𝐨𝐜𝐤𝐞𝐭\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨"
    )
    return text

# ================= BOX STYLE RESPONSE FORMATTER (FULL BOLD) =================

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
        "│💝 𝐋𝐈𝐊𝐄 𝐒𝐄𝐍𝐓 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘 ☺️\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 𝐏𝐋𝐀𝐘𝐄𝐑 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
        f"│👤 𝐍𝐀𝐌𝐄 : {name}\n"
        f"│🆔 𝐔𝐈𝐃 : {uid}\n"
        f"│🌍 𝐒𝐄𝐑𝐕𝐄𝐑 : {region}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ❤️ 𝐋𝐈𝐊𝐄 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│➕ 𝐋𝐈𝐊𝐄𝐒 𝐀𝐃𝐃𝐄𝐃 : {likes_given}\n"
        f"│🤡 𝐋𝐈𝐊𝐄𝐒 𝐁𝐄𝐅𝐎𝐑𝐄 : {likes_before}\n"
        f"│🗿 𝐋𝐈𝐊𝐄𝐒 𝐀𝐅𝐓𝐄𝐑 : {likes_after}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│♻️ 𝐑𝐄𝐌𝐀𝐈𝐍𝐒 : ({used}/{total_limit})\n"
        f"│🙋🏻 𝐔𝐒𝐄𝐑 : {user_display}\n"
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
        "│⚠️ 𝐌𝐀𝐗 𝐋𝐈𝐊𝐄𝐒 𝐑𝐄𝐀𝐂𝐇𝐄𝐃 ❌\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 𝐏𝐋𝐀𝐘𝐄𝐑 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
        f"│👤 𝐍𝐀𝐌𝐄 : {name}\n"
        f"│🆔 𝐔𝐈𝐃 : {uid}\n"
        f"│🌍 𝐒𝐄𝐑𝐕𝐄𝐑 : {region}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ❤️ 𝐋𝐈𝐊𝐄 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│🤡 𝐋𝐈𝐊𝐄𝐒 𝐁𝐄𝐅𝐎𝐑𝐄 : {likes_before}\n"
        f"│🗿 𝐋𝐈𝐊𝐄𝐒 𝐀𝐅𝐓𝐄𝐑 : {likes_after}\n"
        f"│📊 𝐒𝐓𝐀𝐓𝐔𝐒 : 𝐌𝐀𝐗 𝐑𝐄𝐀𝐂𝐇𝐄𝐃\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"      
        f"│🙋🏻 𝐔𝐒𝐄𝐑 : {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_error(uid, error_msg, username=None):
    user_display = username if username else "User"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│❌ 𝐄𝐑𝐑𝐎𝐑 𝐎𝐂𝐂𝐔𝐑𝐑𝐄𝐃 ⚠️\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ❌ 𝐄𝐑𝐑𝐎𝐑 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│🆔 𝐔𝐈𝐃 : {uid}\n"
        f"│⚠️ 𝐄𝐑𝐑𝐎𝐑 : {error_msg[:50]}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧 𝐥𝐚𝐭𝐞𝐫! ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│🙋🏻 𝐔𝐒𝐄𝐑 : {user_display}\n"
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
    system_status_text = "🟢 𝐎𝐍" if system_status else "🔴 𝐎𝐅𝐅"
    regions_str = ", ".join(SUPPORTED_REGIONS)
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🤖 𝐑𝐈𝐘𝐀𝐃 𝐎𝐁𝟓𝟐 𝐋𝐈𝐊𝐄 𝐁𝐎𝐓\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
        f"│👤 𝐍𝐀𝐌𝐄 : {user_name}\n"
        f"│👑 𝐒𝐓𝐀𝐓𝐔𝐒 : {user_type}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📋 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ✦ ⟯\n"
        "│• /like <region> <UID> – 𝐒𝐄𝐍𝐃 𝐋𝐈𝐊𝐄\n"
        "│• /remain – 𝐃𝐀𝐈𝐋𝐘 𝐋𝐈𝐌𝐈𝐓\n"
        "│• /myid – 𝐘𝐎𝐔𝐑 𝐈𝐃\n"
        "│• /status – 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐔𝐒\n"
        "│• /myauto – 𝐘𝐎𝐔𝐑 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄𝐒\n"
        "│• /regions – 𝐒𝐔𝐏𝐏𝐎𝐑𝐓𝐄𝐃 𝐑𝐄𝐆𝐈𝐎𝐍𝐒\n"
        "│• /help – 𝐇𝐄𝐋𝐏 𝐌𝐄𝐍𝐔\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⚙️ 𝐋𝐈𝐌𝐈𝐓𝐒 ✦ ⟯\n"
        f"│📊 𝐔𝐒𝐄𝐑 : {daily_limit}/𝐃𝐀𝐘\n"
        f"│👥 𝐆𝐑𝐎𝐔𝐏 : {group_limit}/𝐃𝐀𝐘\n"
        f"│⏰ 𝐀𝐔𝐓𝐎 : {time_str} (𝐁𝐃𝐓)\n"
        f"│🔘 𝐒𝐘𝐒𝐓𝐄𝐌 : {system_status_text}\n"
        f"│🌍 𝐑𝐄𝐆𝐈𝐎𝐍𝐒 : {regions_str}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📢 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃 𝐓𝐎 𝐉𝐎𝐈𝐍 ✦ ⟯\n"
        f"│📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 : {CHANNEL_USERNAME}\n"
        f"│👥 𝐆𝐑𝐎𝐔𝐏 : {REQUIRED_GROUP_USERNAME}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        "│👑 𝐎𝐖𝐍𝐄𝐑 : @riyadalhasan11\n"
        "│🔰 𝐄𝐗𝐀𝐌𝐏𝐋𝐄 : /like BD 123456789\n"
        f"│🙋🏻 𝐔𝐒𝐄𝐑 : {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_remain(user_name, user_type, used, total, group_info="", username=None):
    user_display = username if username else user_name
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│📊 𝐃𝐀𝐈𝐋𝐘 𝐒𝐓𝐀𝐓𝐔𝐒\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
        f"│👤 𝐍𝐀𝐌𝐄 : {user_name}\n"
        f"│👑 𝐒𝐓𝐀𝐓𝐔𝐒 : {user_type}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📊 𝐋𝐈𝐌𝐈𝐓 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│✅ 𝐔𝐒𝐄𝐃 : {used}/{total}\n"
        f"│⏳ 𝐋𝐄𝐅𝐓 : {max(0, total - used) if isinstance(used, int) else '∞'}\n"
        f"{group_info}"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│🙋🏻 𝐔𝐒𝐄𝐑 : {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_myid(user_id, user_name, user_type, username=None):
    user_display = username if username else user_name
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🆔 𝐘𝐎𝐔𝐑 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
        f"│🆔 𝐈𝐃 : {user_id}\n"
        f"│📛 𝐍𝐀𝐌𝐄 : {user_name}\n"
        f"│👑 𝐒𝐓𝐀𝐓𝐔𝐒 : {user_type}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│🙋🏻 𝐔𝐒𝐄𝐑 : {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_processing(uid, region, user_type):
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│⏳ 𝐏𝐑𝐎𝐂𝐄𝐒𝐒𝐈𝐍𝐆...\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
        f"│👤 𝐒𝐓𝐀𝐓𝐔𝐒 : {user_type}\n"
        f"│🆔 𝐔𝐈𝐃 : {uid}\n"
        f"│🌍 𝐑𝐄𝐆𝐈𝐎𝐍 : {region.upper()}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭... ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        "│🙋🏻 𝐔𝐒𝐄𝐑 : 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_auto_time_changed(old_hour, old_min, new_hour, new_min, username=None):
    old_suffix = "𝐀𝐌" if old_hour < 12 else "𝐏𝐌"
    old_display = old_hour if old_hour <= 12 else old_hour - 12
    if old_display == 0:
        old_display = 12
    old_time = f"{old_display}:{old_min:02d} {old_suffix}"
    
    new_suffix = "𝐀𝐌" if new_hour < 12 else "𝐏𝐌"
    new_display = new_hour if new_hour <= 12 else new_hour - 12
    if new_display == 0:
        new_display = 12
    new_time = f"{new_display}:{new_min:02d} {new_suffix}"
    
    user_display = username if username else "𝐎𝐰𝐧𝐞𝐫"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│⏰ 𝐀𝐔𝐓𝐎 𝐓𝐈𝐌𝐄 𝐔𝐏𝐃𝐀𝐓𝐄𝐃\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⏰ 𝐓𝐈𝐌𝐄 𝐂𝐇𝐀𝐍𝐆𝐄 ✦ ⟯\n"
        f"│📊 𝐎𝐋𝐃 : {old_time}\n"
        f"│📊 𝐍𝐄𝐖 : {new_time} (𝐁𝐃𝐓)\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐀𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐰𝐢𝐥𝐥 𝐫𝐮𝐧 𝐚𝐭 𝐭𝐡𝐢𝐬 𝐭𝐢𝐦𝐞 𝐝𝐚𝐢𝐥𝐲! ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│🙋🏻 𝐔𝐒𝐄𝐑 : {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_system_status(user_type, status_on):
    status_text = "🟢 𝐎𝐍" if status_on else "🔴 𝐎𝐅𝐅"
    action = "𝐓𝐔𝐑𝐍𝐄𝐃 𝐎𝐍" if status_on else "𝐓𝐔𝐑𝐍𝐄𝐃 𝐎𝐅𝐅"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        f"│⚙️ 𝐋𝐈𝐊𝐄 𝐒𝐘𝐒𝐓𝐄𝐌 {action}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📊 𝐒𝐓𝐀𝐓𝐔𝐒 ✦ ⟯\n"
        f"│👑 𝐁𝐘 : {user_type}\n"
        f"│🔘 𝐒𝐘𝐒𝐓𝐄𝐌 : {status_text}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐒𝐲𝐬𝐭𝐞𝐦 𝐮𝐩𝐝𝐚𝐭𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲! ✨"
    )
    return text

def format_system_off_message(username=None):
    user_display = username if username else "𝐔𝐬𝐞𝐫"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🔴 𝐒𝐘𝐒𝐓𝐄𝐌 𝐈𝐒 𝐎𝐅𝐅\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⚠️ 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
        "│🔘 𝐓𝐡𝐞 𝐥𝐢𝐤𝐞 𝐬𝐲𝐬𝐭𝐞𝐦 𝐢𝐬 𝐜𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐎𝐅𝐅\n"
        "│⏰ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧 𝐥𝐚𝐭𝐞𝐫\n"
        "│👑 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐨𝐰𝐧𝐞𝐫 𝐟𝐨𝐫 𝐦𝐨𝐫𝐞 𝐢𝐧𝐟𝐨\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐧𝐝𝐞𝐫𝐬𝐭𝐚𝐧𝐝𝐢𝐧𝐠! ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│🙋🏻 𝐔𝐒𝐄𝐑 : {user_display}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    return text

def format_auto_like_list(user_auto_likes):
    if not user_auto_likes:
        return "╭━━━━━━━━━━━━━━━✪\n│📭 𝐍𝐎 𝐀𝐂𝐓𝐈𝐕𝐄 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄𝐒\n╰━━━━━━━━━━━━━━━✪"
    
    today_bd = datetime.now(BANGLADESH_TZ).date()
    text = "╭━━━━━━━━━━━━━━━✪\n│🌟 𝐘𝐎𝐔𝐑 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄𝐒\n╰━━━━━━━━━━━━━━━✪\n\n"
    
    for uid, data in user_auto_likes.items():
        expiry = data.get('expiry_date')
        if isinstance(expiry, str):
            expiry_parts = expiry.split('-')
            expiry = date(int(expiry_parts[0]), int(expiry_parts[1]), int(expiry_parts[2]))
        
        days_left = (expiry - today_bd).days if expiry else 0
        region = data.get('region', 'BD')
        
        if days_left < 0:
            status = "❌ 𝐄𝐗𝐏𝐈𝐑𝐄𝐃"
        elif days_left == 0:
            status = "⚠️ 𝐄𝐗𝐏𝐈𝐑𝐄𝐒 𝐓𝐎𝐃𝐀𝐘"
        elif days_left <= 3:
            status = f"⚠️ {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓"
        else:
            status = f"✅ {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓"
        
        text += f"╭━⟮ 🆔 𝐔𝐈𝐃 : {uid} ⟯\n"
        text += f"│🌍 𝐑𝐄𝐆𝐈𝐎𝐍 : {region}\n"
        text += f"│📅 𝐀𝐃𝐃𝐄𝐃 : {data.get('added_date', 'N/A')}\n"
        text += f"│📆 𝐄𝐗𝐏𝐈𝐑𝐄𝐒 : {expiry}\n"
        text += f"│📊 𝐒𝐓𝐀𝐓𝐔𝐒 : {status}\n"
        text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    return text

def format_all_auto_likes():
    active_likes = get_all_active_auto_likes()
    
    if not active_likes:
        return "╭━━━━━━━━━━━━━━━✪\n│📭 𝐍𝐎 𝐀𝐂𝐓𝐈𝐕𝐄 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄𝐒\n╰━━━━━━━━━━━━━━━✪"
    
    today_bd = datetime.now(BANGLADESH_TZ).date()
    text = "╭━━━━━━━━━━━━━━━✪\n│📋 𝐀𝐋𝐋 𝐀𝐂𝐓𝐈𝐕𝐄 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄𝐒\n╰━━━━━━━━━━━━━━━✪\n\n"
    
    for tg_user_id, uids in active_likes.items():
        text += f"╭━⟮ 👤 𝐓𝐆 𝐔𝐒𝐄𝐑 : {tg_user_id} ⟯\n"
        for uid, data in uids.items():
            expiry = data.get('expiry_date')
            if isinstance(expiry, str):
                expiry_parts = expiry.split('-')
                expiry = date(int(expiry_parts[0]), int(expiry_parts[1]), int(expiry_parts[2]))
            
            days_left = (expiry - today_bd).days if expiry else 0
            region = data.get('region', 'BD')
            
            if days_left < 0:
                status = "𝐄𝐗𝐏𝐈𝐑𝐄𝐃"
            elif days_left == 0:
                status = "𝐄𝐗𝐏𝐈𝐑𝐄𝐒 𝐓𝐎𝐃𝐀𝐘"
            elif days_left <= 3:
                status = f"{days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓 ⚠️"
            else:
                status = f"{days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓 ✅"
            
            text += f"│   🆔 𝐔𝐈𝐃 : {uid}\n"
            text += f"│   🌍 𝐑𝐄𝐆𝐈𝐎𝐍 : {region}\n"
            text += f"│   📅 𝐄𝐗𝐏𝐈𝐑𝐄𝐒 : {expiry} ({status})\n"
        text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    total_uids = sum(len(uids) for uids in active_likes.values())
    text += f"╭━⟮ ✦ 📊 𝐓𝐎𝐓𝐀𝐋 ✦ ⟯\n"
    text += f"│📌 𝐔𝐒𝐄𝐑𝐒 : {len(active_likes)}\n"
    text += f"│📌 𝐔𝐈𝐃𝐬 : {total_uids}\n"
    text += "╰━━━━━━━━━━━━━━━✪"
    
    return text

def format_region_list():
    text = "╭━━━━━━━━━━━━━━━✪\n│🌍 𝐒𝐔𝐏𝐏𝐎𝐑𝐓𝐄𝐃 𝐑𝐄𝐆𝐈𝐎𝐍𝐒\n╰━━━━━━━━━━━━━━━✪\n\n"
    for i, region in enumerate(SUPPORTED_REGIONS, 1):
        text += f"╭━⟮ {i}. {region} ⟯\n"
    text += f"\n╭━⟮ ✦ 📝 𝐔𝐒𝐀𝐆𝐄 ✦ ⟯\n"
    text += f"│📌 /like <region> <UID>\n"
    text += f"│🔰 𝐄𝐗𝐀𝐌𝐏𝐋𝐄 : /like BD 123456789\n"
    text += "╰━━━━━━━━━━━━━━━✪"
    return text

def format_auto_like_dm_box(results):
    now_bd = datetime.now(BANGLADESH_TZ)
    
    text = "╭━━━━━━━━━━━━━━━✪\n"
    text += "│🤖 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄 𝐑𝐄𝐏𝐎𝐑𝐓\n"
    text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    text += "╭━⟮ ✦ ⏰ 𝐓𝐈𝐌𝐄 ✦ ⟯\n"
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
                expiry_status = f"\n│📅 𝐄𝐗𝐏𝐈𝐑𝐘 : 𝐄𝐗𝐏𝐈𝐑𝐄𝐃 ❌"
            elif days_left == 0:
                expiry_status = f"\n│📅 𝐄𝐗𝐏𝐈𝐑𝐘 : 𝐄𝐗𝐏𝐈𝐑𝐄𝐒 𝐓𝐎𝐃𝐀𝐘 ⚠️"
            elif days_left <= 3:
                expiry_status = f"\n│📅 𝐄𝐗𝐏𝐈𝐑𝐘 : {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓 ⚠️"
            else:
                expiry_status = f"\n│📅 𝐄𝐗𝐏𝐈𝐑𝐘 : {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓 ✅"
        
        text += f"\n╭━⟮ 🆔 𝐔𝐈𝐃 : {uid_num} ⟯\n"
        text += f"│🌍 𝐑𝐄𝐆𝐈𝐎𝐍 : {region}\n"
        text += f"│{status_emoji} 𝐒𝐓𝐀𝐓𝐔𝐒 : {status_text}\n"
        text += f"│👤 𝐍𝐀𝐌𝐄 : {name[:35]}\n"
        
        if status == 0:
            error_msg = result_data.get('error', 'Unknown error')[:50]
            text += f"│⚠️ 𝐄𝐑𝐑𝐎𝐑 : {error_msg}\n"
        else:
            text += f"│👍 𝐁𝐄𝐅𝐎𝐑𝐄 : {likes_before}\n"
            text += f"│❤️ 𝐀𝐅𝐓𝐄𝐑 : {likes_after}\n"
            text += f"│➕ 𝐆𝐈𝐕𝐄𝐍 : {likes_given}\n"
        
        if added_date and added_date != 'N/A':
            text += f"│📅 𝐀𝐃𝐃𝐄𝐃 : {added_date}\n"
        if expiry_date:
            text += f"│📆 𝐄𝐗𝐏𝐈𝐑𝐄𝐒 : {expiry_date}"
        text += expiry_status
        text += f"\n╰━━━━━━━━━━━━━━━✪"
    
    text += "\n\n✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨"
    
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
        
        response = requests.get(
            url, 
            params=params, 
            timeout=30,
            verify=False,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"API Response: {data}")
                return data
            except:
                return {"status": 0, "error": "Invalid JSON response"}
        else:
            return {"status": 0, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return {"status": 0, "error": "Cannot connect to API server"}
    except requests.exceptions.Timeout:
        return {"status": 0, "error": "Request timeout"}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": 0, "error": str(e)[:50]}

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
            keyboard.add(InlineKeyboardButton("1️⃣ 𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK))
            keyboard.add(InlineKeyboardButton("2️⃣ 𝐉𝐎𝐈𝐍 𝐆𝐑𝐎𝐔𝐏", url=REQUIRED_GROUP_LINK))
            keyboard.add(InlineKeyboardButton("✅ 𝐕𝐄𝐑𝐈𝐅𝐘", callback_data="check_both_membership"))
            
            channel_status = "✅ 𝐉𝐎𝐈𝐍𝐄𝐃" if channel_ok else "❌ 𝐍𝐎𝐓 𝐉𝐎𝐈𝐍𝐄𝐃"
            group_status = "✅ 𝐉𝐎𝐈𝐍𝐄𝐃" if group_ok else "❌ 𝐍𝐎𝐓 𝐉𝐎𝐈𝐍𝐄𝐃"
            
            msg = (
                "╭━━━━━━━━━━━━━━━✪\n"
                "│🔒 𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 & 𝐆𝐑𝐎𝐔𝐏\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "✨ 𝐂𝐥𝐢𝐜𝐤 𝐭𝐡𝐞 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐛𝐞𝐥𝐨𝐰 ✨\n\n"
                "1️⃣ 𝐅𝐢𝐫𝐬𝐭, 𝐣𝐨𝐢𝐧 𝐭𝐡𝐞 𝐜𝐡𝐚𝐧𝐧𝐞𝐥\n"
                "2️⃣ 𝐓𝐡𝐞𝐧, 𝐣𝐨𝐢𝐧 𝐭𝐡𝐞 𝐠𝐫𝐨𝐮𝐩\n"
                "3️⃣ 𝐅𝐢𝐧𝐚𝐥𝐥𝐲, 𝐜𝐥𝐢𝐜𝐤 𝐕𝐄𝐑𝐈𝐅𝐘\n\n"
                "╭━⟮ ✦ 📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 ✦ ⟯\n"
                f"│📢 𝐍𝐚𝐦𝐞 : {CHANNEL_USERNAME}\n"
                f"│📊 𝐒𝐭𝐚𝐭𝐮𝐬 : {channel_status}\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "╭━⟮ ✦ 👥 𝐆𝐑𝐎𝐔𝐏 ✦ ⟯\n"
                f"│👥 𝐍𝐚𝐦𝐞 : {REQUIRED_GROUP_USERNAME}\n"
                f"│📊 𝐒𝐭𝐚𝐭𝐮𝐬 : {group_status}\n"
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
            bot.answer_callback_query(call.id, "✅ 𝐀𝐂𝐂𝐄𝐒𝐒 𝐆𝐑𝐀𝐍𝐓𝐄𝐃!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
            welcome_text = (
                "╭━━━━━━━━━━━━━━━✪\n"
                "│✅ 𝐀𝐂𝐂𝐄𝐒𝐒 𝐆𝐑𝐀𝐍𝐓𝐄𝐃\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                f"╭━⟮ ✦ 👤 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 ✦ ⟯\n"
                f"│👋 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {call.from_user.first_name}!\n"
                f"│👑 𝐒𝐭𝐚𝐭𝐮𝐬 : {user_type}\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "✨ 𝐘𝐨𝐮 𝐜𝐚𝐧 𝐧𝐨𝐰 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭! ✨\n\n"
                "╭━⟮ ✦ 📢 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃 ✦ ⟯\n"
                "│✅ 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 : 𝐉𝐎𝐈𝐍𝐄𝐃\n"
                "│✅ 𝐆𝐫𝐨𝐮𝐩 : 𝐉𝐎𝐈𝐍𝐄𝐃\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
                "│🔰 𝐔𝐬𝐞 : /like BD UID\n"
                f"│🙋🏻 𝐔𝐬𝐞𝐫 : {get_display_username(call.message)}\n"
                "╰━━━━━━━━━━━━━━━✪"
            )
            
            if user_type == "👤 FREE":
                welcome_text += (
                    "\n\n╭━⟮ ✦ 👑 𝐕𝐈𝐏 𝐎𝐅𝐅𝐄𝐑 ✦ ⟯\n"
                    "│🌟 𝐖𝐚𝐧𝐭 𝐮𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝 𝐥𝐢𝐤𝐞𝐬?\n"
                    "│📲 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 @riyadalhasan11\n"
                    "╰━━━━━━━━━━━━━━━✪"
                )
            
            bot.send_message(call.message.chat.id, welcome_text)
        else:
            channel_status = "✅ 𝐉𝐎𝐈𝐍𝐄𝐃" if channel_ok else "❌ 𝐍𝐎𝐓 𝐉𝐎𝐈𝐍𝐄𝐃"
            group_status = "✅ 𝐉𝐎𝐈𝐍𝐄𝐃" if group_ok else "❌ 𝐍𝐎𝐓 𝐉𝐎𝐈𝐍𝐄𝐃"
            bot.answer_callback_query(call.id, f"𝐂𝐡𝐚𝐧𝐧𝐞𝐥 : {channel_status} | 𝐆𝐫𝐨𝐮𝐩 : {group_status}", show_alert=True)
    
    elif call.data.startswith('broadcast_'):
        handle_broadcast_callback(call)

# ================= HELPERS =================

def get_user_type(user_id):
    if user_id == OWNER_ID:
        return "👑 𝐎𝐖𝐍𝐄𝐑"
    elif user_id in ADMIN_USERS:
        return "🛡️ 𝐀𝐃𝐌𝐈𝐍"
    elif user_id in VIP_USERS:
        return "🌟 𝐕𝐈𝐏"
    else:
        return "👤 𝐅𝐑𝐄𝐄"

def is_allowed(message):
    if message.from_user.id == OWNER_ID or message.from_user.id in ADMIN_USERS:
        return True
    return message.chat.id in ALLOWED_GROUP_IDS

# ================= RATE LIMITING =================
rate_limiter = {}

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
    expired_count = cleanup_expired_auto_likes()
    if expired_count > 0:
        print(f"🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞𝐝 {expired_count} 𝐞𝐱𝐩𝐢𝐫𝐞𝐝 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞𝐬 𝐛𝐞𝐟𝐨𝐫𝐞 𝐭𝐚𝐬𝐤")
    
    now_bd = datetime.now(BANGLADESH_TZ)
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    time_suffix = "𝐀𝐌" if auto_hour < 12 else "𝐏𝐌"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    auto_time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    print(f"\n{'='*60}")
    print(f"📊 𝐀𝐔𝐓𝐎 𝐓𝐀𝐒𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃 𝐚𝐭 {now_bd.strftime('%H:%M:%S')}")
    print(f"⏰ 𝐀𝐮𝐭𝐨 𝐓𝐢𝐦𝐞 : {auto_time_str}")
    print(f"📅 𝐃𝐚𝐭𝐞 : {now_bd.strftime('%d-%m-%Y')}")
    print(f"📊 𝐓𝐨𝐭𝐚𝐥 𝐔𝐈𝐃𝐬 : {len(AUTO_LIKE_UIDS)}")
    print(f"{'='*60}\n")
    
    if not AUTO_LIKE_UIDS:
        for group_id in TASK_GROUPS:
            try:
                bot.send_message(group_id, 
                    "╭━━━━━━━━━━━━━━━✪\n"
                    "│📭 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄 𝐑𝐄𝐏𝐎𝐑𝐓\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    "╭━⟮ ✦ ⏰ 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
                    f"│🕒 𝐀𝐮𝐭𝐨 𝐓𝐢𝐦𝐞 : {auto_time_str}\n"
                    f"│📅 𝐃𝐚𝐭𝐞 : {now_bd.strftime('%d-%m-%Y')}\n"
                    f"│🌏 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞 : 𝐁𝐃𝐓 (𝐔𝐓𝐂+6)\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    "╭━⟮ ✦ 📊 𝐒𝐓𝐀𝐓𝐔𝐒 ✦ ⟯\n"
                    "│📭 𝐀𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐥𝐢𝐬𝐭 𝐢𝐬 𝐄𝐌𝐏𝐓𝐘!\n"
                    "│➡️ 𝐀𝐝𝐝 𝐔𝐈𝐃𝐬 𝐰𝐢𝐭𝐡 /autolike 𝐜𝐨𝐦𝐦𝐚𝐧𝐝\n"
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
                "│⏳ 𝐀𝐔𝐓𝐎 𝐓𝐀𝐒𝐊 𝐈𝐍 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "╭━⟮ ✦ ⏰ 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
                f"│🕒 𝐀𝐮𝐭𝐨 𝐓𝐢𝐦𝐞 : {auto_time_str}\n"
                f"│📅 𝐃𝐚𝐭𝐞 : {now_bd.strftime('%d-%m-%Y')}\n"
                f"│🌏 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞 : 𝐁𝐃𝐓 (𝐔𝐓𝐂+6)\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "╭━⟮ ✦ 📊 𝐏𝐑𝐎𝐂𝐄𝐒𝐒𝐈𝐍𝐆 ✦ ⟯\n"
                f"│📊 𝐓𝐨𝐭𝐚𝐥 𝐔𝐈𝐃𝐬 : {len(AUTO_LIKE_UIDS)}\n"
                f"│🔄 𝐒𝐭𝐚𝐭𝐮𝐬 : 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐞𝐚𝐜𝐡 𝐔𝐈𝐃...\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "✨ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭... ✨"
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
            print(f"   ⚠️ 𝐔𝐈𝐃 {uid} 𝐢𝐬 𝐞𝐱𝐩𝐢𝐫𝐞𝐝 - 𝐬𝐤𝐢𝐩𝐩𝐢𝐧𝐠")
            continue
        
        print(f"[{idx}/{len(uids_to_process)}] 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐔𝐈𝐃 : {uid} (𝐑𝐞𝐠𝐢𝐨𝐧 : {assigned_region})")
        
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
                status_text = "𝐌𝐀𝐗 𝐑𝐄𝐀𝐂𝐇𝐄𝐃"
                given_text = "0"
                max_count += 1
            elif status == 0:
                status_emoji = "❌"
                status_text = "𝐅𝐀𝐈𝐋𝐄𝐃"
                error_msg = res.get('error', 'Unknown error')[:35]
                given_text = "0"
                fail_count += 1
            else:
                status_emoji = "✅"
                status_text = "𝐒𝐔𝐂𝐂𝐄𝐒𝐒"
                given_text = str(likes_given)
                success_count += 1
            
            expiry_status = ""
            if days_left is not None:
                if days_left < 0:
                    expiry_status = f"\n│📅 𝐄𝐗𝐏𝐈𝐑𝐘 : 𝐄𝐗𝐏𝐈𝐑𝐄𝐃 ❌"
                elif days_left == 0:
                    expiry_status = f"\n│📅 𝐄𝐗𝐏𝐈𝐑𝐘 : 𝐄𝐗𝐏𝐈𝐑𝐄𝐒 𝐓𝐎𝐃𝐀𝐘 ⚠️"
                elif days_left <= 3:
                    expiry_status = f"\n│📅 𝐄𝐗𝐏𝐈𝐑𝐘 : {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓 ⚠️"
                else:
                    expiry_status = f"\n│📅 𝐄𝐗𝐏𝐈𝐑𝐘 : {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓 ✅"
            
            result_text = (
                f"\n╭━⟮ 🆔 𝐔𝐈𝐃 : {uid_num} ⟯\n"
                f"│🌍 𝐑𝐄𝐆𝐈𝐎𝐍 : {region}\n"
                f"│{status_emoji} 𝐒𝐓𝐀𝐓𝐔𝐒 : {status_text}\n"
                f"│👤 𝐍𝐀𝐌𝐄 : {name[:35]}\n"
                f"│👍 𝐁𝐄𝐅𝐎𝐑𝐄 : {likes_before}\n"
                f"│❤️ 𝐀𝐅𝐓𝐄𝐑 : {likes_after}\n"
                f"│➕ 𝐆𝐈𝐕𝐄𝐍 : {given_text}"
            )
            
            if status == 0:
                result_text += f"\n│⚠️ 𝐄𝐑𝐑𝐎𝐑 : {error_msg}"
            
            if added_date and added_date != 'N/A':
                result_text += f"\n│📅 𝐀𝐃𝐃𝐄𝐃 : {added_date}"
            if expiry_date:
                result_text += f"\n│📆 𝐄𝐗𝐏𝐈𝐑𝐄𝐒 : {expiry_date}"
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
                f"\n╭━⟮ 🆔 𝐔𝐈𝐃 : {uid} ⟯\n"
                f"│❌ 𝐒𝐓𝐀𝐓𝐔𝐒 : 𝐄𝐑𝐑𝐎𝐑\n"
                f"│⚠️ 𝐄𝐑𝐑𝐎𝐑 : {str(e)[:50]}\n"
                f"╰━━━━━━━━━━━━━━━✪"
            )
            all_results.append(result_text)
            print(f"   ❌ 𝐄𝐑𝐑𝐎𝐑 - {str(e)[:40]}")
            
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
                    "status_text": "𝐄𝐑𝐑𝐎𝐑",
                    "status_emoji": "❌"
                })
    
    total = len(uids_to_process)
    success_rate = (success_count / total * 100) if total > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"📊 𝐀𝐔𝐓𝐎 𝐓𝐀𝐒𝐊 𝐒𝐔𝐌𝐌𝐀𝐑𝐘")
    print(f"📌 𝐓𝐨𝐭𝐚𝐥 𝐔𝐈𝐃𝐬 : {total}")
    print(f"✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬 : {success_count}")
    print(f"⚠️ 𝐌𝐚𝐱 𝐑𝐞𝐚𝐜𝐡𝐞𝐝 : {max_count}")
    print(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝 : {fail_count}")
    print(f"📈 𝐒𝐮𝐜𝐜𝐞𝐬𝐬 𝐑𝐚𝐭𝐞 : {success_rate:.1f}%")
    print(f"{'='*60}\n")
    
    report = "╭━━━━━━━━━━━━━━━✪\n"
    report += "│📋 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄 𝐓𝐀𝐒𝐊 𝐑𝐄𝐏𝐎𝐑𝐓\n"
    report += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    report += "╭━⟮ ✦ ⏰ 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
    report += f"│🕒 𝐀𝐮𝐭𝐨 𝐓𝐢𝐦𝐞 : {auto_time_str}\n"
    report += f"│📅 𝐃𝐚𝐭𝐞 : {now_bd.strftime('%d-%m-%Y')}\n"
    report += f"│🌏 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞 : 𝐁𝐃𝐓 (𝐔𝐓𝐂+6)\n"
    report += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    report += "╭━⟮ ✦ 📊 𝐒𝐔𝐌𝐌𝐀𝐑𝐘 ✦ ⟯\n"
    report += f"│📌 𝐓𝐨𝐭𝐚𝐥 𝐔𝐈𝐃𝐬 : {total}\n"
    report += f"│✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬 : {success_count}\n"
    report += f"│⚠️ 𝐌𝐚𝐱 𝐑𝐞𝐚𝐜𝐡𝐞𝐝 : {max_count}\n"
    report += f"│❌ 𝐅𝐚𝐢𝐥𝐞𝐝 : {fail_count}\n"
    report += f"│📈 𝐒𝐮𝐜𝐜𝐞𝐬𝐬 𝐑𝐚𝐭𝐞 : {success_rate:.1f}%\n"
    report += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    if region_stats:
        report += "╭━⟮ ✦ 🌍 𝐑𝐄𝐆𝐈𝐎𝐍 𝐒𝐓𝐀𝐓𝐒 ✦ ⟯\n"
        for region, count in sorted(region_stats.items(), key=lambda x: x[1], reverse=True):
            report += f"│{region} : {count}\n"
        report += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    report += "╭━⟮ ✦ 🔍 𝐃𝐄𝐓𝐀𝐈𝐋𝐄𝐃 𝐑𝐄𝐒𝐔𝐋𝐓𝐒 ✦ ⟯\n"
    for res in all_results:
        report += res
    report += "\n╰━━━━━━━━━━━━━━━✪\n\n"
    report += "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨\n\n"
    report += "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
    report += "│🤖 𝐁𝐨𝐭 : @riyadob52likebot\n"
    report += "│👑 𝐎𝐰𝐧𝐞𝐫 : @riyadalhasan11\n"
    report += "╰━━━━━━━━━━━━━━━✪"
    
    for group_id, msg_id in processing_messages:
        try:
            bot.edit_message_text(report, group_id, msg_id, parse_mode=None)
            print(f"✅ 𝐑𝐞𝐩𝐨𝐫𝐭 𝐬𝐞𝐧𝐭 𝐭𝐨 𝐠𝐫𝐨𝐮𝐩 : {group_id}")
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
                print(f"✅ 𝐑𝐞𝐩𝐨𝐫𝐭 𝐬𝐞𝐧𝐭 𝐭𝐨 𝐠𝐫𝐨𝐮𝐩 : {group_id} (𝐚𝐬 𝐧𝐞𝐰 𝐦𝐞𝐬𝐬𝐚𝐠𝐞)")
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
            print(f"📨 𝐃𝐌 𝐬𝐞𝐧𝐭 𝐭𝐨 𝐮𝐬𝐞𝐫 {tg_user_id} ({len(results)} 𝐫𝐞𝐩𝐨𝐫𝐭𝐬)")
            time.sleep(0.5)
        except Exception as e:
            dm_failed += 1
            logger.error(f"Failed to send DM to {tg_user_id}: {e}")
    
    summary_report = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│📊 𝐀𝐔𝐓𝐎 𝐓𝐀𝐒𝐊 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        f"📌 𝐓𝐨𝐭𝐚𝐥 : {total}\n"
        f"✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬 : {success_count}\n"
        f"⚠️ 𝐌𝐚𝐱 : {max_count}\n"
        f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝 : {fail_count}\n"
        f"📈 𝐑𝐚𝐭𝐞 : {success_rate:.1f}%\n\n"
        f"📨 𝐃𝐌 𝐒𝐞𝐧𝐭 : {dm_sent} 𝐮𝐬𝐞𝐫𝐬\n"
        f"❌ 𝐃𝐌 𝐅𝐚𝐢𝐥𝐞𝐝 : {dm_failed}\n\n"
        "✨ 𝐓𝐚𝐬𝐤 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲! ✨"
    )
    bot.send_message(OWNER_ID, summary_report)
    
    save_all_data()
    print(f"✅ 𝐀𝐮𝐭𝐨 𝐭𝐚𝐬𝐤 𝐟𝐮𝐥𝐥𝐲 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝 𝐚𝐭 {now_bd.strftime('%H:%M:%S')}")

# ================= AUTO LIKE SCHEDULER =================
def auto_scheduler():
    global auto_time_data
    last_run_date = None
    error_count = 0
    check_count = 0
    
    print("\n🕐 𝐀𝐔𝐓𝐎 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄𝐑 𝐒𝐓𝐀𝐑𝐓𝐄𝐃")
    print("⏰ 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 𝐞𝐯𝐞𝐫𝐲 30 𝐬𝐞𝐜𝐨𝐧𝐝𝐬 𝐟𝐨𝐫 𝐬𝐜𝐡𝐞𝐝𝐮𝐥𝐞𝐝 𝐭𝐢𝐦𝐞\n")
    
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
                print(f"⏰ [{now_bd.strftime('%H:%M:%S')}] 𝐒𝐜𝐡𝐞𝐝𝐮𝐥𝐞𝐫 𝐂𝐡𝐞𝐜𝐤 #{check_count} - 𝐓𝐚𝐫𝐠𝐞𝐭 : {auto_hour:02d}:{auto_min:02d} | 𝐔𝐈𝐃𝐬 : {len(AUTO_LIKE_UIDS)}")
            
            if current_hour == auto_hour and current_minute == auto_min:
                if last_run_date != now_bd.date():
                    print(f"\n{'='*60}")
                    print(f"✅✅✅ 𝐀𝐔𝐓𝐎 𝐓𝐀𝐒𝐊 𝐓𝐑𝐈𝐆𝐆𝐄𝐑𝐄𝐃 𝐚𝐭 {now_bd.strftime('%H:%M:%S')} ✅✅✅")
                    print(f"📅 𝐃𝐚𝐭𝐞 : {now_bd.strftime('%Y-%m-%d')}")
                    print(f"🎯 𝐓𝐚𝐫𝐠𝐞𝐭 𝐓𝐢𝐦𝐞 : {auto_hour:02d}:{auto_min:02d}")
                    print(f"📊 𝐔𝐈𝐃𝐬 𝐭𝐨 𝐩𝐫𝐨𝐜𝐞𝐬𝐬 : {len(AUTO_LIKE_UIDS)}")
                    print(f"{'='*60}\n")
                    logger.info(f"✅ 𝐀𝐔𝐓𝐎 𝐓𝐀𝐒𝐊 𝐓𝐑𝐈𝐆𝐆𝐄𝐑𝐄𝐃 𝐚𝐭 {now_bd.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    try:
                        if AUTO_LIKE_UIDS:
                            send_auto_task()
                        else:
                            print(f"⚠️ 𝐍𝐨 𝐔𝐈𝐃𝐬 𝐢𝐧 𝐚𝐮𝐭𝐨 𝐥𝐢𝐬𝐭 - 𝐬𝐤𝐢𝐩𝐩𝐢𝐧𝐠")
                            for group_id in TASK_GROUPS:
                                try:
                                    bot.send_message(group_id, 
                                        "╭━━━━━━━━━━━━━━━✪\n"
                                        "│⚠️ 𝐀𝐔𝐓𝐎 𝐓𝐀𝐒𝐊 𝐒𝐊𝐈𝐏𝐏𝐄𝐃\n"
                                        "╰━━━━━━━━━━━━━━━✪\n\n"
                                        f"⏰ 𝐓𝐢𝐦𝐞 : {auto_hour:02d}:{auto_min:02d}\n"
                                        f"📅 𝐃𝐚𝐭𝐞 : {now_bd.strftime('%d-%m-%Y')}\n\n"
                                        "📭 𝐍𝐨 𝐔𝐈𝐃𝐬 𝐢𝐧 𝐚𝐮𝐭𝐨 𝐥𝐢𝐬𝐭!\n"
                                        "➡️ 𝐀𝐝𝐝 𝐔𝐈𝐃𝐬 𝐰𝐢𝐭𝐡 /autolike 𝐜𝐨𝐦𝐦𝐚𝐧𝐝"
                                    )
                                except:
                                    pass
                        
                        last_run_date = now_bd.date()
                        error_count = 0
                        save_all_data()
                        
                        print(f"✅ 𝐋𝐚𝐬𝐭 𝐫𝐮𝐧 𝐝𝐚𝐭𝐞 𝐮𝐩𝐝𝐚𝐭𝐞𝐝 𝐭𝐨 : {last_run_date}")
                        print(f"⏱️ 𝐖𝐚𝐢𝐭𝐢𝐧𝐠 2 𝐦𝐢𝐧𝐮𝐭𝐞𝐬 𝐭𝐨 𝐚𝐯𝐨𝐢𝐝 𝐝𝐮𝐩𝐥𝐢𝐜𝐚𝐭𝐞 𝐫𝐮𝐧𝐬...\n")
                        
                        time.sleep(120)
                        
                    except Exception as e:
                        logger.error(f"❌ 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐚𝐮𝐭𝐨 𝐭𝐚𝐬𝐤 𝐞𝐱𝐞𝐜𝐮𝐭𝐢𝐨𝐧 : {e}")
                        print(f"❌❌❌ 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐚𝐮𝐭𝐨 𝐭𝐚𝐬𝐤 𝐞𝐱𝐞𝐜𝐮𝐭𝐢𝐨𝐧 : {e}")
                        error_count += 1
                        
                        if error_count > 3:
                            print("⚠️ 𝐌𝐮𝐥𝐭𝐢𝐩𝐥𝐞 𝐞𝐫𝐫𝐨𝐫𝐬 𝐝𝐞𝐭𝐞𝐜𝐭𝐞𝐝, 𝐰𝐚𝐢𝐭𝐢𝐧𝐠 5 𝐦𝐢𝐧𝐮𝐭𝐞𝐬...")
                            time.sleep(300)
            
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ 𝐂𝐫𝐢𝐭𝐢𝐜𝐚𝐥 𝐞𝐫𝐫𝐨𝐫 𝐢𝐧 𝐚𝐮𝐭𝐨_𝐬𝐜𝐡𝐞𝐝𝐮𝐥𝐞𝐫 : {e}")
            print(f"❌❌❌ 𝐂𝐑𝐈𝐓𝐈𝐂𝐀𝐋 𝐄𝐑𝐑𝐎𝐑 : {e}")
            error_count += 1
            time.sleep(60)

# ================= COMMAND HANDLERS =================

@bot.message_handler(commands=['start'])
@both_required
def start_cmd(message):
    if not is_allowed(message) and message.from_user.id != OWNER_ID:
        bot.reply_to(message, 
            "╭━━━━━━━━━━━━━━━✪\n"
            "│❌ 𝐍𝐎𝐓 𝐀𝐋𝐋𝐎𝐖𝐄𝐃\n"
            "╰━━━━━━━━━━━━━━━✪\n\n"
            "❌ 𝐓𝐡𝐢𝐬 𝐛𝐨𝐭 𝐰𝐨𝐫𝐤𝐬 𝐨𝐧𝐥𝐲 𝐢𝐧 𝐚𝐥𝐥𝐨𝐰𝐞𝐝 𝐠𝐫𝐨𝐮𝐩𝐬!"
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
        InlineKeyboardButton("📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK),
        InlineKeyboardButton("👥 𝐆𝐑𝐎𝐔𝐏", url=REQUIRED_GROUP_LINK)
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
    time_suffix = "𝐀𝐌" if auto_hour < 12 else "𝐏𝐌"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    system_status = "🟢 𝐎𝐍" if is_like_system_on() else "🔴 𝐎𝐅𝐅"
    regions_str = ", ".join(SUPPORTED_REGIONS)
    
    if is_admin(message.from_user.id):
        text = (
            "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n"
            f"│{user_type} 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐋𝐈𝐒𝐓\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 👤 𝐔𝐒𝐄𝐑 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ✦ ⟯\n"
            "│📌 /like <region> <UID> – 𝐒𝐞𝐧𝐝 𝐥𝐢𝐤𝐞𝐬 𝐭𝐨 𝐚𝐧𝐲 𝐔𝐈𝐃\n"
            "│📌 /remain – 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐝𝐚𝐢𝐥𝐲 𝐫𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠 𝐥𝐢𝐦𝐢𝐭\n"
            "│📌 /myid – 𝐆𝐞𝐭 𝐲𝐨𝐮𝐫 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐈𝐃\n"
            "│📌 /status – 𝐂𝐡𝐞𝐜𝐤 𝐛𝐨𝐭 𝐬𝐭𝐚𝐭𝐮𝐬 𝐚𝐧𝐝 𝐬𝐭𝐚𝐭𝐢𝐬𝐭𝐢𝐜𝐬\n"
            "│📌 /myauto – 𝐕𝐢𝐞𝐰 𝐲𝐨𝐮𝐫 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐥𝐢𝐬𝐭 𝐰𝐢𝐭𝐡 𝐞𝐱𝐩𝐢𝐫𝐲\n"
            "│📌 /regions – 𝐒𝐡𝐨𝐰 𝐚𝐥𝐥 𝐬𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝 𝐫𝐞𝐠𝐢𝐨𝐧𝐬\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 👑 𝐀𝐃𝐌𝐈𝐍/𝐎𝐖𝐍𝐄𝐑 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ✦ ⟯\n"
            "│📌 /task – 𝐕𝐢𝐞𝐰 𝐚𝐮𝐭𝐨 𝐭𝐚𝐬𝐤 𝐢𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧\n"
            "│📌 /autolike list – 𝐋𝐢𝐬𝐭 𝐚𝐥𝐥 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞𝐬 𝐰𝐢𝐭𝐡 𝐞𝐱𝐩𝐢𝐫𝐲\n"
            "│📌 /autolike <days> <uid> <tg_userid> [region] – 𝐀𝐝𝐝 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞\n"
            "│📌 /removeauto <uid> <tg_userid> – 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞\n"
            "│📌 /listauto – 𝐋𝐢𝐬𝐭 𝐚𝐥𝐥 𝐚𝐜𝐭𝐢𝐯𝐞 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞𝐬\n"
            "│📌 /userauto <tg_userid> – 𝐂𝐡𝐞𝐜𝐤 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞𝐬 𝐟𝐨𝐫 𝐚 𝐮𝐬𝐞𝐫\n"
            "│📌 /alt <time> – 𝐂𝐡𝐚𝐧𝐠𝐞 𝐚𝐮𝐭𝐨 𝐭𝐚𝐬𝐤 𝐭𝐢𝐦𝐞\n"
            "│📌 /scheduler – 𝐂𝐡𝐞𝐜𝐤 𝐬𝐜𝐡𝐞𝐝𝐮𝐥𝐞𝐫 𝐬𝐭𝐚𝐭𝐮𝐬\n"
            "│📌 /on – 𝐓𝐮𝐫𝐧 𝐥𝐢𝐤𝐞 𝐬𝐲𝐬𝐭𝐞𝐦 𝐎𝐍\n"
            "│📌 /off – 𝐓𝐮𝐫𝐧 𝐥𝐢𝐤𝐞 𝐬𝐲𝐬𝐭𝐞𝐦 𝐎𝐅𝐅\n"
            "│📌 /addadmin <user_id> – 𝐀𝐝𝐝 𝐧𝐞𝐰 𝐚𝐝𝐦𝐢𝐧 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /removeadmin <user_id> – 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚𝐝𝐦𝐢𝐧 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /admins – 𝐋𝐢𝐬𝐭 𝐚𝐥𝐥 𝐚𝐝𝐦𝐢𝐧𝐬 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /allow <group_id> – 𝐀𝐥𝐥𝐨𝐰 𝐚 𝐠𝐫𝐨𝐮𝐩 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /addvip <user_id> – 𝐀𝐝𝐝 𝐕𝐈𝐏 𝐮𝐬𝐞𝐫 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /removevip <user_id> – 𝐑𝐞𝐦𝐨𝐯𝐞 𝐕𝐈𝐏 𝐮𝐬𝐞𝐫 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /limit <number> – 𝐒𝐞𝐭 𝐮𝐬𝐞𝐫 𝐝𝐚𝐢𝐥𝐲 𝐥𝐢𝐦𝐢𝐭 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /glimit <number> – 𝐒𝐞𝐭 𝐠𝐫𝐨𝐮𝐩 𝐝𝐚𝐢𝐥𝐲 𝐥𝐢𝐦𝐢𝐭 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /limits – 𝐒𝐡𝐨𝐰 𝐚𝐥𝐥 𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐥𝐢𝐦𝐢𝐭𝐬 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /testapi [uid] [region] – 𝐓𝐞𝐬𝐭 𝐀𝐏𝐈 𝐜𝐨𝐧𝐧𝐞𝐜𝐭𝐢𝐨𝐧 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "│📌 /broadcast <message> – 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 (𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲)\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ ⚙️ 𝐂𝐔𝐑𝐑𝐄𝐍𝐓 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒 ✦ ⟯\n"
            f"│👤 𝐔𝐒𝐄𝐑 𝐋𝐈𝐌𝐈𝐓 : {DAILY_LIMIT}/𝐝𝐚𝐲\n"
            f"│👥 𝐆𝐑𝐎𝐔𝐏 𝐋𝐈𝐌𝐈𝐓 : {GROUP_DAILY_LIMIT}/𝐝𝐚𝐲\n"
            f"│⏰ 𝐀𝐔𝐓𝐎 𝐓𝐈𝐌𝐄 : {time_str} (𝐁𝐃𝐓)\n"
            f"│🔘 𝐒𝐘𝐒𝐓𝐄𝐌 : {system_status}\n"
            f"│🌍 𝐑𝐄𝐆𝐈𝐎𝐍𝐒 : {regions_str}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 📢 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃 𝐓𝐎 𝐉𝐎𝐈𝐍 ✦ ⟯\n"
            f"│📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 : {CHANNEL_USERNAME}\n"
            f"│👥 𝐆𝐑𝐎𝐔𝐏 : {REQUIRED_GROUP_USERNAME}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨\n\n"
            "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
            f"│🙋🏻 𝐔𝐒𝐄𝐑 : {username}\n"
            "│👑 𝐎𝐖𝐍𝐄𝐑 : @riyadalhasan11\n"
            "│🤖 𝐁𝐎𝐓 : @riyadob52likebot\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪"
        )
    else:
        text = (
            "╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n"
            "│📚 𝐔𝐒𝐄𝐑 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐋𝐈𝐒𝐓\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 📋 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ✦ ⟯\n"
            "│📌 /like <region> <UID> – 𝐒𝐞𝐧𝐝 𝐥𝐢𝐤𝐞𝐬 𝐭𝐨 𝐚𝐧𝐲 𝐔𝐈𝐃\n"
            "│   └─ 𝐄𝐱𝐚𝐦𝐩𝐥𝐞 : /like BD 123456789\n"
            "│\n"
            "│📌 /remain – 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐝𝐚𝐢𝐥𝐲 𝐫𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠 𝐥𝐢𝐦𝐢𝐭\n"
            "│\n"
            "│📌 /myid – 𝐆𝐞𝐭 𝐲𝐨𝐮𝐫 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐈𝐃\n"
            "│\n"
            "│📌 /status – 𝐂𝐡𝐞𝐜𝐤 𝐛𝐨𝐭 𝐬𝐭𝐚𝐭𝐮𝐬 𝐚𝐧𝐝 𝐬𝐭𝐚𝐭𝐢𝐬𝐭𝐢𝐜𝐬\n"
            "│\n"
            "│📌 /myauto – 𝐕𝐢𝐞𝐰 𝐲𝐨𝐮𝐫 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐥𝐢𝐬𝐭\n"
            "│\n"
            "│📌 /regions – 𝐒𝐡𝐨𝐰 𝐚𝐥𝐥 𝐬𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝 𝐫𝐞𝐠𝐢𝐨𝐧𝐬\n"
            "│\n"
            "│📌 /help – 𝐒𝐡𝐨𝐰 𝐭𝐡𝐢𝐬 𝐡𝐞𝐥𝐩 𝐦𝐞𝐧𝐮\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ ⚙️ 𝐂𝐔𝐑𝐑𝐄𝐍𝐓 𝐋𝐈𝐌𝐈𝐓𝐒 ✦ ⟯\n"
            f"│👤 𝐔𝐒𝐄𝐑 𝐋𝐈𝐌𝐈𝐓 : {DAILY_LIMIT} 𝐥𝐢𝐤𝐞𝐬/𝐝𝐚𝐲\n"
            f"│👥 𝐆𝐑𝐎𝐔𝐏 𝐋𝐈𝐌𝐈𝐓 : {GROUP_DAILY_LIMIT} 𝐥𝐢𝐤𝐞𝐬/𝐝𝐚𝐲\n"
            f"│⏰ 𝐀𝐔𝐓𝐎 𝐓𝐈𝐌𝐄 : {time_str} (𝐁𝐃𝐓)\n"
            f"│🔘 𝐒𝐘𝐒𝐓𝐄𝐌 𝐒𝐓𝐀𝐓𝐔𝐒 : {system_status}\n"
            f"│🌍 𝐒𝐔𝐏𝐏𝐎𝐑𝐓𝐄𝐃 𝐑𝐄𝐆𝐈𝐎𝐍𝐒 : {regions_str}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 📢 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃 𝐓𝐎 𝐉𝐎𝐈𝐍 ✦ ⟯\n"
            f"│📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 : {CHANNEL_USERNAME}\n"
            f"│👥 𝐆𝐑𝐎𝐔𝐏 : {REQUIRED_GROUP_USERNAME}\n"
            "│⚠️ 𝐘𝐨𝐮 𝐦𝐮𝐬𝐭 𝐣𝐨𝐢𝐧 𝐛𝐨𝐭𝐡 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭!\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "╭━⟮ ✦ 💡 𝐓𝐈𝐏𝐒 ✦ ⟯\n"
            "│• 𝐔𝐬𝐞 /regions 𝐭𝐨 𝐬𝐞𝐞 𝐚𝐥𝐥 𝐬𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝 𝐫𝐞𝐠𝐢𝐨𝐧𝐬\n"
            "│• 𝐂𝐡𝐞𝐜𝐤 /myauto 𝐭𝐨 𝐬𝐞𝐞 𝐲𝐨𝐮𝐫 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐞𝐱𝐩𝐢𝐫𝐲\n"
            "│• 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐨𝐰𝐧𝐞𝐫 𝐟𝐨𝐫 𝐕𝐈𝐏 𝐛𝐞𝐧𝐞𝐟𝐢𝐭𝐬\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✪\n\n"
            "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨\n\n"
            "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
            f"│🙋🏻 𝐔𝐒𝐄𝐑 : {username}\n"
            "│👑 𝐎𝐖𝐍𝐄𝐑 : @riyadalhasan11\n"
            "│🤖 𝐁𝐎𝐓 : @riyadob52likebot\n"
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
                "│❌ 𝐍𝐎𝐓 𝐀𝐋𝐋𝐎𝐖𝐄𝐃\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "❌ 𝐓𝐡𝐢𝐬 𝐛𝐨𝐭 𝐰𝐨𝐫𝐤𝐬 𝐨𝐧𝐥𝐲 𝐢𝐧 𝐚𝐥𝐥𝐨𝐰𝐞𝐝 𝐠𝐫𝐨𝐮𝐩𝐬!"
            )
            return

        if not check_rate_limit(message.from_user.id):
            bot.reply_to(
                message,
                "╭━━━━━━━━━━━━━━━✪\n"
                "│⚠️ 𝐑𝐀𝐓𝐄 𝐋𝐈𝐌𝐈𝐓\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "⚠️ 𝐓𝐨𝐨 𝐦𝐚𝐧𝐲 𝐫𝐞𝐪𝐮𝐞𝐬𝐭𝐬! 𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭 𝐚 𝐦𝐢𝐧𝐮𝐭𝐞."
            )
            return

        args = message.text.split()

        if len(args) != 3:
            bot.reply_to(
                message,
                "╭━━━━━━━━━━━━━━━✪\n"
                "│⚠️ 𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐅𝐎𝐑𝐌𝐀𝐓\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                f"📌 /like <region> <UID>\n"
                f"🌍 𝐒𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝 : {', '.join(SUPPORTED_REGIONS)}\n"
                "🔰 𝐄𝐱𝐚𝐦𝐩𝐥𝐞 : /like BD 123456789"
            )
            return

        region = args[1].upper()
        uid = args[2]

        if region not in SUPPORTED_REGIONS:
            bot.reply_to(
                message,
                "╭━━━━━━━━━━━━━━━✪\n"
                "│❌ 𝐔𝐍𝐒𝐔𝐏𝐏𝐎𝐑𝐓𝐄𝐃 𝐑𝐄𝐆𝐈𝐎𝐍\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                f"🌍 {region} 𝐢𝐬 𝐧𝐨𝐭 𝐬𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝!\n\n"
                f"✅ 𝐒𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝 : {', '.join(SUPPORTED_REGIONS)}"
            )
            return

        if not uid.isdigit() or len(uid) < 5 or len(uid) > 15:
            bot.reply_to(
                message,
                "╭━━━━━━━━━━━━━━━✪\n"
                "│⚠️ 𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐔𝐈𝐃\n"
                "╰━━━━━━━━━━━━━━━✪\n\n"
                "📏 𝐔𝐈𝐃 𝐦𝐮𝐬𝐭 𝐛𝐞 5-15 𝐝𝐢𝐠𝐢𝐭𝐬"
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
                    "│🚫 𝐃𝐀𝐈𝐋𝐘 𝐋𝐈𝐌𝐈𝐓 𝐑𝐄𝐀𝐂𝐇𝐄𝐃\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    f"📊 𝐔𝐬𝐞𝐝 : {used}/{DAILY_LIMIT}\n\n"
                    "🌟 𝐆𝐞𝐭 𝐕𝐈𝐏 𝐟𝐨𝐫 𝐮𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝 𝐥𝐢𝐤𝐞𝐬!\n"
                    "📲 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 @riyadalhasan11"
                )
                return

        if message.chat.type in ['group', 'supergroup']:
            group_used = get_group_daily_usage(message.chat.id)
            if group_used >= GROUP_DAILY_LIMIT and not is_unlimited(user_id):
                bot.reply_to(
                    message,
                    "╭━━━━━━━━━━━━━━━✪\n"
                    "│🚫 𝐆𝐑𝐎𝐔𝐏 𝐋𝐈𝐌𝐈𝐓 𝐑𝐄𝐀𝐂𝐇𝐄𝐃\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    f"📊 𝐆𝐫𝐨𝐮𝐩 𝐔𝐬𝐞𝐝 : {group_used}/{GROUP_DAILY_LIMIT}"
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
            InlineKeyboardButton("📢 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=CHANNEL_LINK),
            InlineKeyboardButton("👥 𝐆𝐑𝐎𝐔𝐏", url=REQUIRED_GROUP_LINK)
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
            group_info = f"│👥 𝐆𝐑𝐎𝐔𝐏 : {group_used}/{GROUP_DAILY_LIMIT}\n"
        
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
    time_suffix = "𝐀𝐌" if auto_hour < 12 else "𝐏𝐌"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    today_bd = now_bd.date()
    total_users_today = sum(1 for data in like_tracker.values() 
                           if isinstance(data, dict) and data.get("date") == today_bd)
    total_likes_today = sum(data["used"] for data in like_tracker.values() 
                           if isinstance(data, dict) and data.get("date") == today_bd)
    
    system_status_text = "🟢 𝐎𝐍" if is_like_system_on() else "🔴 𝐎𝐅𝐅"
    active_auto = len(get_all_active_auto_likes())
    
    expiring_soon = 0
    for user_data in AUTO_LIKE_USERS.values():
        for uid_data in user_data.values():
            days_left = get_remaining_days(uid_data.get('expiry_date'))
            if 0 <= days_left <= 3:
                expiring_soon += 1
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🤖 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐔𝐒\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👤 𝐘𝐎𝐔𝐑 𝐒𝐓𝐀𝐓𝐔𝐒 ✦ ⟯\n"
        f"│👤 {user_type}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 🤖 𝐁𝐎𝐓 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
        "│✅ 𝐒𝐭𝐚𝐭𝐮𝐬 : 𝐎𝐍𝐋𝐈𝐍𝐄\n"
        f"│👑 𝐎𝐰𝐧𝐞𝐫 : {OWNER_ID}\n"
        f"│📊 𝐔𝐬𝐞𝐫 𝐋𝐢𝐦𝐢𝐭 : {DAILY_LIMIT}\n"
        f"│👥 𝐆𝐫𝐨𝐮𝐩 𝐋𝐢𝐦𝐢𝐭 : {GROUP_DAILY_LIMIT}\n"
        f"│⏰ 𝐀𝐮𝐭𝐨 : {time_str}\n"
        f"│🔘 𝐒𝐲𝐬𝐭𝐞𝐦 : {system_status_text}\n"
        f"│🌏 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞 : 𝐁𝐃𝐓 (𝐔𝐓𝐂+6)\n"
        f"│🌍 𝐑𝐞𝐠𝐢𝐨𝐧𝐬 : {len(SUPPORTED_REGIONS)}\n"
        f"│🌟 𝐕𝐈𝐏 : {len(VIP_USERS)}\n"
        f"│🛡️ 𝐀𝐝𝐦𝐢𝐧𝐬 : {len(ADMIN_USERS)}\n"
        f"│⚡ 𝐀𝐮𝐭𝐨 𝐔𝐈𝐃𝐬 : {len(AUTO_LIKE_UIDS)}\n"
        f"│👤 𝐀𝐮𝐭𝐨 𝐔𝐬𝐞𝐫𝐬 : {active_auto}\n"
        f"│⚠️ 𝐄𝐱𝐩𝐢𝐫𝐢𝐧𝐠 𝐒𝐨𝐨𝐧 : {expiring_soon}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📈 𝐓𝐎𝐃𝐀𝐘'𝐒 𝐒𝐓𝐀𝐓𝐒 ✦ ⟯\n"
        f"│👤 𝐀𝐜𝐭𝐢𝐯𝐞 : {total_users_today}\n"
        f"│❤️ 𝐋𝐢𝐤𝐞𝐬 : {total_likes_today}\n"
        f"│🕒 𝐂𝐮𝐫𝐫𝐞𝐧𝐭 : {now_bd.strftime('%I:%M %p')}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞! ✨\n\n"
        "╭━⟮ ✦ 🧾 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦ ⟯\n"
        f"│🙋🏻 𝐔𝐬𝐞𝐫 : {username}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    
    bot.reply_to(message, text)

# ================= ADMIN/OWNER ONLY COMMANDS =================

@bot.message_handler(commands=['task'])
def task_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐚𝐧𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    
    if not AUTO_LIKE_UIDS:
        bot.reply_to(message, "📭 𝐀𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐥𝐢𝐬𝐭 𝐢𝐬 𝐞𝐦𝐩𝐭𝐲!")
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
    
    time_suffix = "𝐀𝐌" if auto_hour < 12 else "𝐏𝐌"
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
                        expiry_info = " [𝐄𝐗𝐏𝐈𝐑𝐄𝐃]"
                    elif days_left == 0:
                        expiry_info = " [𝐄𝐗𝐏𝐈𝐑𝐄𝐒 𝐓𝐎𝐃𝐀𝐘]"
                    elif days_left <= 3:
                        expiry_info = f" [{days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓]"
                break
        uid_list_text += f"│{i}. {uid} ({region}){expiry_info}\n"
    if len(AUTO_LIKE_UIDS) > 15:
        uid_list_text += f"│... 𝐚𝐧𝐝 {len(AUTO_LIKE_UIDS) - 15} 𝐦𝐨𝐫𝐞\n"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│📋 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⏰ 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄 𝐈𝐍𝐅𝐎 ✦ ⟯\n"
        f"│🕒 𝐀𝐮𝐭𝐨 𝐓𝐢𝐦𝐞 : {time_str} (𝐝𝐚𝐢𝐥𝐲)\n"
        f"│⏳ 𝐍𝐞𝐱𝐭 𝐑𝐮𝐧 : 𝐢𝐧 {hours_until}𝐡 {minutes_until}𝐦\n"
        f"│📊 𝐓𝐨𝐭𝐚𝐥 𝐔𝐈𝐃𝐬 : {len(AUTO_LIKE_UIDS)}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 🆔 𝐔𝐈𝐃 𝐋𝐈𝐒𝐓 ✦ ⟯\n"
        f"{uid_list_text}"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "✨ 𝐀𝐝𝐦𝐢𝐧/𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 ✨"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['autolike'])
def add_auto_like_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐚𝐧𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    
    args = message.text.split()
    
    if len(args) >= 2 and args[1].lower() == 'list':
        show_auto_like_list(message)
        return
    
    if len(args) < 4 or len(args) > 5:
        bot.reply_to(
            message,
            "╭━━━━━━━━━━━━━━━✪\n"
            "│⚠️ 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄 𝐔𝐒𝐀𝐆𝐄\n"
            "╰━━━━━━━━━━━━━━━✪\n\n"
            "📌 /autolike list - 𝐕𝐢𝐞𝐰 𝐚𝐥𝐥 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞𝐬\n\n"
            "📌 /autolike <days> <uid> <tg_user_id> [region]\n\n"
            "🔰 𝐄𝐱𝐚𝐦𝐩𝐥𝐞𝐬:\n"
            "• /autolike 30 123456789 7603719412 BD\n"
            "• /autolike 7 987654321 1234567890 ID\n\n"
            f"🌍 𝐑𝐞𝐠𝐢𝐨𝐧𝐬 : {', '.join(SUPPORTED_REGIONS)}\n"
            "📅 𝐃𝐚𝐲𝐬 : 𝐍𝐮𝐦𝐛𝐞𝐫 𝐨𝐟 𝐝𝐚𝐲𝐬 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐰𝐢𝐥𝐥 𝐰𝐨𝐫𝐤"
        )
        return
    
    try:
        days = int(args[1])
        uid = args[2]
        tg_user_id = int(args[3])
        region = args[4].upper() if len(args) == 5 else "BD"
        
        if days <= 0:
            bot.reply_to(message, "❌ 𝐃𝐚𝐲𝐬 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐠𝐫𝐞𝐚𝐭𝐞𝐫 𝐭𝐡𝐚𝐧 0!")
            return
        
        if not uid.isdigit() or len(uid) < 5 or len(uid) > 15:
            bot.reply_to(message, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐔𝐈𝐃! 𝐌𝐮𝐬𝐭 𝐛𝐞 5-15 𝐝𝐢𝐠𝐢𝐭𝐬.")
            return
        
        if region not in SUPPORTED_REGIONS:
            bot.reply_to(message, f"❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐫𝐞𝐠𝐢𝐨𝐧! 𝐒𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝 : {', '.join(SUPPORTED_REGIONS)}")
            return
        
        success, msg = add_auto_like_for_user(tg_user_id, uid, days, region)
        bot.reply_to(message, msg)
        
        if success:
            try:
                auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
                auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
                time_suffix = "𝐀𝐌" if auto_hour < 12 else "𝐏𝐌"
                display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
                if display_hour == 0:
                    display_hour = 12
                auto_time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
                
                expiry_date = datetime.now(BANGLADESH_TZ).date() + timedelta(days=days)
                
                notify_text = (
                    "╭━━━━━━━━━━━━━━━✪\n"
                    "│✨ 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄 𝐀𝐒𝐒𝐈𝐆𝐍𝐄𝐃\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    f"🆔 𝐔𝐈𝐃 : {uid}\n"
                    f"🌍 𝐑𝐞𝐠𝐢𝐨𝐧 : {region}\n"
                    f"📅 𝐃𝐚𝐲𝐬 : {days}\n"
                    f"📆 𝐄𝐱𝐩𝐢𝐫𝐞𝐬 : {expiry_date}\n"
                    f"⏰ 𝐓𝐢𝐦𝐞 : {auto_time_str} 𝐁𝐃𝐓\n\n"
                    "✨ 𝐀𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐰𝐢𝐥𝐥 𝐫𝐮𝐧 𝐝𝐚𝐢𝐥𝐲!\n"
                    "📊 𝐂𝐡𝐞𝐜𝐤 𝐰𝐢𝐭𝐡 /myauto"
                )
                bot.send_message(tg_user_id, notify_text)
            except:
                pass
                
    except ValueError:
        bot.reply_to(message, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐢𝐧𝐩𝐮𝐭! 𝐃𝐚𝐲𝐬 𝐚𝐧𝐝 𝐔𝐬𝐞𝐫 𝐈𝐃 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐧𝐮𝐦𝐛𝐞𝐫𝐬.")
    except IndexError:
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /autolike <days> <uid> <tg_user_id> [region]")

def show_auto_like_list(message):
    if not AUTO_LIKE_USERS:
        bot.reply_to(message, "📭 𝐍𝐨 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞𝐬 𝐜𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐞𝐝 𝐲𝐞𝐭!\n\n𝐔𝐬𝐞 : /autolike <days> <uid> <tg_user_id> [region]")
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
    text += "│📋 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄 𝐋𝐈𝐒𝐓\n"
    text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    text += "╭━⟮ ✦ 📊 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 ✦ ⟯\n"
    text += f"│📌 𝐓𝐨𝐭𝐚𝐥 𝐔𝐈𝐃𝐬 : {total_uids}\n"
    text += f"│👤 𝐓𝐨𝐭𝐚𝐥 𝐔𝐬𝐞𝐫𝐬 : {len(AUTO_LIKE_USERS)}\n"
    text += f"│⚠️ 𝐄𝐱𝐩𝐢𝐫𝐢𝐧𝐠 𝐬𝐨𝐨𝐧 (≤3 𝐝𝐚𝐲𝐬) : {expiring_soon}\n"
    text += f"│❌ 𝐄𝐱𝐩𝐢𝐫𝐞𝐝 : {expired_count}\n"
    text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    if region_stats:
        text += "╭━⟮ ✦ 🌍 𝐑𝐄𝐆𝐈𝐎𝐍 𝐖𝐈𝐒𝐄 ✦ ⟯\n"
        for region, count in sorted(region_stats.items(), key=lambda x: x[1], reverse=True):
            text += f"│{region} : {count} 𝐔𝐈𝐃(𝐬)\n"
        text += "╰━━━━━━━━━━━━━━━✪\n\n"
    
    text += "╭━⟮ ✦ 📋 𝐃𝐄𝐓𝐀𝐈𝐋𝐄𝐃 𝐋𝐈𝐒𝐓 ✦ ⟯\n"
    
    for tg_user_id, uids in AUTO_LIKE_USERS.items():
        try:
            chat = bot.get_chat(int(tg_user_id))
            user_name = chat.first_name if chat.first_name else f"𝐔𝐬𝐞𝐫 {tg_user_id}"
            if chat.username:
                user_name += f" (@{chat.username})"
        except:
            user_name = f"𝐔𝐬𝐞𝐫 {tg_user_id}"
        
        text += f"\n╭━⟮ 👤 {user_name} ⟯\n"
        text += f"│🆔 𝐈𝐃 : {tg_user_id}\n"
        
        for uid, data in uids.items():
            expiry = data.get('expiry_date')
            days_left = get_remaining_days(expiry) if expiry else None
            region = data.get('region', 'BD')
            added_date = data.get('added_date', 'N/A')
            
            if days_left is not None:
                if days_left < 0:
                    status = "❌ 𝐄𝐗𝐏𝐈𝐑𝐄𝐃"
                elif days_left == 0:
                    status = "⚠️ 𝐄𝐗𝐏𝐈𝐑𝐄𝐒 𝐓𝐎𝐃𝐀𝐘"
                elif days_left <= 3:
                    status = f"⚠️ {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓"
                else:
                    status = f"✅ {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓"
            else:
                status = "✅ 𝐀𝐂𝐓𝐈𝐕𝐄"
            
            text += f"│\n"
            text += f"│   🆔 𝐔𝐈𝐃 : {uid}\n"
            text += f"│   🌍 𝐑𝐞𝐠𝐢𝐨𝐧 : {region}\n"
            text += f"│   📅 𝐀𝐝𝐝𝐞𝐝 : {added_date}\n"
            text += f"│   📆 𝐄𝐱𝐩𝐢𝐫𝐞𝐬 : {expiry}\n"
            text += f"│   📊 𝐒𝐭𝐚𝐭𝐮𝐬 : {status}\n"
            text += f"│   {'─' * 25}\n"
        
        text += "╰━━━━━━━━━━━━━━━✪\n"
    
    text += "\n✨ 𝐔𝐬𝐞 /removeauto <uid> <tg_user_id> 𝐭𝐨 𝐫𝐞𝐦𝐨𝐯𝐞\n"
    text += "📊 𝐔𝐬𝐞𝐫𝐬 𝐜𝐚𝐧 𝐜𝐡𝐞𝐜𝐤 𝐭𝐡𝐞𝐢𝐫 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞𝐬 𝐰𝐢𝐭𝐡 /myauto"
    
    if len(text) > 4096:
        for i in range(0, len(text), 4096):
            bot.send_message(message.chat.id, text[i:i+4096])
    else:
        bot.reply_to(message, text)

@bot.message_handler(commands=['removeauto'])
def remove_auto_like_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐚𝐧𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    
    args = message.text.split()
    
    if len(args) != 3:
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /removeauto <uid> <tg_user_id>")
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
                    "│❌ 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄 𝐑𝐄𝐌𝐎𝐕𝐄𝐃\n"
                    "╰━━━━━━━━━━━━━━━✪\n\n"
                    f"🆔 𝐔𝐈𝐃 : {uid}\n\n"
                    "✨ 𝐀𝐮𝐭𝐨 𝐥𝐢𝐤𝐞 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐫𝐞𝐦𝐨𝐯𝐞𝐝! ✨")
            except:
                pass
    except ValueError:
        bot.reply_to(message, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐓𝐆 𝐔𝐬𝐞𝐫 𝐈𝐃!")

@bot.message_handler(commands=['listauto'])
def list_auto_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐚𝐧𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    
    text = format_all_auto_likes()
    bot.reply_to(message, text)

@bot.message_handler(commands=['userauto'])
def user_auto_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐚𝐧𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /userauto <tg_user_id>")
        return
    
    try:
        tg_user_id = args[1]
        user_auto_likes = get_user_auto_likes(int(tg_user_id))
        
        if not user_auto_likes:
            bot.reply_to(message, f"📭 𝐍𝐨 𝐚𝐮𝐭𝐨 𝐥𝐢𝐤𝐞𝐬 𝐟𝐨𝐮𝐧𝐝 𝐟𝐨𝐫 𝐮𝐬𝐞𝐫 {tg_user_id}")
            return
        
        today_bd = datetime.now(BANGLADESH_TZ).date()
        
        text = f"╭━━━━━━━━━━━━━━━✪\n"
        text += f"│👤 𝐀𝐔𝐓𝐎 𝐋𝐈𝐊𝐄𝐒 𝐅𝐎𝐑 𝐔𝐒𝐄𝐑\n"
        text += f"╰━━━━━━━━━━━━━━━✪\n\n"
        text += f"🆔 𝐔𝐬𝐞𝐫 𝐈𝐃 : {tg_user_id}\n\n"
        
        for uid, data in user_auto_likes.items():
            expiry = data.get('expiry_date')
            days_left = get_remaining_days(expiry) if expiry else None
            region = data.get('region', 'BD')
            
            if days_left is not None:
                if days_left < 0:
                    status = "❌ 𝐄𝐗𝐏𝐈𝐑𝐄𝐃"
                elif days_left == 0:
                    status = "⚠️ 𝐄𝐗𝐏𝐈𝐑𝐄𝐒 𝐓𝐎𝐃𝐀𝐘"
                elif days_left <= 3:
                    status = f"⚠️ {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓"
                else:
                    status = f"✅ {days_left} 𝐃𝐀𝐘𝐒 𝐋𝐄𝐅𝐓"
            else:
                status = "✅ 𝐀𝐂𝐓𝐈𝐕𝐄"
            
            text += f"╭━⟮ 🆔 𝐔𝐈𝐃 : {uid} ⟯\n"
            text += f"│🌍 𝐑𝐞𝐠𝐢𝐨𝐧 : {region}\n"
            text += f"│📅 𝐀𝐝𝐝𝐞𝐝 : {data.get('added_date', 'N/A')}\n"
            text += f"│📆 𝐄𝐱𝐩𝐢𝐫𝐞𝐬 : {expiry}\n"
            text += f"│📊 𝐒𝐭𝐚𝐭𝐮𝐬 : {status}\n"
            text += "╰━━━━━━━━━━━━━━━✪\n\n"
        
        bot.reply_to(message, text)
        
    except ValueError:
        bot.reply_to(message, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐔𝐬𝐞𝐫 𝐈𝐃! 𝐌𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫.")

@bot.message_handler(commands=['alt'])
def auto_time_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐚𝐧𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    
    if len(message.text.split()) < 2:
        bot.reply_to(
            message,
            "╭━━━━━━━━━━━━━━━✪\n"
            "│⏰ 𝐀𝐔𝐓𝐎 𝐓𝐈𝐌𝐄 𝐇𝐄𝐋𝐏\n"
            "╰━━━━━━━━━━━━━━━✪\n\n"
            "📌 /alt 4am   - 𝐒𝐞𝐭 𝐭𝐨 4:00 𝐀𝐌\n"
            "📌 /alt 6pm   - 𝐒𝐞𝐭 𝐭𝐨 6:00 𝐏𝐌\n"
            "📌 /alt 12am  - 𝐒𝐞𝐭 𝐭𝐨 12:00 𝐀𝐌\n"
            "📌 /alt 12pm  - 𝐒𝐞𝐭 𝐭𝐨 12:00 𝐏𝐌\n"
            "📌 /alt 8     - 𝐒𝐞𝐭 𝐭𝐨 8:00 𝐀𝐌"
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
            bot.reply_to(message, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐡𝐨𝐮𝐫! 𝐔𝐬𝐞 0-23")
            return
        
        auto_time_data["hour"] = new_hour
        auto_time_data["minute"] = new_min
        save_json_data(AUTO_TIME_FILE, auto_time_data)
        
        text = format_auto_time_changed(old_hour, old_min, new_hour, new_min, get_display_username(message))
        bot.reply_to(message, text)
        
    except (ValueError, IndexError):
        bot.reply_to(message, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐟𝐨𝐫𝐦𝐚𝐭! 𝐔𝐬𝐞 : /alt 4am, /alt 6pm, /alt 8")

@bot.message_handler(commands=['scheduler'])
def scheduler_check_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐚𝐧𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
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
        "│🤖 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄𝐑 𝐒𝐓𝐀𝐓𝐔𝐒\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        f"📅 𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐓𝐢𝐦𝐞 : {now_bd.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"🌏 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞 : 𝐁𝐚𝐧𝐠𝐥𝐚𝐝𝐞𝐬𝐡 (𝐔𝐓𝐂+6)\n"
        f"⏰ 𝐀𝐮𝐭𝐨 𝐓𝐢𝐦𝐞 : {auto_hour:02d}:{auto_min:02d}\n"
        f"⏳ 𝐍𝐞𝐱𝐭 𝐑𝐮𝐧 : 𝐢𝐧 {hours_until}𝐡 {minutes_until}𝐦\n"
        f"📊 𝐓𝐨𝐭𝐚𝐥 𝐔𝐈𝐃𝐬 : {len(AUTO_LIKE_UIDS)}\n"
        f"👤 𝐀𝐮𝐭𝐨 𝐔𝐬𝐞𝐫𝐬 : {len(AUTO_LIKE_USERS)}\n"
        f"⚠️ 𝐄𝐱𝐩𝐢𝐫𝐢𝐧𝐠 𝐒𝐨𝐨𝐧 : {expiring_soon}\n"
        f"🔄 𝐒𝐜𝐡𝐞𝐝𝐮𝐥𝐞𝐫 𝐓𝐡𝐫𝐞𝐚𝐝 : {'✅ 𝐀𝐥𝐢𝐯𝐞' if scheduler_alive else '❌ 𝐃𝐞𝐚𝐝'}\n"
        f"📢 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 : {CHANNEL_USERNAME}\n"
        f"👥 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝 𝐆𝐫𝐨𝐮𝐩 : {REQUIRED_GROUP_USERNAME}\n"
        "╰━━━━━━━━━━━━━━━✪"
    )
    
    bot.reply_to(message, status_text)

@bot.message_handler(commands=['on'])
def turn_on_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐚𝐧𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    
    if is_like_system_on():
        bot.reply_to(message, "⚠️ 𝐋𝐢𝐤𝐞 𝐬𝐲𝐬𝐭𝐞𝐦 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐎𝐍!")
        return
    
    set_like_system(True)
    text = format_system_status(get_user_type(message.from_user.id), True)
    bot.reply_to(message, text)

@bot.message_handler(commands=['off'])
def turn_off_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫 𝐚𝐧𝐝 𝐚𝐝𝐦𝐢𝐧𝐬!")
        return
    
    if not is_like_system_on():
        bot.reply_to(message, "⚠️ 𝐋𝐢𝐤𝐞 𝐬𝐲𝐬𝐭𝐞𝐦 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐎𝐅𝐅!")
        return
    
    set_like_system(False)
    text = format_system_status(get_user_type(message.from_user.id), False)
    bot.reply_to(message, text)

# ================= ADMIN MANAGEMENT (OWNER ONLY) =================

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫!")
        return
    
    try:
        uid = int(message.text.split()[1])
        if uid == OWNER_ID:
            bot.reply_to(message, "❌ 𝐎𝐰𝐧𝐞𝐫 𝐜𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐚𝐝𝐝𝐞𝐝 𝐚𝐬 𝐚𝐝𝐦𝐢𝐧!")
            return
        if uid in ADMIN_USERS:
            bot.reply_to(message, f"⚠️ 𝐔𝐬𝐞𝐫 {uid} 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚𝐧 𝐚𝐝𝐦𝐢𝐧!")
            return
        ADMIN_USERS.add(uid)
        save_json_data(ADMIN_FILE, list(ADMIN_USERS))
        bot.reply_to(message, f"✅ 𝐔𝐬𝐞𝐫 {uid} 𝐢𝐬 𝐧𝐨𝐰 𝐚𝐧 𝐀𝐃𝐌𝐈𝐍!")
        logger.info(f"Admin added: {uid} by owner {message.from_user.id}")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /addadmin user_id")

@bot.message_handler(commands=['removeadmin'])
def remove_admin(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫!")
        return
    
    try:
        uid = int(message.text.split()[1])
        if uid in ADMIN_USERS:
            ADMIN_USERS.discard(uid)
            save_json_data(ADMIN_FILE, list(ADMIN_USERS))
            bot.reply_to(message, f"✅ 𝐑𝐞𝐦𝐨𝐯𝐞𝐝 𝐚𝐝𝐦𝐢𝐧 𝐟𝐫𝐨𝐦 𝐮𝐬𝐞𝐫 {uid}")
            logger.info(f"Admin removed: {uid} by owner {message.from_user.id}")
        else:
            bot.reply_to(message, f"❌ 𝐔𝐬𝐞𝐫 {uid} 𝐢𝐬 𝐧𝐨𝐭 𝐚𝐧 𝐚𝐝𝐦𝐢𝐧")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /removeadmin user_id")

@bot.message_handler(commands=['admins'])
def list_admins(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐨𝐰𝐧𝐞𝐫!")
        return
    
    if not ADMIN_USERS:
        bot.reply_to(message, "📭 𝐍𝐨 𝐚𝐝𝐦𝐢𝐧 𝐮𝐬𝐞𝐫𝐬 𝐜𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐞𝐝!")
        return
    
    admin_list = ""
    for i, uid in enumerate(sorted(ADMIN_USERS), 1):
        admin_list += f"│{i}. {uid}\n"
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│🛡️ 𝐀𝐃𝐌𝐈𝐍 𝐔𝐒𝐄𝐑𝐒 𝐋𝐈𝐒𝐓\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 👑 𝐀𝐃𝐌𝐈𝐍𝐒 ✦ ⟯\n"
        f"{admin_list}"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        f"📊 𝐓𝐨𝐭𝐚𝐥 𝐀𝐝𝐦𝐢𝐧𝐬 : {len(ADMIN_USERS)}\n\n"
        "✨ 𝐎𝐰𝐧𝐞𝐫 𝐨𝐧𝐥𝐲 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 ✨"
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
        bot.reply_to(message, f"✅ 𝐆𝐫𝐨𝐮𝐩 {gid} 𝐚𝐥𝐥𝐨𝐰𝐞𝐝!")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /allow group_id")

@bot.message_handler(commands=['addvip'])
def add_vip(message):
    if not is_owner(message.from_user.id):
        return
    
    try:
        uid = int(message.text.split()[1])
        if uid in VIP_USERS:
            bot.reply_to(message, "⚠️ 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐕𝐈𝐏!")
            return
        VIP_USERS.add(uid)
        save_json_data(VIP_FILE, list(VIP_USERS))
        bot.reply_to(message, f"✅ 𝐔𝐬𝐞𝐫 {uid} 𝐢𝐬 𝐧𝐨𝐰 𝐕𝐈𝐏!")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /addvip user_id")

@bot.message_handler(commands=['removevip'])
def remove_vip(message):
    if not is_owner(message.from_user.id):
        return
    
    try:
        uid = int(message.text.split()[1])
        if uid in VIP_USERS:
            VIP_USERS.discard(uid)
            save_json_data(VIP_FILE, list(VIP_USERS))
            bot.reply_to(message, f"✅ 𝐑𝐞𝐦𝐨𝐯𝐞𝐝 𝐕𝐈𝐏 𝐟𝐫𝐨𝐦 𝐮𝐬𝐞𝐫 {uid}")
        else:
            bot.reply_to(message, f"❌ 𝐔𝐬𝐞𝐫 {uid} 𝐢𝐬 𝐧𝐨𝐭 𝐕𝐈𝐏")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /removevip user_id")

@bot.message_handler(commands=['limit'])
def set_daily_limit(message):
    if not is_owner(message.from_user.id):
        return
    
    global DAILY_LIMIT
    try:
        new_limit = int(message.text.split()[1])
        if new_limit < 0:
            bot.reply_to(message, "❌ 𝐋𝐢𝐦𝐢𝐭 𝐜𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐧𝐞𝐠𝐚𝐭𝐢𝐯𝐞!")
            return
        old_limit = DAILY_LIMIT
        DAILY_LIMIT = new_limit
        bot.reply_to(message, f"📊 𝐔𝐬𝐞𝐫 𝐥𝐢𝐦𝐢𝐭 𝐜𝐡𝐚𝐧𝐠𝐞𝐝 𝐟𝐫𝐨𝐦 {old_limit} 𝐭𝐨 {DAILY_LIMIT}")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /limit number")

@bot.message_handler(commands=['glimit'])
def set_group_limit(message):
    if not is_owner(message.from_user.id):
        return
    
    global GROUP_DAILY_LIMIT
    try:
        new_limit = int(message.text.split()[1])
        if new_limit < 0:
            bot.reply_to(message, "❌ 𝐋𝐢𝐦𝐢𝐭 𝐜𝐚𝐧𝐧𝐨𝐭 𝐛𝐞 𝐧𝐞𝐠𝐚𝐭𝐢𝐯𝐞!")
            return
        old_limit = GROUP_DAILY_LIMIT
        GROUP_DAILY_LIMIT = new_limit
        bot.reply_to(message, f"👥 𝐆𝐫𝐨𝐮𝐩 𝐥𝐢𝐦𝐢𝐭 𝐜𝐡𝐚𝐧𝐠𝐞𝐝 𝐟𝐫𝐨𝐦 {old_limit} 𝐭𝐨 {GROUP_DAILY_LIMIT}")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /glimit number")

@bot.message_handler(commands=['limits'])
def show_all_limits(message):
    if not is_owner(message.from_user.id):
        return
    
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    time_suffix = "𝐀𝐌" if auto_hour < 12 else "𝐏𝐌"
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
    
    system_status_text = "🟢 𝐎𝐍" if is_like_system_on() else "🔴 𝐎𝐅𝐅"
    
    expiring_soon = 0
    for user_data in AUTO_LIKE_USERS.values():
        for uid_data in user_data.values():
            days_left = get_remaining_days(uid_data.get('expiry_date'))
            if 0 <= days_left <= 3:
                expiring_soon += 1
    
    text = (
        "╭━━━━━━━━━━━━━━━✪\n"
        "│📊 𝐂𝐔𝐑𝐑𝐄𝐍𝐓 𝐋𝐈𝐌𝐈𝐓𝐒\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ ⚙️ 𝐋𝐈𝐌𝐈𝐓𝐒 ✦ ⟯\n"
        f"│👤 𝐔𝐬𝐞𝐫 : {DAILY_LIMIT}\n"
        f"│👥 𝐆𝐫𝐨𝐮𝐩 : {GROUP_DAILY_LIMIT}\n"
        f"│⏰ 𝐀𝐮𝐭𝐨 : {time_str} (𝐁𝐃𝐓)\n"
        f"│🔘 𝐒𝐲𝐬𝐭𝐞𝐦 : {system_status_text}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 📈 𝐓𝐎𝐃𝐀𝐘'𝐒 𝐒𝐓𝐀𝐓𝐒 ✦ ⟯\n"
        f"│👤 𝐀𝐜𝐭𝐢𝐯𝐞 𝐔𝐬𝐞𝐫𝐬 : {total_users_today}\n"
        f"│❤️ 𝐓𝐨𝐭𝐚𝐥 𝐋𝐢𝐤𝐞𝐬 : {total_likes_today}\n"
        f"│👥 𝐀𝐜𝐭𝐢𝐯𝐞 𝐆𝐫𝐨𝐮𝐩𝐬 : {total_groups_today}\n"
        f"│👥 𝐆𝐫𝐨𝐮𝐩 𝐋𝐢𝐤𝐞𝐬 : {total_group_likes}\n"
        "╰━━━━━━━━━━━━━━━✪\n\n"
        "╭━⟮ ✦ 🌟 𝐎𝐓𝐇𝐄𝐑𝐒 ✦ ⟯\n"
        f"│🌟 𝐕𝐈𝐏 : {len(VIP_USERS)}\n"
        f"│🛡️ 𝐀𝐝𝐦𝐢𝐧𝐬 : {len(ADMIN_USERS)}\n"
        f"│⚡ 𝐀𝐮𝐭𝐨 𝐔𝐈𝐃𝐬 : {len(AUTO_LIKE_UIDS)}\n"
        f"│👤 𝐀𝐮𝐭𝐨 𝐔𝐬𝐞𝐫𝐬 : {len(AUTO_LIKE_USERS)}\n"
        f"│⚠️ 𝐄𝐱𝐩𝐢𝐫𝐢𝐧𝐠 𝐒𝐨𝐨𝐧 : {expiring_soon}\n"
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
        
        testing = bot.reply_to(message, "🔍 𝐓𝐞𝐬𝐭𝐢𝐧𝐠 𝐀𝐏𝐈 𝐜𝐨𝐧𝐧𝐞𝐜𝐭𝐢𝐨𝐧...")
        result = call_api(uid, region)
        
        if result.get("status") == 0:
            text = f"❌ 𝐀𝐏𝐈 𝐓𝐄𝐒𝐓 𝐅𝐀𝐈𝐋𝐄𝐃\n𝐄𝐫𝐫𝐨𝐫 : {result.get('error', 'Unknown')}"
        else:
            name = result.get('PlayerNickname', 'N/A')
            likes = result.get('LikesGivenByAPI', 'N/A')
            text = f"✅ 𝐀𝐏𝐈 𝐓𝐄𝐒𝐓 𝐒𝐔𝐂𝐂𝐄𝐒𝐒\n🌍 𝐑𝐞𝐠𝐢𝐨𝐧 : {region}\n👤 𝐍𝐚𝐦𝐞 : {name}\n🆔 𝐔𝐈𝐃 : {uid}\n❤️ 𝐋𝐢𝐤𝐞𝐬 : {likes}"
        
        bot.edit_message_text(text, testing.chat.id, testing.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ 𝐓𝐞𝐬𝐭 𝐞𝐫𝐫𝐨𝐫 : {e}")

# ================= BROADCAST COMMANDS =================

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if not is_owner(message.from_user.id):
        return
    
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /broadcast 𝐘𝐨𝐮𝐫 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐡𝐞𝐫𝐞")
        return
    
    broadcast_text = message.text.split(' ', 1)[1]
    broadcast_id = int(time.time())
    broadcast_data["messages"].append({
        "id": broadcast_id,
        "text": broadcast_text,
        "sender_id": message.from_user.id,
        "time": datetime.now(BANGLADESH_TZ).isoformat(),
        "status": "pending"
    })
    save_json_data(BROADCAST_FILE, broadcast_data)
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ 𝐂𝐎𝐍𝐅𝐈𝐑𝐌", callback_data=f"broadcast_confirm_{broadcast_id}"),
        InlineKeyboardButton("❌ 𝐂𝐀𝐍𝐂𝐄𝐋", callback_data=f"broadcast_cancel_{broadcast_id}"),
        InlineKeyboardButton("👁️ 𝐏𝐑𝐄𝐕𝐈𝐄𝐖", callback_data=f"broadcast_preview_{broadcast_id}")
    )
    
    unique_users = set()
    for user_id in like_tracker.keys():
        if isinstance(user_id, int):
            unique_users.add(user_id)
    for user_id in VIP_USERS:
        unique_users.add(user_id)
    for user_id in ADMIN_USERS:
        unique_users.add(user_id)
    for user_id in AUTO_LIKE_USERS.keys():
        try:
            unique_users.add(int(user_id))
        except:
            pass
    unique_users.add(OWNER_ID)
    
    bot.reply_to(message, f"📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐫𝐞𝐚𝐝𝐲!\n\n𝐌𝐞𝐬𝐬𝐚𝐠𝐞 : {broadcast_text[:100]}\n\n👥 𝐓𝐨𝐭𝐚𝐥 𝐮𝐬𝐞𝐫𝐬 : {len(unique_users)}\n\n𝐂𝐥𝐢𝐜𝐤 𝐂𝐎𝐍𝐅𝐈𝐑𝐌 𝐭𝐨 𝐬𝐞𝐧𝐝", reply_markup=keyboard)

@bot.message_handler(commands=['broadcast_preview'])
def broadcast_preview_cmd(message):
    if not is_owner(message.from_user.id):
        return
    
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ 𝐔𝐬𝐚𝐠𝐞 : /broadcast_preview 𝐘𝐨𝐮𝐫 𝐦𝐞𝐬𝐬𝐚𝐠𝐞")
        return
    
    broadcast_text = message.text.split(' ', 1)[1]
    bot.reply_to(message, f"👁️ 𝐏𝐑𝐄𝐕𝐈𝐄𝐖 :\n\n{broadcast_text}")

@bot.message_handler(commands=['broadcast_stats'])
def broadcast_stats_cmd(message):
    if not is_owner(message.from_user.id):
        return
    
    total_msgs = len(broadcast_data["messages"])
    pending = sum(1 for m in broadcast_data["messages"] if m.get("status") == "pending")
    sent = sum(1 for m in broadcast_data["messages"] if m.get("status") == "sent")
    failed = sum(1 for m in broadcast_data["messages"] if m.get("status") == "failed")
    
    text = f"📊 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐒𝐓𝐀𝐓𝐒\n\n𝐓𝐨𝐭𝐚𝐥 : {total_msgs}\n𝐏𝐞𝐧𝐝𝐢𝐧𝐠 : {pending}\n𝐒𝐞𝐧𝐭 : {sent}\n𝐅𝐚𝐢𝐥𝐞𝐝 : {failed}"
    bot.reply_to(message, text)

@bot.message_handler(commands=['broadcast_cancel'])
def broadcast_cancel_cmd(message):
    if not is_owner(message.from_user.id):
        return
    
    cancelled = 0
    for msg in broadcast_data["messages"]:
        if msg.get("status") == "pending":
            msg["status"] = "cancelled"
            cancelled += 1
    save_json_data(BROADCAST_FILE, broadcast_data)
    bot.reply_to(message, f"✅ 𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝 {cancelled} 𝐩𝐞𝐧𝐝𝐢𝐧𝐠 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭𝐬")

def send_broadcast(broadcast_id):
    broadcast = None
    for msg in broadcast_data["messages"]:
        if msg["id"] == broadcast_id:
            broadcast = msg
            break
    if not broadcast:
        return
    
    unique_users = set()
    for user_id in like_tracker.keys():
        if isinstance(user_id, int):
            unique_users.add(user_id)
    for user_id in VIP_USERS:
        unique_users.add(user_id)
    for user_id in ADMIN_USERS:
        unique_users.add(user_id)
    for user_id in AUTO_LIKE_USERS.keys():
        try:
            unique_users.add(int(user_id))
        except:
            pass
    unique_users.add(OWNER_ID)
    
    broadcast["stats"] = {"total": len(unique_users), "sent": 0, "failed": 0}
    broadcast["status"] = "sending"
    save_json_data(BROADCAST_FILE, broadcast_data)
    
    bot.send_message(OWNER_ID, f"📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐬𝐭𝐚𝐫𝐭𝐞𝐝! 𝐓𝐨𝐭𝐚𝐥 : {len(unique_users)}")
    
    sent_count = 0
    failed_count = 0
    
    for user_id in unique_users:
        try:
            now_bd = datetime.now(BANGLADESH_TZ)
            formatted_msg = f"📢 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐌𝐄𝐒𝐒𝐀𝐆𝐄\n\n{broadcast['text']}\n\n📅 {now_bd.strftime('%d-%m-%Y')} ⏰ {now_bd.strftime('%I:%M %p')} (𝐁𝐃𝐓)"
            bot.send_message(user_id, formatted_msg)
            sent_count += 1
            
            if sent_count % 10 == 0:
                broadcast["stats"]["sent"] = sent_count
                save_json_data(BROADCAST_FILE, broadcast_data)
            time.sleep(0.1)
        except:
            failed_count += 1
    
    broadcast["stats"]["sent"] = sent_count
    broadcast["stats"]["failed"] = failed_count
    broadcast["status"] = "completed"
    save_json_data(BROADCAST_FILE, broadcast_data)
    
    bot.send_message(OWNER_ID, f"✅ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝!\n𝐒𝐞𝐧𝐭 : {sent_count}\n𝐅𝐚𝐢𝐥𝐞𝐝 : {failed_count}\n𝐒𝐮𝐜𝐜𝐞𝐬𝐬 : {(sent_count/len(unique_users)*100):.1f}%")

def handle_broadcast_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "❌ 𝐎𝐧𝐥𝐲 𝐨𝐰𝐧𝐞𝐫 𝐜𝐚𝐧 𝐜𝐨𝐧𝐟𝐢𝐫𝐦!")
        return
    
    action = call.data.split('_')[1]
    broadcast_id = int(call.data.split('_')[2])
    
    if action == "confirm":
        bot.answer_callback_query(call.id, "✅ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐬𝐭𝐚𝐫𝐭𝐞𝐝!")
        bot.edit_message_text("📢 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐒𝐄𝐍𝐃𝐈𝐍𝐆...\n\n𝐒𝐞𝐧𝐝𝐢𝐧𝐠 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐚𝐥𝐥 𝐮𝐬𝐞𝐫𝐬...\n𝐓𝐡𝐢𝐬 𝐦𝐚𝐲 𝐭𝐚𝐤𝐞 𝐚 𝐟𝐞𝐰 𝐦𝐢𝐧𝐮𝐭𝐞𝐬.", call.message.chat.id, call.message.message_id)
        broadcast_thread = threading.Thread(target=send_broadcast, args=(broadcast_id,), daemon=True)
        broadcast_thread.start()
    elif action == "cancel":
        for msg in broadcast_data["messages"]:
            if msg["id"] == broadcast_id:
                msg["status"] = "cancelled"
                break
        save_json_data(BROADCAST_FILE, broadcast_data)
        bot.answer_callback_query(call.id, "❌ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐜𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝!")
        bot.edit_message_text("❌ 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐂𝐀𝐍𝐂𝐄𝐋𝐋𝐄𝐃", call.message.chat.id, call.message.message_id)
    elif action == "preview":
        for msg in broadcast_data["messages"]:
            if msg["id"] == broadcast_id:
                bot.answer_callback_query(call.id, "👁️ 𝐏𝐫𝐞𝐯𝐢𝐞𝐰")
                bot.send_message(call.from_user.id, f"👁️ 𝐏𝐑𝐄𝐕𝐈𝐄𝐖 :\n\n{msg['text']}")
                break

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
    print("║   🤖 𝐁𝐎𝐓 𝐒𝐓𝐀𝐑𝐓𝐈𝐍𝐆...   ║")
    print("╚════════════════════════════╝")
    
    cleanup_expired_auto_likes()
    
    auto_hour = auto_time_data.get("hour", AUTO_LIKE_HOUR)
    auto_min = auto_time_data.get("minute", AUTO_LIKE_MINUTE)
    time_suffix = "𝐀𝐌" if auto_hour < 12 else "𝐏𝐌"
    display_hour = auto_hour if auto_hour <= 12 else auto_hour - 12
    if display_hour == 0:
        display_hour = 12
    time_str = f"{display_hour}:{auto_min:02d} {time_suffix}"
    
    now_bd = datetime.now(BANGLADESH_TZ)
    
    print(f"📊 𝐎𝐰𝐧𝐞𝐫 𝐈𝐃 : {OWNER_ID}")
    print(f"📊 𝐔𝐬𝐞𝐫 𝐃𝐚𝐢𝐥𝐲 𝐋𝐢𝐦𝐢𝐭 : {DAILY_LIMIT}")
    print(f"📊 𝐆𝐫𝐨𝐮𝐩 𝐃𝐚𝐢𝐥𝐲 𝐋𝐢𝐦𝐢𝐭 : {GROUP_DAILY_LIMIT}")
    print(f"📊 𝐕𝐈𝐏 𝐔𝐬𝐞𝐫𝐬 : {len(VIP_USERS)}")
    print(f"📊 𝐀𝐝𝐦𝐢𝐧 𝐔𝐬𝐞𝐫𝐬 : {len(ADMIN_USERS)}")
    print(f"📊 𝐀𝐮𝐭𝐨 𝐋𝐢𝐤𝐞 𝐔𝐈𝐃𝐬 : {len(AUTO_LIKE_UIDS)}")
    print(f"📊 𝐀𝐮𝐭𝐨 𝐋𝐢𝐤𝐞 𝐔𝐬𝐞𝐫𝐬 : {len(AUTO_LIKE_USERS)}")
    print(f"📊 𝐀𝐥𝐥𝐨𝐰𝐞𝐝 𝐆𝐫𝐨𝐮𝐩𝐬 : {len(ALLOWED_GROUP_IDS)}")
    print(f"⏰ 𝐀𝐮𝐭𝐨 𝐓𝐚𝐬𝐤 𝐓𝐢𝐦𝐞 : {time_str} 𝐃𝐚𝐢𝐥𝐲 (𝐁𝐃𝐓)")
    print(f"🕒 𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐓𝐢𝐦𝐞 : {now_bd.strftime('%I:%M %p')} (𝐁𝐃𝐓)")
    print(f"🌏 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞 : 𝐁𝐚𝐧𝐠𝐥𝐚𝐝𝐞𝐬𝐡 𝐓𝐢𝐦𝐞 (𝐔𝐓𝐂+6)")
    print(f"📢 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 : {CHANNEL_USERNAME}")
    print(f"👥 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝 𝐆𝐫𝐨𝐮𝐩 : {REQUIRED_GROUP_USERNAME}")
    print(f"🔘 𝐒𝐲𝐬𝐭𝐞𝐦 𝐒𝐭𝐚𝐭𝐮𝐬 : {'𝐎𝐍' if is_like_system_on() else '𝐎𝐅𝐅'}")
    print("📋 𝐓𝐚𝐬𝐤 𝐆𝐫𝐨𝐮𝐩𝐬 :")
    for i, group_id in enumerate(TASK_GROUPS, 1):
        print(f"   {i}. {group_id}")
    print("=" * 50)
    
    # Start auto scheduler
    scheduler_thread = threading.Thread(target=auto_scheduler, name="AutoScheduler", daemon=True)
    scheduler_thread.start()
    logger.info("✅ Auto scheduler started")
    print("✅ 𝐀𝐮𝐭𝐨 𝐬𝐜𝐡𝐞𝐝𝐮𝐥𝐞𝐫 𝐬𝐭𝐚𝐫𝐭𝐞𝐝")
    
    # Start periodic saver
    saver_thread = threading.Thread(target=periodic_saver, name="DataSaver", daemon=True)
    saver_thread.start()
    logger.info("✅ Periodic saver started")
    print("✅ 𝐏𝐞𝐫𝐢𝐨𝐝𝐢𝐜 𝐬𝐚𝐯𝐞𝐫 𝐬𝐭𝐚𝐫𝐭𝐞𝐝")
    
    # Startup message to all task groups
    for group_id in TASK_GROUPS:
        try:
            bot.send_message(
                group_id,
                f"╭━━━━━━━━━━━━━━━✪\n"
                f"│🤖 𝐁𝐎𝐓 𝐒𝐓𝐀𝐑𝐓𝐄𝐃\n"
                f"╰━━━━━━━━━━━━━━━✪\n\n"
                f"⏰ 𝐀𝐮𝐭𝐨 𝐓𝐢𝐦𝐞 : {time_str} 𝐁𝐃𝐓\n"
                f"📊 𝐓𝐨𝐭𝐚𝐥 𝐔𝐈𝐃𝐬 : {len(AUTO_LIKE_UIDS)}\n"
                f"👤 𝐀𝐮𝐭𝐨 𝐔𝐬𝐞𝐫𝐬 : {len(AUTO_LIKE_USERS)}\n"
                f"🔘 𝐒𝐲𝐬𝐭𝐞𝐦 : {'𝐎𝐍' if is_like_system_on() else '𝐎𝐅𝐅'}\n"
                f"🕒 𝐂𝐮𝐫𝐫𝐞𝐧𝐭 : {now_bd.strftime('%I:%M %p')}\n"
                f"🌏 𝐓𝐢𝐦𝐞𝐳𝐨𝐧𝐞 : 𝐁𝐚𝐧𝐠𝐥𝐚𝐝𝐞𝐬𝐡 (𝐔𝐓𝐂+6)"
            )
        except:
            pass
    
    print("\n🚀 𝐁𝐨𝐭 𝐢𝐬 𝐫𝐮𝐧𝐧𝐢𝐧𝐠! 𝐏𝐫𝐞𝐬𝐬 𝐂𝐭𝐫𝐥+𝐂 𝐭𝐨 𝐬𝐭𝐨𝐩.\n")
    
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n👋 𝐁𝐨𝐭 𝐬𝐭𝐨𝐩𝐩𝐞𝐝 𝐛𝐲 𝐮𝐬𝐞𝐫")
        logger.info("Bot stopped by user")
        save_all_data()
    except Exception as e:
        print(f"❌ 𝐁𝐨𝐭 𝐜𝐫𝐚𝐬𝐡𝐞𝐝 : {e}")
        logger.error(f"Bot crashed: {e}")
        save_all_data()
        time.sleep(5)
