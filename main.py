#credit @SymoonAi 🐸
import telebot
from telebot import types
from telebot.types import MessageEntity
import random
import string
import emoji
import json
import os

TOKEN = "8702944221:AAGBbL8pgfC5GZiFEIrOmCD2DZoXQ37W-r8"
ADMIN_ID = 7603719412
bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json"
POSTS_FILE = "posts.json"

# CUSTOM EMOJI CONFIGURATION
CUSTOM_EMOJIS = {
    "make_post":       ("🏣", 6336646834139700626),
    "connect_channel": ("🤙", None),
    "send_channel":    ("👏", None),
    "admin_panel":     ("🛠", None),
    "success":         ("✅", 6336861449360514102),
    "error":           ("❌", 6337033209397649451),
    "broadcast":       ("📢", 6336698133229082903),
    "status":          ("📊", 6336674562448563935),
    "welcome":         ("⭐", 6336646834139700626),
    "bot_active":      ("🚀", 6336674562448563935),
}

def get_emoji(key: str) -> str:
    char, _ = CUSTOM_EMOJIS.get(key, ("❓", None))
    return char

def get_emoji_entity(key: str, offset: int) -> MessageEntity | None:
    char, emoji_id = CUSTOM_EMOJIS.get(key, ("❓", None))
    if emoji_id:
        return MessageEntity(
            type="custom_emoji",
            offset=offset,
            length=len(char),
            custom_emoji_id=emoji_id
        )
    return None

def make_entities(text, bold=False, emoji_key=None, code_words=None):
    """
    text এর জন্য entities তৈরি করে।
    bold=True → পুরো text bold
    emoji_key → শুরুতে custom emoji
    code_words → list of words যেগুলো code format হবে
    """
    entities = []

    if emoji_key:
        ent = get_emoji_entity(emoji_key, 0)
        if ent:
            entities.append(ent)

    if bold:
        entities.append(MessageEntity(
            type="bold",
            offset=0,
            length=len(text)
        ))

    if code_words:
        for word in code_words:
            idx = text.find(str(word))
            if idx != -1:
                entities.append(MessageEntity(
                    type="code",
                    offset=idx,
                    length=len(str(word))
                ))

    return entities if entities else None

# ===========================

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        registered_users = set(json.load(f))
else:
    registered_users = set()

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(list(registered_users), f)

# Premium Emoji IDs
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

posts_db = {}
user_channels = {}
temp_data = {}

# --- UTILS ---
def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def process_text_and_entities(message):
    input_text = message.text or message.caption or ""
    original_entities = message.entities or message.caption_entities or []
    final_text, new_entities = "", []
    offset_map = {}
    current_old_offset, current_new_offset = 0, 0

    for char in input_text:
        offset_map[current_old_offset] = current_new_offset
        if emoji.is_emoji(char):
            rand_id = random.choice(PREMIUM_EMOJIS)
            placeholder = "✨"
            new_entities.append(MessageEntity(
                type="custom_emoji",
                offset=current_new_offset,
                length=len(placeholder),
                custom_emoji_id=rand_id
            ))
            final_text += placeholder
            char_len = len(char.encode('utf-16-le')) // 2
            current_old_offset += char_len
            current_new_offset += len(placeholder)
        else:
            final_text += char
            current_old_offset += 1
            current_new_offset += 1

    offset_map[current_old_offset] = current_new_offset
    for ent in original_entities:
        if ent.type == "custom_emoji":
            continue
        new_start = offset_map.get(ent.offset)
        new_end = offset_map.get(ent.offset + ent.length)
        if new_start is not None and new_end is not None:
            new_entities.append(MessageEntity(
                type=ent.type,
                offset=new_start,
                length=new_end - new_start,
                url=ent.url,
                user=ent.user,
                language=ent.language,
                custom_emoji_id=ent.custom_emoji_id
            ))
    return final_text, new_entities

