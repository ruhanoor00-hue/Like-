import telebot
import requests
import time
import json
import random
import os
import threading
import sys
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================= Monkey Patch for Button Styles =================
# This allows passing style="success", "primary", "danger" without crashing pyTelegramBotAPI
original_kb_init = KeyboardButton.__init__
def new_kb_init(self, text, style=None, **kwargs):
    original_kb_init(self, text, **kwargs)
    self.style = style
KeyboardButton.__init__ = new_kb_init

original_ikb_init = InlineKeyboardButton.__init__
def new_ikb_init(self, text, style=None, **kwargs):
    original_ikb_init(self, text, **kwargs)
    self.style = style
InlineKeyboardButton.__init__ = new_ikb_init
# ==================================================================

# ================= Configuration =================
BOT_TOKEN = "8967483751:AAFnqslPjUP5TpgiyvUr-c4pWNQ7AiMeweY"
ADMIN_ID = 7438873835
FORCE_SUB_CHANNEL_ID = -1002761413900
FORCE_SUB_CHANNEL_LINK = "https://t.me/Cyber_Surokkha"

bot = telebot.TeleBot(BOT_TOKEN)

# ================= Texts =================
TOP_TEXT = """
<i>✧ ─── ･ ｡ﾟ☆: .☽ . :☆ﾟ. ─── ✧</i>

<b>TIKSTAR AUTO BOT</b>

<i>✧ ─── ･ ｡ﾟ☆: .☽ . :☆ﾟ. ─── ✧</i>

<blockquote>The bot automates TikTok tasks
(watch, like, follow) to collect real TikStar coins.</blockquote>
"""

# ================= Data Variables =================
DATA_FILE = "bot_users.json"
user_states = {}
user_data = {}      # Token & FID storage for running tasks
user_stats = {}     # Session stats for running tasks
running_tasks = {}  # Thread control flags

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

bot_db = load_data()

def ensure_user(user_id):
    if user_id not in bot_db["users"]:
        bot_db["users"].append(user_id)
        save_data(bot_db)

# ================= API Variables & Setup =================
TIKTOK_API_BASE = "https://api16-normal-c-useast1a.tiktokv.com"
TIKTOK_AID = "1233"
keyie = "1688b7ca5531cfbd4a8f11cefa72d1fb"

TIKSTAR_BASE = "https://api.tikstarapp.xyz/api/tikstar"
CLIENT_ID = "16"
CLIENT_SECRET = "3ZhY6sI2KhJ4iftS3IlFAypFT1m7dQMe1keSjTqF"
REGISTRATION_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxNiIsImp0aSI6IjMxYzZlOWFkZWE4ZjYxOGVhMTQzMTM1YWJhNDg4NmYyYmEzZjU5OTExNzkyYWM3ZGNlMmY2YWJjYzNmMzUxY2UxYzY4MTk4ZWY5ZTE2M2Q5IiwiaWF0IjoxNzYyMDYxODYwLjE1MzE4MywibmJmIjoxNzYyMDYxODYwLjE1MzE4NSwiZXhwIjoyMDc3NTk0NjYwLjE0OTQ4Niwic3ViIjoiIiwic2NvcGVzIjpbIioiXX0.XB7kc0sHW34lcIhvrDvFdWgyJK03lUzTegpv0FJMGN1RVD1HNCoJvOoBsoxLwu16LQaEZonfD2qcAW9oHhEbdMBHRDFtkFM1vszd0xB5crHpXJ526NSJ_xATelTJtomrs-UhRFov_rUD1ZDPWFrp9yger8QwsPYxEUogVlBcuxC23-I71un7Km5kPHglJ_exsPNPJOy1rxw_eQu774T0qGUHWM6LW-pQni3nOcfp3AZ6C-2XTorFMpj64f8nxIVb0gW20QDxUQ9f15qbaxeX85Xa67EHE1gpWt7gKQPhs7TRmbThZs4XmW3DKAv-0A8_0azoLX_s4xMhG9Ul2A-_1Fj_yVCVQkaIhzJkXHqKP-L7lDUNF4oBVNgKUKILzdWRq-IeefYzpocsd_rEiwB4ZeYCiEYdMFHHcKZt5Sf4Zjvl25uhjXzLEhbjjGlDx0jBOuPo4EHBccGtn1EvfAJSYkStCXQ-z7Bko4362G6hqdnFTp-YVjz8IpbzP_gA5UsUhRrAdgjRi6GEbdQWs2LTJKadpfq592MF_Umcg1MpSCt-vSQi7q2JKwZxBINT-p6APJckkQ_9Dmo2wZbtb2UwQoZP_Fh4YtI2ZGocrcR2OZojhY1nmhVPAe4hlPUZmEVQKX2SSA-_ADp07-gM30Zhy0bUFpJqxlKipYzLBoL92BM"

