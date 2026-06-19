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
# আপনার ID লিস্ট থেকে প্রথম কয়েকটা টেস্ট করি
TEST_IDS = [
    "6100639476441161711",  # ✅
    "6102462664288509137",  # ❌
    "6100199534351097095",  # ⚠️
    "6336861449360514102",  # success
    "6337033209397649451",  # error
]    

# 🌐 20 LIKES API CONFIG
API_20_URL = 'https://riyad-like-api-ob-52.vercel.app'
API_20_KEY = 'RIYADAH' 

# 🌐 50 LIKES API CONFIG
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
# ✨ PREMIUM EMOJI IDs (YOUR IDs)
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

# Emoji Map - শুধু আপনার দেওয়া ইমোজি গুলোই
EMOJI_MAP = {
    "✅": PREMIUM_EMOJIS[0],   # check
    "❌": PREMIUM_EMOJIS[1],   # cross
    "⚠️": PREMIUM_EMOJIS[2],   # warning
    "ℹ️": PREMIUM_EMOJIS[3],   # info
    "🔥": PREMIUM_EMOJIS[4],   # fire
    "⚡": PREMIUM_EMOJIS[5],   # bolt
    "🚀": PREMIUM_EMOJIS[6],   # rocket
    "⭐": PREMIUM_EMOJIS[7],   # star
    "❤️": PREMIUM_EMOJIS[8],   # heart
    "💙": PREMIUM_EMOJIS[9],   # blue_heart
    "👑": PREMIUM_EMOJIS[10],  # crown
    "💎": PREMIUM_EMOJIS[11],  # diamond
    "🏆": PREMIUM_EMOJIS[12],  # trophy
    "🎯": PREMIUM_EMOJIS[13],  # target
    "📊": PREMIUM_EMOJIS[14],  # chart
    "📈": PREMIUM_EMOJIS[15],  # chart_up
    "📉": PREMIUM_EMOJIS[16],  # chart_down
    "👤": PREMIUM_EMOJIS[17],  # user
    "👥": PREMIUM_EMOJIS[18],  # users
    "🆔": PREMIUM_EMOJIS[19],  # id
    "🌍": PREMIUM_EMOJIS[20],  # globe
    "💳": PREMIUM_EMOJIS[21],  # card
    "⏰": PREMIUM_EMOJIS[22],  # clock
    "📅": PREMIUM_EMOJIS[23],  # calendar
    "⏳": PREMIUM_EMOJIS[24],  # hourglass
    "📢": PREMIUM_EMOJIS[25],  # speaker
    "🟢": PREMIUM_EMOJIS[26],  # green_circle
    "🔴": PREMIUM_EMOJIS[27],  # red_circle
    "🎓": PREMIUM_EMOJIS[28],  # graduate
    "📌": PREMIUM_EMOJIS[29],  # pin
    "📭": PREMIUM_EMOJIS[30],  # empty
    "💠": PREMIUM_EMOJIS[31],  # diamond2
    "🤖": PREMIUM_EMOJIS[32],  # bot
    "🔑": PREMIUM_EMOJIS[33],  # key
    "💾": PREMIUM_EMOJIS[34],  # save
    "📱": PREMIUM_EMOJIS[35],  # mobile
    "🔍": PREMIUM_EMOJIS[36],  # search
    "⏸️": PREMIUM_EMOJIS[37],  # pause
    "▶️": PREMIUM_EMOJIS[38],  # play
    "🚫": PREMIUM_EMOJIS[39],  # ban
    "📝": PREMIUM_EMOJIS[40],  # note
    "💰": PREMIUM_EMOJIS[41],  # money
    "🔄": PREMIUM_EMOJIS[42],  # refresh
    "❤️‍🔥": PREMIUM_EMOJIS[43], # heart_fire
    "🥇": PREMIUM_EMOJIS[44],  # gold
    "🥈": PREMIUM_EMOJIS[45],  # silver
    "🥉": PREMIUM_EMOJIS[46],  # bronze
}