# --- KEYBOARDS ---
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        f"MAKE POST {get_emoji('make_post')}",
        f"CONNECT CHANNELS {get_emoji('connect_channel')}",
        f"SEND TO CHANNEL {get_emoji('send_channel')}"
    )
    if user_id == ADMIN_ID:
        markup.add(f"ADMIN PANEL {get_emoji('admin_panel')}")
    return markup

def admin_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(
            f"STATUS {get_emoji('status')}",
            callback_data="admin_status"
        ),
        types.InlineKeyboardButton(
            f"BROADCAST {get_emoji('broadcast')}",
            callback_data="admin_broadcast"
        )
    )
    return markup

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def welcome(message):
    if message.chat.id not in registered_users:
        registered_users.add(message.chat.id)
        save_users()

    text = f"{get_emoji('welcome')} WELCOME TO SYMOON PREMIUM EMOJI BOT!\n\nTHIS BOT CONVERTS YOUR NORMAL EMOJI INTO PREMIUM EMOJI"
    bot.send_message(
        message.chat.id,
        text,
        entities=make_entities(text, bold=True, emoji_key="welcome"),
        reply_markup=main_menu(message.chat.id)
    )

# --- ADMIN ---
@bot.message_handler(func=lambda m: m.text == f"ADMIN PANEL {get_emoji('admin_panel')}" and m.chat.id == ADMIN_ID)
def admin_panel(message):
    text = f"{get_emoji('admin_panel')} ADMIN PANEL\n\nWelcome"
    bot.send_message(
        message.chat.id,
        text,
        entities=make_entities(text, bold=True, emoji_key="admin_panel"),
        reply_markup=admin_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callback(call):
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == "admin_status":
        total = len(registered_users)
        bot.answer_callback_query(call.id)
        text = f"{get_emoji('status')} BOT STATUS\n\nTotal Users: {total}"
        bot.send_message(
            call.message.chat.id,
            text,
            entities=make_entities(text, bold=True, emoji_key="status", code_words=[str(total)])
        )

    elif call.data == "admin_broadcast":
        bot.answer_callback_query(call.id)
        sent = bot.send_message(call.message.chat.id, "Broadcast message send karo:")
        bot.register_next_step_handler(sent, perform_broadcast)

def perform_broadcast(message):
    success, fail = 0, 0
    for user_id in registered_users:
        try:
            bot.copy_message(user_id, message.chat.id, message.message_id)
            success += 1
        except:
            fail += 1
    text = f"{get_emoji('broadcast')} BROADCAST COMPLETE\n\n{get_emoji('success')} Success: {success}\n{get_emoji('error')} Failed: {fail}"
    bot.send_message(
        ADMIN_ID,
        text,
        entities=make_entities(text, bold=True, emoji_key="broadcast", code_words=[str(success), str(fail)])
    )

# --- MAKE POST ---
@bot.message_handler(func=lambda m: m.text == f"MAKE POST {get_emoji('make_post')}")
def start_post(message):
    sent = bot.send_message(message.chat.id, "SEND YOUR POST WITH NORMAL EMOJIS:")
    bot.register_next_step_handler(sent, process_post_content)

def process_post_content(message):
    photo_id = message.photo[-1].file_id if message.content_type == 'photo' else None
    processed_text, entities = process_text_and_entities(message)
    temp_data[message.chat.id] = {
        "id": generate_id(),
        "content": processed_text,
        "entities": entities,
        "photo_id": photo_id
    }
    sent = bot.send_message(message.chat.id, "SEND THE BUTTON NAME:")
    bot.register_next_step_handler(sent, process_button_name)

def process_button_name(message):
    temp_data[message.chat.id]["btn_name"] = message.text
    sent = bot.send_message(message.chat.id, "SEND THE BUTTON LINK (URL):")
    bot.register_next_step_handler(sent, process_button_link)

def process_button_link(message):
    user_id = message.chat.id
    data = temp_data[user_id]
    data["btn_url"] = message.text
    posts_db[data["id"]] = data

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text=data["btn_name"], url=data["btn_url"])
    )

    text = f"{get_emoji('success')} Done! ID: {data['id']}"
    bot.send_message(
        user_id,
        text,
        entities=make_entities(text, emoji_key="success", code_words=[data['id']])
    )

    if data["photo_id"]:
        bot.send_photo(
            user_id,
            data["photo_id"],
            caption=data["content"],
            caption_entities=data["entities"],
            reply_markup=markup
        )
    else:
        bot.send_message(
            user_id,
            data["content"],
            entities=data["entities"],
            reply_markup=markup
        )