_SIGN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sign")
if not os.path.isdir(_SIGN_DIR):
    _SIGN_DIR = os.path.join(os.getcwd(), "sign")
if _SIGN_DIR not in sys.path:
    sys.path.insert(0, os.path.dirname(_SIGN_DIR))

try:
    from sign import sign_mobile_request, make_seed_device
    _SIGN_DEVICE = make_seed_device()
    _SIGN_OK = True
except:
    _SIGN_OK = False

def gen_device_number():
    return ''.join(random.choices('0123456789abcdef', k=16))

_current_device = gen_device_number()

def get_base_headers():
    return {
        "User-Agent": "okhttp/4.12.0",
        "Accept-Encoding": "gzip",
        "device-number": _current_device,
        "platform": "tiktok",
        "app-version": "22",
        "accept-language": "en",
    }

def get_auth_headers(token=None):
    headers = get_base_headers()
    if token:
        headers["authorization"] = f"Bearer {token}"
    return headers

def get_fid_from_username(username):
    url = f"{TIKSTAR_BASE}/users/tiktok/{username}"
    params = {"include": "account"}
    payload = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    headers = get_auth_headers(REGISTRATION_TOKEN)
    try:
        resp = requests.post(url, params=params, data=payload, headers=headers, timeout=20)
        if resp.status_code in (200, 201):
            data = resp.json()
            return data.get("fid"), data.get("id"), data
    except:
        pass
    return None, None, None

def login_with_tiktok_fid(tiktok_fid):
    url = f"{TIKSTAR_BASE}/auth"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "*",
        "username": str(tiktok_fid),
        "password": "password",
        "grant_type": "password",
    }
    headers = get_auth_headers(REGISTRATION_TOKEN)
    try:
        resp = requests.post(url, data=payload, headers=headers, timeout=20)
        data = resp.json()
        if "access_token" in data:
            return data["access_token"]
    except:
        pass
    return None

def get_random_video(user_token, user_id):
    url = f"{TIKSTAR_BASE}/videos/rand"
    params = {"user_id": str(user_id)}
    headers = get_auth_headers(user_token)
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return {"id": data.get("id"), "coins": data.get("meta", {}).get("coins", "?")}
    except:
        pass
    return None

def submit_video_view(user_token, post_id):
    url = f"{TIKSTAR_BASE}/viewvideos"
    payload = {"post_id": str(post_id)}
    headers = get_auth_headers(user_token)
    try:
        resp = requests.post(url, data=payload, headers=headers, timeout=15)
        if resp.status_code in (200, 201):
            data = resp.json()
            return True, data.get("amount", {}).get("amount", "?")
    except:
        pass
    return False, None

def get_random_post(user_token, user_id):
    url = f"{TIKSTAR_BASE}/posts/rand"
    params = {"user_id": str(user_id)}
    headers = get_auth_headers(user_token)
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            return {"id": data.get("id")}
    except:
        pass
    return None

def like_post(user_token, post_id):
    url = f"{TIKSTAR_BASE}/likeposts"
    payload = {"post_ids": str(post_id)}
    headers = get_auth_headers(user_token)
    try:
        resp = requests.post(url, data=payload, headers=headers, timeout=20)
        if resp.status_code in (200, 201):
            data = resp.json()
            return True, data.get("amount", {}).get("amount", "?")
    except:
        pass
    return False, None

def get_random_user(user_token, user_id):
    url = f"{TIKSTAR_BASE}/users/rand"
    params = {"user_id": str(user_id)}
    headers = get_auth_headers(user_token)
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            return {"id": data.get("id"), "fid": data.get("fid")}
    except:
        pass
    return None

