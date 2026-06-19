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
    {"username": "@riyadautolikegroup", "link": "https://t.me/riyadautolikegroup", "name": "Riyad Auto Likes Group"},
    {"username": "@riyadalhasanbackupchanel", "link": "https://t.me/riyadalhasanbackupchanel", "name": "Riyad Al Hasan Backup Channel"}
]

# 👑 Admin Settings
ADMIN_IDS_FILE = 'admin_ids.json'
DEFAULT_ADMINS = [7603719412]

# ==========================================
# ✨ PREMIUM ANIMATED EMOJI SYSTEM (REAL IDs)
# ==========================================
PREMIUM_EMOJIS = [
    "6100639476441161711",
    "6102462664288509137",
    "6100199534351097095",
    "6102926404792360795",
    "6100409966273764915",
    "6100430105375415737",
    "6102470558438400435",
    "6100451820730064687",
    "6102638599033858630",
    "6100179369479642954",
    "6100485115316542792",
    "6102661242101440205",
    "6102592514034770678",
    "6102475626499808862",
    "6102863908723236868",
    "6102510630483271620",
    "6282589525348720171",
    "6055377380204092112",
    "6055551219005398825",
    "6055181976371994390",
    "6055481009175010794",
    "6055484548228062462",
    "6055202102588742236",
    "6055450347403484860",
    "6055228576767155521",
    "6055183995006623379",
    "6337009415278828759",
    "6336756235546663929",
    "6334772471757020134",
    "6336732269629153634",
    "6336833407519038409",
    "6337048276142924106",
    "6337018975876030803",
    "6336608132189395373",
    "6336797785060286399",
    "6336685231147326793",
    "6336907611669011898",
    "6336988189550451848",
    "6337098578799893838",
    "6336808092981796477",
    "6337020083977592163",
    "6337112997005107243",
    "6337051755066433311",
    "6336835907190004485",
    "6336618976981818626",
    "6336857218817728795",
    "6336974471424908889",
    "6337125748763008448",
    "6337098338281725706",
    "6336962978092425393",
    "6336633214798404108",
    "6337019139084786234",
    "6337035356881296575",
    "6337026908680625329",
    "6336690569791676356",
    "6337106906741480828",
    "6337072645787361389",
    "6336720729052027967",
    "6336670885956557643",
    "6337113894653271580",
    "6334488003188105980",
    "6336721798498884548",
    "6336799284003873851",
    "6337112129421713282",
    "6336599202952388231",
    "6336755629956275338",
    "6334702021408465964",
    "6337109865973948062",
    "6336708763273142215",
    "6337083451925078342",
    "6336930400765484501",
    "6334788126912815244",
    "6337059606266651217",
    "6336812005697002754",
    "6336813629194640485",
    "6337085796977221633",
    "6336663202260065128",
    "6334324468013341494",
    "6337047855236129713",
    "6336782885818742144",
    "6336664645369076808",
    "6336910583786383660",
    "6336862179504954500",
    "6336697226990985005",
    "6336772620846899242",
    "6337033209397649451",
    "6336861449360514102",
    "6336573617832206335",
    "6337055242579876765",
    "6336789422758960593",
    "6336781331040577785",
    "6336603218746810844",
    "6337123072998383823",
    "6336894825551371014",
    "6334681658968513467",
    "6336799919659031563",
    "6336707603631972035",
    "6336874467406389346",
    "6336756411640323933",
    "6336608037700115865",
    "6336613247495445753",
    "6336973539417007164",
    "6336931040715612818",
    "6336653869296132233",
    "6336836572909938734",
    "6336798231736885254",
    "6336813951317187443",
    "6336866435817545002",
    "6336662845777780692",
    "6336580455420141312",
    "6336750437340816001",
    "6336677470141422007",
    "6337078718871117522",
    "6336931345658289868",
    "6336935322798005307",
    "6336646834139700626",
    "6337010179783007229",
    "6336618208182673162",
    "6336580975111184057",
    "6336957184181543528",
    "6336991256157101601",
    "6336655355354815762",
    "6336795865209904645",
    "6337054177427988529",
    "6336855354801921798",
    "6336878444546105899",
    "6336861037043654967",
    "6336662472115626382",
    "6337093386184432717",
    "6336637947852365586",
    "6336876696494417749",
    "6334678278829252492",
    "6337087411884923105",
    "6336989731443711607",
    "6336882614959349480",
    "6336886055228153516",
    "6336797591786757523",
    "6336674519498890396",
    "6336856849450540332",
    "6337048379222138619",
    "6336816932024491505",
    "6336672814396874442",
    "6336835035311644293",
    "6336668004033504924",
    "6336682357814205676",
    "6336764563488252026",
    "6337100812182887680",
    "6336575056646249129"
]