# --- CHANNEL CONNECT ---
@bot.message_handler(func=lambda m: m.text == f"CONNECT CHANNELS {get_emoji('connect_channel')}")
def ask_channel(message):
    sent = bot.send_message(
        message.chat.id,
        "FORWARD A MESSAGE FROM THE CHANNEL OR WRITE @{username} :"
    )
    bot.register_next_step_handler(sent, verify_channel)

def verify_channel(message):
    chat_id = message.forward_from_chat.id if message.forward_from_chat else message.text
    try:
        member = bot.get_chat_member(chat_id, bot.get_me().id)
        if member.status in ['administrator', 'creator']:
            chat_info = bot.get_chat(chat_id)
            if message.chat.id not in user_channels:
                user_channels[message.chat.id] = []
            user_channels[message.chat.id].append({
                "id": chat_info.id,
                "title": chat_info.title
            })
            text = f"{get_emoji('success')} Connected: {chat_info.title}"
            bot.send_message(
                message.chat.id,
                text,
                entities=make_entities(text, emoji_key="success")
            )
        else:
            text = f"{get_emoji('error')} Bot ke admin banao age!"
            bot.send_message(
                message.chat.id,
                text,
                entities=make_entities(text, emoji_key="error")
            )
    except:
        text = f"{get_emoji('error')} CHANNEL NOT FOUND"
        bot.send_message(
            message.chat.id,
            text,
            entities=make_entities(text, emoji_key="error")
        )

# --- SEND TO CHANNEL ---
@bot.message_handler(func=lambda m: m.text == f"SEND TO CHANNEL {get_emoji('send_channel')}")
def ask_post_id(message):
    sent = bot.send_message(message.chat.id, "Enter Post ID:")
    bot.register_next_step_handler(sent, select_channel)

def select_channel(message):
    post_id = message.text.upper()
    if post_id not in posts_db or message.chat.id not in user_channels:
        text = f"{get_emoji('error')} ID vul!  channel e connect nai."
        bot.send_message(
            message.chat.id,
            text,
            entities=make_entities(text, emoji_key="error")
        )
        return
    markup = types.InlineKeyboardMarkup()
    for chan in user_channels[message.chat.id]:
        markup.add(types.InlineKeyboardButton(
            text=chan["title"],
            callback_data=f"send_{post_id}_{chan['id']}"
        ))
    bot.send_message(message.chat.id, "Konsa channel?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("send_"))
def perform_send(call):
    parts = call.data.split("_")
    pid = parts[1]
    cid = parts[2]
    data = posts_db.get(pid)
    if data:
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text=data["btn_name"], url=data["btn_url"])
        )
        try:
            if data["photo_id"]:
                bot.send_photo(
                    cid,
                    data["photo_id"],
                    caption=data["content"],
                    caption_entities=data["entities"],
                    reply_markup=markup
                )
            else:
                bot.send_message(
                    cid,
                    data["content"],
                    entities=data["entities"],
                    reply_markup=markup
                )
            text = f"{get_emoji('success')} Sent successfully!"
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                entities=make_entities(text, emoji_key="success")
            )
        except Exception as e:
            bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

print(f"{get_emoji('bot_active')} Bot is active...")
bot.infinity_polling()