def follow_user(user_token, user_id):
    url = f"{TIKSTAR_BASE}/tiktok/verify-follow"
    payload = {"user_id": str(user_id)}
    headers = get_auth_headers(user_token)
    try:
        resp = requests.post(url, data=payload, headers=headers, timeout=20)
        if resp.status_code in (200, 201):
            data = resp.json()
            return True, data.get("amount", {}).get("amount", "?")
    except:
        pass
    return False, None

def get_user_coins(user_token):
    url = f"{TIKSTAR_BASE}/user"
    params = {"include": "account"}
    headers = get_auth_headers(user_token)
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            account = data.get("account", {})
            amount = account.get("amount", {})
            return amount.get("amount", "?"), data.get("name", "?")
    except:
        pass
    return "?", "?"

def tiktok_follow(fid):
    if not _SIGN_OK:
        return False
    url = f"{TIKTOK_API_BASE}/aweme/v1/commit/follow/user/"
    params = {
        "user_id": str(fid), "type": "1", "qid": "0", "aid": TIKTOK_AID,
        "device_id": str(_SIGN_DEVICE.device_id), "iid": str(_SIGN_DEVICE.iid),
        "install_id": str(_SIGN_DEVICE.install_id),
    }
    try:
        signed = sign_mobile_request("POST", "/aweme/v1/commit/follow/user/", {}, _SIGN_DEVICE, params, True)
        headers = {
            "X-SS-STUB": signed.get("X-SS-STUB", ""), "X-Khronos": signed.get("X-Khronos", ""),
            "X-Gorgon": signed.get("X-Gorgon", ""),
            "User-Agent": f"com.zhiliaoapp.musically/{_SIGN_DEVICE.app_version} (Linux; U; Android {_SIGN_DEVICE.os_version}; en_US; {_SIGN_DEVICE.device_type}; Build/TP1A; Cronet/58.0.2991.0)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"sessionid={keyie}; install_id={_SIGN_DEVICE.install_id}; iid={_SIGN_DEVICE.iid}",
        }
        resp = requests.post(url, params=params, headers=headers, timeout=20)
        return resp.json().get("status_code") == 0
    except:
        return False

def tiktok_unfollow(fid):
    if not _SIGN_OK:
        return False
    url = f"{TIKTOK_API_BASE}/aweme/v1/commit/follow/user/"
    params = {
        "user_id": str(fid), "type": "0", "qid": "0", "aid": TIKTOK_AID,
        "device_id": str(_SIGN_DEVICE.device_id), "iid": str(_SIGN_DEVICE.iid),
        "install_id": str(_SIGN_DEVICE.install_id),
    }
    try:
        signed = sign_mobile_request("POST", "/aweme/v1/commit/follow/user/", {}, _SIGN_DEVICE, params, True)
        headers = {
            "X-SS-STUB": signed.get("X-SS-STUB", ""), "X-Khronos": signed.get("X-Khronos", ""),
            "X-Gorgon": signed.get("X-Gorgon", ""),
            "User-Agent": f"com.zhiliaoapp.musically/{_SIGN_DEVICE.app_version} (Linux; U; Android {_SIGN_DEVICE.os_version}; en_US; {_SIGN_DEVICE.device_type}; Build/TP1A; Cronet/58.0.2991.0)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"sessionid={keyie}; install_id={_SIGN_DEVICE.install_id}; iid={_SIGN_DEVICE.iid}",
        }
        resp = requests.post(url, params=params, headers=headers, timeout=20)
        return resp.json().get("status_code") == 0
    except:
        return False

# ================= Keyboards =================
def get_main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("▶️ Start Task", style="success"),
        KeyboardButton("⏹ Stop Task", style="danger")
    )
    markup.add(
        KeyboardButton("📊 Statistics", style="primary"),
        KeyboardButton("🔗 Share Bot", style="primary")
    )
    if user_id == ADMIN_ID:
        markup.add(KeyboardButton("👑 Admin Panel", style="danger"))
    return markup

def get_admin_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📢 Broadcast", style="primary"),
        KeyboardButton("👥 Statistics", style="primary")
    )
    markup.add(KeyboardButton("🔙 Back to Main", style="danger"))
    return markup