# Emoji Index Mapping
PE = {
    "check": 0, "cross": 1, "warning": 2, "info": 3, "fire": 4,
    "bolt": 5, "rocket": 6, "star": 7, "heart": 8, "blue_heart": 9,
    "crown": 10, "diamond": 11, "trophy": 12, "target": 13, "chart": 14,
    "chart_up": 15, "chart_down": 16, "user": 17, "users": 18, "id": 19,
    "globe": 20, "card": 21, "clock": 22, "calendar": 23, "hourglass": 24,
    "speaker": 25, "green_circle": 26, "red_circle": 27, "graduate": 28,
    "pin": 29, "empty": 30, "diamond2": 31, "bot": 32, "key": 33,
    "save": 34, "mobile": 35, "search": 36, "pause": 37, "play": 38,
    "ban": 39, "note": 40, "money": 41, "refresh": 42, "heart_fire": 43,
    "gold": 44, "silver": 45, "bronze": 46
}

def pe(name):
    """Premium Animated Emoji"""
    if name in PE:
        idx = PE[name]
        if idx < len(PREMIUM_EMOJIS):
            emoji_map = {
                "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️",
                "fire": "🔥", "bolt": "⚡", "rocket": "🚀", "star": "⭐",
                "heart": "❤️", "blue_heart": "💙", "crown": "👑", "diamond": "💎",
                "trophy": "🏆", "target": "🎯", "chart": "📊", "chart_up": "📈",
                "chart_down": "📉", "user": "👤", "users": "👥", "id": "🆔",
                "globe": "🌍", "card": "💳", "clock": "⏰", "calendar": "📅",
                "hourglass": "⏳", "speaker": "📢", "green_circle": "🟢",
                "red_circle": "🔴", "graduate": "🎓", "pin": "📌", "empty": "📭",
                "diamond2": "💠", "bot": "🤖", "key": "🔑", "save": "💾",
                "mobile": "📱", "search": "🔍", "pause": "⏸️", "play": "▶️",
                "ban": "🚫", "note": "📝", "money": "💰", "refresh": "🔄",
                "heart_fire": "❤️‍🔥", "gold": "🥇", "silver": "🥈", "bronze": "🥉"
            }
            emoji_char = emoji_map.get(name, name)
            return f'<emoji id="{PREMIUM_EMOJIS[idx]}">{emoji_char}</emoji>'
    return name

# Load admin IDs
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

# Global State
bot_is_on = True
USER_LIMIT = 1
user_usage = {}