def pe(emoji_char):
    """Convert normal emoji to Premium Custom Emoji using MessageEntity"""
    if emoji_char in EMOJI_MAP:
        return emoji_char, EMOJI_MAP[emoji_char]
    return emoji_char, None

def make_premium_text(text, bold=False):
    """Build text with premium emoji entities"""
    entities = []
    final_text = ""
    
    for char in text:
        if char in EMOJI_MAP:
            final_text += char
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=len(final_text) - len(char),
                length=len(char),
                custom_emoji_id=EMOJI_MAP[char]
            ))
        else:
            final_text += char
    
    if bold and entities:
        pass  # bold + custom_emoji can't mix easily, skip bold for premium text
    
    return final_text, entities if entities else None

def premium_text(text):
    """Simple premium text converter"""
    final_text, entities = make_premium_text(text)
    return final_text, entities

# ==========================================
# 🔧 LOAD ADMIN
# ==========================================
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
        text, entities = premium_text(f"📢 Join {channel['name']}")
        markup.add(InlineKeyboardButton(text=text, url=channel['link']))
    markup.add(InlineKeyboardButton(text="🔄 Try Again", callback_data="check_join"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    user_id = call.from_user.id
    not_joined = check_force_join(user_id)
    
    if not not_joined:
        bot.answer_callback_query(call.id, "✅ Verification Successful!")
        text, entities = premium_text("✅ Verification Successful!\n\nYou have joined all required channels.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, entities=entities)
    else:
        bot.answer_callback_query(call.id, "❌ Not joined all channels!")
        channels_text = "\n".join([f"❌ {ch['name']}" for ch in not_joined])
        text, entities = premium_text(f"⚠️ ACCESS DENIED!\n\n❌ Not joined:\n{channels_text}\n\nPlease join all channels.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, entities=entities, reply_markup=force_join_keyboard(not_joined))

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
    default = {"time": "08:57 AM", "last_run": "", "tasks": {}, "next_serial": 1, "stats": {"total_20_tasks": 0, "total_50_tasks": 0, "total_20_likes_sent": 0, "total_50_likes_sent": 0}}
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
    if chat_id > 0: return bot_is_on
    return get_group_status(chat_id)

# ==========================================
# 🎨 PREMIUM REPORT UI
# ==========================================
def report_ui(data, region, status, response_time, remain_requests, likes_sent):
    nickname = html.escape(str(data.get('PlayerNickname', 'Unknown')))
    uid = data.get('UID', 'Unknown')
    added = data.get('LikesGivenByAPI', 0)
    before = data.get('LikesbeforeCommand', 0)
    after = data.get('LikesafterCommand', 0)

    if status in [1, 2]:
        api_time = round(response_time * 0.8, 2)
        return f"""✅ <b>Likes Sent Successfully!</b>
━━━━━━━━━━━━━━━━━━━━━━━
⚡ Speed: {response_time}s | ⏱️ API: {api_time}s
💎 <b>Likes Sent:</b> <code>{likes_sent}</code>

👤 <b>Account:</b> <code>{nickname}</code>
🆔 <b>UID:</b> <code>{uid}</code>
🌍 <b>Region:</b> <code>{region.upper()}</code>

📈 <b>Before:</b> <code>{before}</code>
❤️ <b>Added:</b> <code>{added}</code>
📉 <b>After:</b> <code>{after}</code>

💎 <i>Remaining: {remain_requests}</i>"""
    else:
        return f"""❌ <b>Failed!</b>
⚠️ Target maxed or invalid.
📉 Before: <code>{before}</code> | 📈 After: <code>{after}</code>"""

def auto_report_ui(success, package, speed, nickname, uid, region, before, added, after, serial, reason="MAX"):
    if success:
        return f"""✅ <b>Auto Likes Sent! ⚡</b>
━━━━━━━━━━━━━━━━━━━━━━━
💳 {package} Likes | ⚡ {speed}s

👤 {nickname}
🆔 <code>{uid}</code> | 🌍 {region.upper()}

📈 Before: <code>{before}</code>
❤️ Added: <code>{added}</code>
📉 After: <code>{after}</code>

🎓 TASK: {serial}"""
    else:
        return f"""❌ <b>Auto Failed! ({reason})</b>
💳 {package} Likes | ⚡ {speed}s
👤 {nickname} | 🆔 <code>{uid}</code>
🎓 TASK: {serial}"""

# ==========================================
# 🤖 BOT GROUP TRACKING
# ==========================================
@bot.message_handler(content_types=['new_chat_members'])
def on_bot_added(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            chat_id = str(message.chat.id)
            all_groups = load_all_groups()
            all_groups[chat_id] = {"title": message.chat.title or "Unknown", "added_date": time.time(), "status": True}
            save_all_groups(all_groups)
            groups = load_groups()
            groups[chat_id] = "unlimited"
            save_groups(groups)

@bot.message_handler(content_types=['left_chat_member'])
def on_bot_removed(message):
    if message.left_chat_member.id == bot.get_me().id:
        chat_id = str(message.chat.id)
        all_groups = load_all_groups()
        if chat_id in all_groups: del all_groups[chat_id]; save_all_groups(all_groups)
        groups = load_groups()
        if chat_id in groups: del groups[chat_id]; save_groups(groups)

# ==========================================
# 👑 ADMIN COMMAND
# ==========================================
@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Not authorized!")
        return
    
    args = message.text.split()
    
    if len(args) == 3 and args[1].lower() == 'add':
        try:
            new_id = int(args[2])
            if new_id in ADMIN_IDS: bot.reply_to(message, "❌ Already admin!"); return
            ADMIN_IDS.append(new_id); save_admin_ids(ADMIN_IDS)
            text, entities = premium_text(f"✅ Admin Added: {new_id}")
            bot.send_message(message.chat.id, text, entities=entities)
        except: bot.reply_to(message, "❌ Invalid ID!")
    
    elif len(args) == 3 and args[1].lower() == 'remove':
        try:
            rid = int(args[2])
            if rid == 7603719412: bot.reply_to(message, "❌ Cannot remove master!"); return
            if rid in ADMIN_IDS: ADMIN_IDS.remove(rid); save_admin_ids(ADMIN_IDS)
            bot.reply_to(message, f"✅ Removed: {rid}")
        except: bot.reply_to(message, "❌ Invalid!")
    
    elif len(args) == 2 and args[1].lower() == 'list':
        text = f"👑 ADMINS: {len(ADMIN_IDS)}\n" + "\n".join([f"• {a}" + (" 👑" if a == 7603719412 else "") for a in ADMIN_IDS])
        bot.reply_to(message, text)

# ==========================================
# 🔧 LIMIT
# ==========================================
@bot.message_handler(commands=['limit'])
def handle_limit(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2: bot.reply_to(message, "⚠️ /limit number"); return
    try:
        global USER_LIMIT
        USER_LIMIT = max(1, int(args[1]))
        text, entities = premium_text(f"✅ Limit: {USER_LIMIT}")
        bot.send_message(message.chat.id, text, entities=entities)
    except: bot.reply_to(message, "❌ Number only!")

# ==========================================
# 📊 GLIST
# ==========================================
@bot.message_handler(commands=['glist'])
def handle_glist(message):
    if not admin_full_control(message.from_user.id): return
    all_groups = load_all_groups()
    if not all_groups: bot.reply_to(message, "📭 No groups!"); return
    text = f"📊 Groups: {len(all_groups)}\n"
    for cid, data in all_groups.items():
        status = "🟢" if get_group_status(int(cid)) else "🔴"
        text += f"{status} {data.get('title','?')} | {cid}\n"
    bot.reply_to(message, text)

# ==========================================
# ON/OFF
# ==========================================
@bot.message_handler(commands=['p0', 'p02', 'remainreset'])
def handle_admin_commands(message):
    global bot_is_on, user_usage
    if not admin_full_control(message.from_user.id): return
    cmd = message.text.split()[0].lower()
    chat_id = message.chat.id
    
    if cmd == '/p0':
        if chat_id < 0: set_group_status(chat_id, True); bot.reply_to(message, "✅ Group ON!")
        else: bot_is_on = True; bot.reply_to(message, "✅ Global ON!")
    elif cmd == '/p02':
        if chat_id < 0: set_group_status(chat_id, False); bot.reply_to(message, "❌ Group OFF!")
        else: bot_is_on = False; bot.reply_to(message, "❌ Global OFF!")
    elif cmd == '/remainreset':
        user_usage.clear()
        bot.reply_to(message, "✅ User limits reset!")

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
            channels_text = "\n".join([f"❌ {ch['name']}" for ch in not_joined])
            text, entities = premium_text(f"⚠️ ACCESS DENIED!\n\nHello {user_name}!\nJoin:\n{channels_text}")
            bot.send_message(chat_id, text, entities=entities, reply_markup=force_join_keyboard(not_joined))
            return

        if not is_bot_on_for_chat(chat_id): bot.reply_to(message, "❌ Bot OFF!"); return
        if is_vip and user_usage.get(user_id, 0) >= vips[str(user_id)]['limit']: bot.reply_to(message, "❌ VIP limit!"); return
        if not is_vip and user_usage.get(user_id, 0) >= USER_LIMIT: bot.reply_to(message, "❌ Daily limit!"); return

    args = message.text.split()
    if len(args) != 3: bot.reply_to(message, "⚠️ /like region uid"); return
    region, uid = args[1].upper(), args[2]
    if region not in ALLOWED_REGIONS: bot.reply_to(message, "❌ Invalid region!"); return

    process_like_request(message, region, uid, user_id, user_name, 50)

def process_like_request(message, region, uid, user_id, user_name, likes_count=50):
    global user_usage
    wait_msg = bot.reply_to(message, "🚀 Processing...")

    try:
        start_time = time.time()
        url = f"{API_50_URL}/like?api_key={API_50_KEY}&server_name={region.lower()}&uid={uid}"
        response = requests.get(url, timeout=45)
        data = response.json()
        response_time = round(time.time() - start_time, 2)
        status = data.get('status')

        if status in [1, 2]:
            if not is_admin(user_id): user_usage[user_id] = user_usage.get(user_id, 0) + 1
            vips = load_vip()
            remain = "♾️" if is_admin(user_id) else (vips[str(user_id)]['limit'] - user_usage.get(user_id, 0) if str(user_id) in vips else USER_LIMIT - user_usage.get(user_id, 0))
            final_text = report_ui(data, region, status, response_time, remain, likes_count)
            text, entities = premium_text(final_text)
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=text, entities=entities, parse_mode="HTML")
        else:
            text, entities = premium_text("❌ Failed to process UID.")
            bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=text, entities=entities)

    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_msg.message_id, text=f"❌ Error: {str(e)[:50]}")

# ==========================================
# 🚀 AUTO TASKS
# ==========================================
@bot.message_handler(commands=['autotime'])
def handle_autotime(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split(maxsplit=1)
    if len(args) != 2: bot.reply_to(message, "⚠️ /autotime HH:MM AM/PM"); return
    db = load_auto_db(); db['time'] = args[1].upper(); save_auto_db(db)
    bot.reply_to(message, f"✅ Time: {args[1].upper()}")

@bot.message_handler(commands=['likeauto'])
def handle_likeauto(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split()
    if len(args) != 5: bot.reply_to(message, "⚠️ /likeauto region uid 20/50 days"); return
    region, uid, pkg, dys = args[1].upper(), args[2], args[3], args[4]
    if region not in ALLOWED_REGIONS: bot.reply_to(message, "❌ Invalid region!"); return
    if pkg not in ['20', '50']: bot.reply_to(message, "❌ 20 or 50!"); return
    try: package, days, total = int(pkg), int(dys), int(pkg)*int(dys)
    except: bot.reply_to(message, "❌ Numbers!"); return

    db = load_auto_db(); serial = str(db['next_serial']).zfill(4); db['next_serial'] += 1
    db['tasks'][serial] = {"chat_id": message.chat.id, "region": region, "uid": uid, "package": package, "total_target": total, "sent": 0, "remain": total, "days": days, "days_completed": 0, "nickname": "...", "created_at": time.time(), "status": "active"}
    save_auto_db(db)
    bot.reply_to(message, f"✅ Task {serial}\n🆔 {uid}\n💳 {package}L x {days}D = {total}")

@bot.message_handler(commands=['autoremove'])
def handle_autoremove(message):
    if not admin_full_control(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2: bot.reply_to(message, "⚠️ /autoremove uid/task_serial"); return
    param = args[1]; db = load_auto_db(); tasks = db.get('tasks', {}); removed = []
    if param.startswith('task_'):
        s = param.replace('task_', '')
        if s in tasks: removed.append(tasks.pop(s))
    else:
        for s, t in list(tasks.items()):
            if t['uid'] == param: removed.append(tasks.pop(s))
    if removed: save_auto_db(db); bot.reply_to(message, f"✅ Removed {len(removed)}")
    else: bot.reply_to(message, "❌ Not found!")

@bot.message_handler(commands=['listauto'])
def handle_listauto(message):
    if not admin_full_control(message.from_user.id): return
    db = load_auto_db(); tasks = db.get('tasks', {})
    if not tasks: bot.reply_to(message, "📭 No tasks!"); return
    text = f"📊 Tasks: {len(tasks)} | ⏰ {db.get('time','?')}\n\n"
    for s, d in tasks.items():
        p = int((d['sent']/d['total_target'])*100) if d['total_target'] else 0
        text += f"🎓 {s} | 👤 {d.get('nickname','?')}\n🆔 {d['uid']} | 💳 {d['package']}L\n📊 {d['sent']}/{d['total_target']} ({p}%)\n\n"
    bot.reply_to(message, text)
    
@bot.message_handler(commands=['test'])
def test_emoji(message):
    for eid in TEST_IDS:
        try:
            bot.send_message(
                message.chat.id,
                f"Test {eid[:8]}... ✅",
                entities=[telebot.types.MessageEntity(
                    type="custom_emoji",
                    offset=5,
                    length=1,
                    custom_emoji_id=eid
                )]
            )
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ ID {eid[:8]}... Error: {str(e)[:50]}")

bot.polling()

# ==========================================
# 🎯 VIP
# ==========================================
@bot.message_handler(commands=['vipadd', 'removevip', 'listvip', 'allow', 'disallow', 'remains'])
def handle_vip(message):
    cmd = message.text.split()[0].lower()
    user_id, chat_id = message.from_user.id, message.chat.id
    
    if cmd == '/remains':
        if not is_admin(user_id):
            if not is_bot_on_for_chat(chat_id): bot.reply_to(message, "❌ Bot OFF!"); return
            not_joined = check_force_join(user_id)
            if not_joined: bot.reply_to(message, "⚠️ Join channels!", reply_markup=force_join_keyboard(not_joined)); return
        
        vips = load_vip()
        if is_admin(user_id): uses = "♾️"
        elif str(user_id) in vips: uses = f"{vips[str(user_id)]['limit'] - user_usage.get(user_id, 0)}/{vips[str(user_id)]['limit']}"
        else: uses = f"{USER_LIMIT - user_usage.get(user_id, 0)}/{USER_LIMIT}"
        bot.reply_to(message, f"👤 Limit: {uses}")
        return

    if not admin_full_control(user_id): return
    args = message.text.split()

    if cmd == '/vipadd' and len(args) == 3:
        vips = load_vip(); vips[args[1]] = {"name": f"User{args[1]}", "limit": int(args[2])}; save_vip(vips)
        bot.reply_to(message, f"✅ VIP: {args[1]}")
    elif cmd == '/removevip':
        vips = load_vip()
        if len(args) == 2 and args[1] in vips: del vips[args[1]]; save_vip(vips)
        bot.reply_to(message, "🚫 Removed")
    elif cmd == '/listvip':
        vips = load_vip()
        if not vips: bot.reply_to(message, "📭 No VIPs"); return
        bot.reply_to(message, "🌟 VIPs:\n" + "\n".join([f"👤 {u}: {d['limit']}" for u, d in vips.items()]))
    elif cmd == '/allow':
        groups = load_groups(); groups[str(chat_id)] = "unlimited"; save_groups(groups)
        bot.reply_to(message, "✅ Allowed!")
    elif cmd == '/disallow':
        groups = load_groups(); cid = str(chat_id)
        if cid in groups: del groups[cid]; save_groups(groups)
        bot.reply_to(message, "🚫 Disallowed!")

# ==========================================
# ⏰ CRON
# ==========================================
def execute_auto_tasks():
    db = load_auto_db(); tasks = db.get("tasks", {})
    if not tasks: return
    for serial, task in list(tasks.items()):
        if task.get('status') == 'paused': continue
        uid, region, package, chat_id = task['uid'], task['region'], task['package'], task['chat_id']
        url = f"{API_20_URL}/like?uid={uid}&server_name={region.lower()}&key={API_20_KEY}" if package == 20 else f"{API_50_URL}/like?api_key={API_50_KEY}&server_name={region.lower()}&uid={uid}"
        try:
            start = time.time(); resp = requests.get(url, timeout=45).json(); rt = round(time.time() - start, 2)
            status = resp.get('status'); nick = html.escape(str(resp.get('PlayerNickname', '?')))
            added = resp.get('LikesGivenByAPI', 0); before = resp.get('LikesbeforeCommand', 0); after = resp.get('LikesafterCommand', 0)
            if status in [1, 2]:
                task['sent'] += added; task['remain'] -= added; task['nickname'] = nick
                msg = auto_report_ui(True, package, rt, nick, uid, region, before, added, after, serial)
                text, entities = premium_text(msg)
                try: bot.send_message(chat_id, text, entities=entities, parse_mode="HTML")
                except: pass
                all_groups = load_all_groups()
                for gid in all_groups:
                    if str(gid) != str(chat_id) and is_bot_on_for_chat(int(gid)):
                        try: bot.send_message(int(gid), text, entities=entities, parse_mode="HTML")
                        except: pass
        except Exception as e: print(f"Task {serial} Error: {e}")
        save_auto_db(db)
        if task.get('remain', 0) <= 0:
            db = load_auto_db()
            if serial in db.get('tasks', {}): del db['tasks'][serial]; save_auto_db(db)
        time.sleep(10)

def cron_worker():
    tz = pytz.timezone('Asia/Dhaka')
    while True:
        try:
            now = datetime.datetime.now(tz); db = load_auto_db()
            target = db.get("time", "04:30 AM"); last = db.get("last_run", "")
            ctime = now.strftime("%I:%M %p"); cdate = now.strftime("%Y-%m-%d")
            if ctime == target and last != cdate:
                db['last_run'] = cdate; save_auto_db(db); execute_auto_tasks()
        except Exception as e: print(f"Cron: {e}")
        time.sleep(30)

if __name__ == "__main__":
    print("🚀 Premium Like Bot Starting...")
    threading.Thread(target=cron_worker, daemon=True).start()
    while True:
        try: bot.polling(none_stop=True, timeout=60)
        except Exception as e: print(f"Restarting... {e}"); time.sleep(5)