def get_cancel_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔙 Cancel", style="danger"))
    return markup

# ================= Force Sub System =================
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(FORCE_SUB_CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Sub check error: {e}")
        return False

def send_force_sub(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔥 Join Channel", url=FORCE_SUB_CHANNEL_LINK, style="primary"))
    markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify_sub", style="success"))
    
    bot.send_message(
        chat_id, 
        "<b>Access Denied! 🚫</b>\n\nYou must join our official channel before using the bot.", 
        parse_mode="HTML", 
        reply_markup=markup
    )

# ================= Task Background Thread =================
def run_task_thread(user_id, username):
    bot.send_message(user_id, f"🔄 Collecting coins for <code>{username}</code>... Task runs in background.", parse_mode="HTML")
    
    fid, tikstar_id, _ = get_fid_from_username(username)
    if not fid:
        bot.send_message(user_id, "❌ User not found on TikStar.")
        running_tasks[user_id] = False
        return

    user_token = login_with_tiktok_fid(fid)
    if not user_token:
        bot.send_message(user_id, "❌ Login failed. Account may not be linked.")
        running_tasks[user_id] = False
        return

    user_data[user_id] = {"username": username, "fid": fid, "token": user_token, "tikstar_id": tikstar_id}
    user_stats[user_id] = {"success": 0, "fail": 0, "coins": 0, "running": True}
    running_tasks[user_id] = True

    mode = "video"
    while running_tasks.get(user_id, False):
        if mode == "video":
            video = get_random_video(user_token, tikstar_id)
            if video:
                time.sleep(2)
                success, earned = submit_video_view(user_token, video["id"])
                if success:
                    user_stats[user_id]["success"] += 1
                    user_stats[user_id]["coins"] += int(earned) if earned != "?" else 0
                else:
                    user_stats[user_id]["fail"] += 1
                    mode = "like"
            else:
                user_stats[user_id]["fail"] += 1
                mode = "like"
                
        elif mode == "like":
            post = get_random_post(user_token, tikstar_id)
            if post:
                time.sleep(2)
                success, earned = like_post(user_token, post["id"])
                if success:
                    user_stats[user_id]["success"] += 1
                    user_stats[user_id]["coins"] += int(earned) if earned != "?" else 0
                else:
                    user_stats[user_id]["fail"] += 1
                    mode = "follow"
            else:
                user_stats[user_id]["fail"] += 1
                mode = "follow"
                
        elif mode == "follow":
            target = get_random_user(user_token, tikstar_id)
            if target:
                time.sleep(2)
                if target.get("fid"):
                    tiktok_follow(target["fid"])
                time.sleep(2)
                success, earned = follow_user(user_token, target["id"])
                if target.get("fid"):
                    tiktok_unfollow(target["fid"])
                if success:
                    user_stats[user_id]["success"] += 1
                    user_stats[user_id]["coins"] += int(earned) if earned != "?" else 0
                else:
                    user_stats[user_id]["fail"] += 1
                    mode = "video"
            else:
                user_stats[user_id]["fail"] += 1
                mode = "video"
                
        time.sleep(2)
        
    user_stats[user_id]["running"] = False

# ================= Bot Handlers =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.chat.id
    ensure_user(user_id)
    
    if not check_subscription(user_id):
        send_force_sub(user_id)
        return

    bot.send_message(
        user_id, 
        TOP_TEXT + f"\n\nWelcome {message.from_user.first_name}! 👋\nChoose an option from the menu below.", 
        reply_markup=get_main_keyboard(user_id),
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data == "verify_sub")
def verify_sub_callback(call):
    if check_subscription(call.message.chat.id):
        bot.edit_message_text("✅ Verification successful! You can now use the bot.", call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Main Menu:", reply_markup=get_main_keyboard(call.message.chat.id))
    else:
        bot.answer_callback_query(call.id, "You haven't joined the channel yet! Join first.", show_alert=True)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.chat.id
    text = message.text

    if not check_subscription(user_id):
        send_force_sub(user_id)
        return

    state = user_states.get(user_id, {})
    current_step = state.get("step")

    # --- Cancel Action ---
    if text in ["🔙 Cancel", "🔙 Back to Main"]:
        user_states.pop(user_id, None)
        bot.send_message(user_id, "Returned to Main Menu.", reply_markup=get_main_keyboard(user_id))
        return

    # --- Main Menu Flows ---
    if text == "▶️ Start Task":
        if running_tasks.get(user_id, False):
            bot.send_message(user_id, "⚠️ You already have a task running. Stop it first using '⏹ Stop Task'.", reply_markup=get_main_keyboard(user_id))
            return
            
        user_states[user_id] = {"step": "waiting_for_username"}
        bot.send_message(user_id, "Please send your <b>TikTok Username</b> (e.g., @yourusername):", parse_mode="HTML", reply_markup=get_cancel_keyboard())

    elif current_step == "waiting_for_username":
        username = text.replace("@", "").strip()
        user_states.pop(user_id, None)
        
        bot.send_message(user_id, "Attempting to start task...", reply_markup=get_main_keyboard(user_id))
        threading.Thread(target=run_task_thread, args=(user_id, username), daemon=True).start()

    elif text == "⏹ Stop Task":
        if running_tasks.get(user_id, False):
            running_tasks[user_id] = False
            bot.send_message(user_id, "✅ Stopping the active task... Please wait a moment.")
        else:
            bot.send_message(user_id, "❌ No active task is currently running.")

    elif text == "📊 Statistics":
        stats = user_stats.get(user_id, {})
        if user_id in user_data:
            coins, name = get_user_coins(user_data[user_id].get("token", ""))
        else:
            coins, name = "?", "?"

        status = "Running 🟢" if running_tasks.get(user_id, False) else "Stopped 🔴"
        
        msg = f"<b>📊 Your Statistics</b>\n\n"
        msg += f"👤 User: <code>{name}</code>\n"
        msg += f"💰 Total Coins (TikStar): <b>{coins}</b>\n\n"
        msg += f"<b>Current Session:</b>\n"
        msg += f"✔️ Success: {stats.get('success', 0)}\n"
        msg += f"❌ Failed: {stats.get('fail', 0)}\n"
        msg += f"🪙 Earned Now: +{stats.get('coins', 0)}\n"
        msg += f"🔄 Status: {status}"
        
        bot.send_message(user_id, msg, parse_mode="HTML")

    elif text == "🔗 Share Bot":
        bot_info = bot.get_me()
        bot_link = f"https://t.me/{bot_info.username}"
        share_text = f"Hey! Check out this awesome Auto TikTok Task bot. It collects real coins completely on autopilot! 🚀\n\nJoin here: {bot_link}"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📤 Share Now", url=f"https://t.me/share/url?url={bot_link}&text=Check%20out%20this%20awesome%20Auto%20TikTok%20Task%20bot!", style="primary"))
        
        bot.send_message(user_id, share_text, reply_markup=markup)

    # --- Admin Flow ---
    elif text == "👑 Admin Panel" and user_id == ADMIN_ID:
        bot.send_message(user_id, "👑 Welcome to the Admin Panel.", reply_markup=get_admin_keyboard())

    elif text == "📢 Broadcast" and user_id == ADMIN_ID:
        user_states[user_id] = {"step": "waiting_for_broadcast"}
        bot.send_message(user_id, "Send the message you want to broadcast to all users:", reply_markup=get_cancel_keyboard())

    elif current_step == "waiting_for_broadcast" and user_id == ADMIN_ID:
        user_states.pop(user_id, None)
        success, failed = 0, 0
        bot.send_message(user_id, "Broadcasting in progress...", reply_markup=get_admin_keyboard())
        
        for uid in bot_db["users"]:
            try:
                bot.send_message(uid, text)
                success += 1
                time.sleep(0.05)
            except:
                failed += 1
                
        bot.send_message(user_id, f"✅ Broadcast Complete!\n\nSuccess: {success}\nFailed: {failed}")

    elif text == "👥 Statistics" and user_id == ADMIN_ID:
        total_users = len(bot_db["users"])
        active_tasks = sum(1 for status in running_tasks.values() if status)
        
        msg = f"<b>👥 Admin Statistics</b>\n\nTotal Users: {total_users}\nActive Tasks Running: {active_tasks}"
        bot.send_message(user_id, msg, parse_mode="HTML")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()