# ==========================================
# 🔗 FORCE JOIN CHECKER
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
        markup.add(InlineKeyboardButton(f"{pe('speaker')} Join {channel['name']}", url=channel['link']))
    markup.add(InlineKeyboardButton(f"{pe('refresh')} Try Again", callback_data="check_join"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    user_id = call.from_user.id
    not_joined = check_force_join(user_id)
    
    if not not_joined:
        bot.answer_callback_query(call.id, "✅ Verification Successful!")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"<b>{pe('check')} Verification Successful!</b>\n\nYou have joined all required channels. You can now use the bot commands.",
            parse_mode="HTML"
        )
    else:
        bot.answer_callback_query(call.id, "❌ You still haven't joined all channels!")
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
# 🛡️ ADMIN CHECKER
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

def load_vip(): return load_json(VIP_FILE, {})
def save_vip(data): save_json(VIP_FILE, data)
def load_groups(): return load_json(GROUPS_FILE, {})
def save_groups(data): save_json(GROUPS_FILE, data)
def load_all_groups(): return load_json(ALL_GROUPS_FILE, {})
def save_all_groups(data): save_json(ALL_GROUPS_FILE, data)

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

def save_auto_db(data): save_json(AUTO_DB_FILE, data)

def load_group_status(): return load_json(GROUP_STATUS_FILE, {})
def save_group_status(data): save_json(GROUP_STATUS_FILE, data)

def get_group_status(chat_id):
    group_status = load_group_status()
    return group_status.get(str(chat_id), True)

def set_group_status(chat_id, status):
    group_status = load_group_status()
    group_status[str(chat_id)] = status
    save_group_status(group_status)

def is_bot_on_for_chat(chat_id):
    if chat_id > 0:
        return bot_is_on
    return get_group_status(chat_id)

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
    return f"<b>{pe('warning')} {title}</b>\n{pe('cross')} {message}"

def info_ui(title, message):
    return f"<b>{pe('info')} {title}</b>\n{pe('diamond2')} {message}"

# ==========================================
# 🤖 BOT GROUP TRACKING
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

# ==========================================
# 👑 ADMIN COMMAND
# ==========================================
@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, f"{pe('cross')} You are not authorized!", parse_mode="HTML")
        return
    
    args = message.text.split()
    
    if len(args) == 3 and args[1].lower() == 'add':
        try:
            new_admin_id = int(args[2])
            if new_admin_id in ADMIN_IDS:
                bot.reply_to(message, f"{pe('cross')} User already admin!", parse_mode="HTML")
                return
            ADMIN_IDS.append(new_admin_id)
            save_admin_ids(ADMIN_IDS)
            bot.reply_to(message, f"{pe('check')} **New Admin Added!**\n{pe('crown')} ID: `{new_admin_id}`", parse_mode="HTML")
        except:
            bot.reply_to(message, f"{pe('cross')} Invalid ID!", parse_mode="HTML")
    
    elif len(args) == 3 and args[1].lower() == 'remove':
        try:
            rid = int(args[2])
            if rid == 7603719412:
                bot.reply_to(message, f"{pe('cross')} Cannot remove master!", parse_mode="HTML")
                return
            if rid in ADMIN_IDS:
                ADMIN_IDS.remove(rid)
                save_admin_ids(ADMIN_IDS)
                bot.reply_to(message, f"{pe('check')} Admin Removed: `{rid}`", parse_mode="HTML")
        except:
            bot.reply_to(message, f"{pe('cross')} Invalid ID!", parse_mode="HTML")
    
    elif len(args) == 2 and args[1].lower() == 'list':
        admin_list = ""
        for idx, aid in enumerate(ADMIN_IDS, 1):
            master = f" {pe('crown')} MASTER" if aid == 7603719412 else ""
            admin_list += f"{idx}. `{aid}`{master}\n"
        bot.reply_to(message, f"<b>{pe('crown')} ADMIN LIST</b>\n{pe('chart')} Total: {len(ADMIN_IDS)}\n{admin_list}", parse_mode="HTML")

# ==========================================
# 🔧 LIMIT COMMAND
# ==========================================
@bot.message_handler(commands=['limit'])
def handle_limit_command(message):
    if not admin_full_control(message.from_user.id):
        return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, f"{pe('warning')} Usage: /limit number", parse_mode="HTML")
        return
    try:
        global USER_LIMIT
        USER_LIMIT = max(1, int(args[1]))
        bot.reply_to(message, f"{pe('check')} Limit set to: {USER_LIMIT}", parse_mode="HTML")
    except:
        bot.reply_to(message, f"{pe('cross')} Invalid number!", parse_mode="HTML")

# ==========================================
# 📊 GROUP LIST
# ==========================================
@bot.message_handler(commands=['glist'])
def handle_glist_command(message):
    if not admin_full_control(message.from_user.id):
        return
    all_groups = load_all_groups()
    if not all_groups:
        bot.reply_to(message, f"{pe('empty')} No groups found!", parse_mode="HTML")
        return
    
    on_count = sum(1 for g in all_groups if all_groups[g].get('status', True))
    off_count = len(all_groups) - on_count
    
    text = f"<b>{pe('chart')} ALL GROUPS</b>\n{pe('pin')} Total: {len(all_groups)}\n"
    text += f"{pe('green_circle')} ON: {on_count} | {pe('red_circle')} OFF: {off_count}\n\n"
    
    for idx, (cid, data) in enumerate(all_groups.items(), 1):
        is_on = get_group_status(int(cid))
        status = pe('green_circle') if is_on else pe('red_circle')
        text += f"{idx}. <b>{data.get('title', 'Unknown')}</b>\n   {status} | ID: <code>{cid}</code>\n\n"
    
    bot.reply_to(message, text, parse_mode="HTML")

# ==========================================
# ON/OFF COMMANDS
# ==========================================
@bot.message_handler(commands=['p0', 'p02', 'remainreset'])
def handle_admin_commands(message):
    global bot_is_on, user_usage
    if not admin_full_control(message.from_user.id): 
        return
    
    cmd = message.text.split()[0].lower()
    chat_id = message.chat.id
    
    if cmd == '/p0':
        if chat_id < 0:
            set_group_status(chat_id, True)
            bot.reply_to(message, f"{pe('check')} Bot ON for this group!", parse_mode="HTML")
        else:
            bot_is_on = True
            bot.reply_to(message, f"{pe('check')} Bot ON globally!", parse_mode="HTML")
    elif cmd == '/p02':
        if chat_id < 0:
            set_group_status(chat_id, False)
            bot.reply_to(message, f"{pe('cross')} Bot OFF for this group!", parse_mode="HTML")
        else:
            bot_is_on = False
            bot.reply_to(message, f"{pe('cross')} Bot OFF globally!", parse_mode="HTML")
    elif cmd == '/remainreset':
        user_usage.clear()
        bot.reply_to(message, f"{pe('check')} User limits reset!", parse_mode="HTML")

# ==========================================
# 🎯 LIKE COMMAND
# ==========================================
@bot.message_handler(commands=['like'])
def handle_like(message):
    global user_usage
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chat_id = message.chat.id
    vips = load_vip()
    is_vip = str(user_id) in vips

    if not is_admin(user_id):
        not_joined = check_force_join(user_id)
        if not_joined:
            channels_text = "\n".join([f"{pe('cross')} {ch['name']}" for ch in not_joined])
            bot.reply_to(message, f"""<b>{pe('warning')} ACCESS DENIED!</b>

<b>{pe('user')} Hello {user_name}!</b>
You must join our channels first.

<b>{pe('cross')} Not joined:</b>
{channels_text}""", parse_mode="HTML", reply_markup=force_join_keyboard(not_joined))
            return

        if not is_bot_on_for_chat(chat_id):
            bot.reply_to(message, f"{pe('cross')} Bot is OFF for this group!", parse_mode="HTML")
            return

        if is_vip:
            if user_usage.get(user_id, 0) >= vips[str(user_id)]['limit']:
                bot.reply_to(message, f"{pe('cross')} VIP limit reached!", parse_mode="HTML")
                return
        else:
            if user_usage.get(user_id, 0) >= USER_LIMIT:
                bot.reply_to(message, f"{pe('cross')} Daily limit reached!", parse_mode="HTML")
                return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, f"{pe('warning')} Use: /like region uid", parse_mode="HTML")
        return

    region = args[1].upper()
    uid = args[2]

    if region not in ALLOWED_REGIONS:
        bot.reply_to(message, f"{pe('cross')} Invalid region!", parse_mode="HTML")
        return

    process_like_request(message, region, uid, user_id, user_name, 50)

def process_like_request(message, region, uid, user_id, user_name, likes_count=50):
    global user_usage
    wait_msg = bot.reply_to(message, f"{pe('rocket')} Processing... {pe('rocket')}", parse_mode="HTML")

    try:
        start_time = time.time()
        url = f"{API_50_URL}/like?api_key={API_50_KEY}&server_name={region.lower()}&uid={uid}"
        response = requests.get(url, timeout=45)
        data = response.json()
        response_time = round(time.time() - start_time, 2)
        status = data.get('status')

        if status in [1, 2]:
            if not is_admin(user_id):
                user_usage[user_id] = user_usage.get(user_id, 0) + 1
            vips = load_vip()
            remain = "♾️" if is_admin(user_id) else (vips[str(user_id)]['limit'] - user_usage.get(user_id, 0) if str(user_id) in vips else USER_LIMIT - user_usage.get(user_id, 0))
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=report_ui(data, region, status, response_time, remain, likes_count), parse_mode="HTML")
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=f"{pe('cross')} Failed to process UID.", parse_mode="HTML")

    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=f"{pe('cross')} Error: {str(e)[:50]}", parse_mode="HTML")

# ==========================================
# 🚀 AUTO TASK COMMANDS
# ==========================================
@bot.message_handler(commands=['autotime'])
def handle_autotime(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        bot.reply_to(message, f"{pe('warning')} Usage: /autotime HH:MM AM/PM", parse_mode="HTML")
        return
    db = load_auto_db()
    db['time'] = args[1].upper()
    save_auto_db(db)
    bot.reply_to(message, f"{pe('check')} Auto time set: {args[1].upper()}", parse_mode="HTML")

@bot.message_handler(commands=['likeauto'])
def handle_likeauto(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split()
    if len(args) != 5:
        bot.reply_to(message, f"{pe('warning')} Usage: /likeauto region uid 20/50 days", parse_mode="HTML")
        return

    region, uid, pkg, dys = args[1].upper(), args[2], args[3], args[4]
    if region not in ALLOWED_REGIONS:
        bot.reply_to(message, f"{pe('cross')} Invalid region!", parse_mode="HTML")
        return
    if pkg not in ['20', '50']:
        bot.reply_to(message, f"{pe('cross')} Package: 20 or 50", parse_mode="HTML")
        return

    try:
        package, days = int(pkg), int(dys)
        total_likes = package * days
    except:
        bot.reply_to(message, f"{pe('cross')} Numbers only!", parse_mode="HTML")
        return

    db = load_auto_db()
    serial = str(db['next_serial']).zfill(4)
    db['next_serial'] += 1
    
    if package == 20: db['stats']['total_20_tasks'] = db['stats'].get('total_20_tasks', 0) + 1
    else: db['stats']['total_50_tasks'] = db['stats'].get('total_50_tasks', 0) + 1

    db['tasks'][serial] = {
        "chat_id": message.chat.id, "region": region, "uid": uid,
        "package": package, "total_target": total_likes, "sent": 0,
        "remain": total_likes, "days": days, "days_completed": 0,
        "nickname": "Waiting...", "created_at": time.time(), "status": "active"
    }
    save_auto_db(db)
    bot.reply_to(message, f"{pe('check')} Task Added!\n{pe('graduate')} Task: {serial}\n{pe('id')} UID: {uid}\n{pe('card')} {package} Likes x {days} Days", parse_mode="HTML")

@bot.message_handler(commands=['autoremove'])
def handle_autoremove(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, f"{pe('warning')} Usage: /autoremove uid", parse_mode="HTML")
        return
    
    param = args[1]
    db = load_auto_db()
    tasks = db.get('tasks', {})
    removed = []
    
    if param.startswith('task_'):
        serial = param.replace('task_', '')
        if serial in tasks:
            removed.append((serial, tasks.pop(serial)))
    else:
        for s, t in list(tasks.items()):
            if t['uid'] == param:
                removed.append((s, tasks.pop(s)))
    
    if removed:
        save_auto_db(db)
        bot.reply_to(message, f"{pe('check')} Removed {len(removed)} task(s)", parse_mode="HTML")
    else:
        bot.reply_to(message, f"{pe('cross')} Not found!", parse_mode="HTML")

@bot.message_handler(commands=['listauto'])
def handle_listauto(message):
    if not admin_full_control(message.from_user.id): return
    db = load_auto_db()
    tasks = db.get('tasks', {})
    if not tasks:
        bot.reply_to(message, f"{pe('empty')} No tasks!", parse_mode="HTML")
        return
    
    text = f"<b>{pe('chart')} AUTO TASKS</b>\n{pe('clock')} Next: {db.get('time', 'N/A')}\n\n"
    for serial, data in tasks.items():
        progress = int((data['sent'] / data['total_target']) * 100) if data['total_target'] > 0 else 0
        text += f"""{pe('graduate')} <b>TASK {serial}</b>
{pe('user')} {data.get('nickname', '?')}
{pe('id')} {data['uid']} | {data['region']}
{pe('card')} {data['package']} Likes | {pe('chart_up')} {progress}%
{pe('chart')} {data['sent']}/{data['total_target']}
{pe('hourglass')} {data['days'] - data['days_completed']} days left

"""
    bot.reply_to(message, text, parse_mode="HTML")

# ==========================================
# 🎯 VIP COMMANDS
# ==========================================
@bot.message_handler(commands=['vipadd', 'removevip', 'listvip', 'allow', 'disallow', 'remains'])
def handle_vip_group_commands(message):
    cmd = message.text.split()[0].lower()
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if cmd == '/remains':
        if not is_admin(user_id):
            if not is_bot_on_for_chat(chat_id):
                bot.reply_to(message, f"{pe('cross')} Bot OFF!", parse_mode="HTML")
                return
            not_joined = check_force_join(user_id)
            if not_joined:
                bot.reply_to(message, f"{pe('warning')} Join channels first!", parse_mode="HTML", reply_markup=force_join_keyboard(not_joined))
                return
        
        vips = load_vip()
        if is_admin(user_id):
            uses = "♾️ Admin"
        elif str(user_id) in vips:
            uses = f"{vips[str(user_id)]['limit'] - user_usage.get(user_id, 0)}/{vips[str(user_id)]['limit']} VIP"
        else:
            uses = f"{USER_LIMIT - user_usage.get(user_id, 0)}/{USER_LIMIT}"
        bot.reply_to(message, f"{pe('user')} Your Limit: {uses}", parse_mode="HTML")
        return

    if not admin_full_control(user_id): return
    args = message.text.split()

    if cmd == '/vipadd' and len(args) == 3:
        vips = load_vip()
        vips[args[1]] = {"name": f"User {args[1]}", "limit": int(args[2])}
        save_vip(vips)
        bot.reply_to(message, f"{pe('check')} VIP Added: {args[1]}", parse_mode="HTML")
    elif cmd == '/removevip':
        vips = load_vip()
        if len(args) == 2 and args[1] in vips:
            del vips[args[1]]
            save_vip(vips)
        bot.reply_to(message, f"{pe('ban')} VIP Removed", parse_mode="HTML")
    elif cmd == '/listvip':
        vips = load_vip()
        text = f"<b>{pe('star')} VIP LIST</b>\n"
        for uid, data in vips.items():
            text += f"{pe('user')} {uid}: {data['limit']}\n"
        bot.reply_to(message, text or f"{pe('empty')} No VIPs", parse_mode="HTML")
    elif cmd == '/allow':
        groups = load_groups()
        groups[str(message.chat.id)] = "unlimited"
        save_groups(groups)
        bot.reply_to(message, f"{pe('check')} Group allowed!", parse_mode="HTML")
    elif cmd == '/disallow':
        groups = load_groups()
        cid = str(message.chat.id)
        if cid in groups:
            del groups[cid]
            save_groups(groups)
        bot.reply_to(message, f"{pe('ban')} Group disallowed!", parse_mode="HTML")

# ==========================================
# ⏰ CRON JOB
# ==========================================
def execute_auto_tasks():
    db = load_auto_db()
    tasks = db.get("tasks", {})
    if not tasks: return

    for serial, task in list(tasks.items()):
        if task.get('status') == 'paused': continue
            
        uid, region, package, chat_id = task['uid'], task['region'], task['package'], task['chat_id']
        
        if package == 20:
            url = f"{API_20_URL}/like?uid={uid}&server_name={region.lower()}&key={API_20_KEY}"
        else:
            url = f"{API_50_URL}/like?api_key={API_50_KEY}&server_name={region.lower()}&uid={uid}"
        
        try:
            start_time = time.time()
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
                
                msg = auto_report_ui(True, package, response_time, nickname, uid, region, before, added, after, serial)
                
                try: bot.send_message(chat_id, msg, parse_mode="HTML")
                except: pass
                
                all_groups = load_all_groups()
                for gid in all_groups:
                    if str(gid) != str(chat_id) and is_bot_on_for_chat(int(gid)):
                        try: bot.send_message(int(gid), msg, parse_mode="HTML")
                        except: pass
            else:
                msg = auto_report_ui(False, package, response_time, nickname, uid, region, before, 0, after, serial)
                try: bot.send_message(chat_id, msg, parse_mode="HTML")
                except: pass

        except Exception as e:
            print(f"Task {serial} Error: {e}")

        save_auto_db(db)
        
        if task.get('remain', 0) <= 0:
            db = load_auto_db()
            if serial in db.get('tasks', {}):
                del db['tasks'][serial]
                save_auto_db(db)
        
        time.sleep(10)

def cron_worker():
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
                db['last_run'] = current_date_str
                save_auto_db(db)
                execute_auto_tasks()
        except Exception as e:
            print(f"Cron Error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    print(f"{pe('rocket')} Premium Bot with Real Animated Emojis Starting...")
    print(f"{pe('crown')} Master Admin: 7603719412")
    
    cron_thread = threading.Thread(target=cron_worker, daemon=True)
    cron_thread.start()
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Bot crashed, restarting... Error: {e}")
            time.sleep(5)
