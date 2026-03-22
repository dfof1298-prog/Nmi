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

stopuser = {}
token = "8519473125:AAFEcTaZkeZQ8P6NNtzxfVtLkUO7UZ77QiA"  # توكنك هنا
bot = telebot.TeleBot(token, parse_mode="HTML")
admin = 1093032296  # ايدي الادمن
active_scans = set()
command_usage = {}

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

@bot.message_handler(commands=["start"])
def start(message):
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
للاشتراك و الاستفسار : @FJ0FF
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

@bot.message_handler(content_types=["document"])
def handle_document(message):
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
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/FJ0FF")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>
اهلا بك عزيزي
البوت مدفوع وليس مجاني وسعر الاشتراك لليوم الكامل 2$
للاشتراك و الاستفسار : @FJ0FF
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
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/FJ0FF")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>
اهلا بك عزيزي
البوت مدفوع وليس مجاني وسعر الاشتراك لليوم الكامل 2$
للاشتراك و الاستفسار : @FJ0FF
</b>
        ''', reply_markup=keyboard)
        return

    current_time = datetime.now()
    required_duration = timedelta(hours=0)
    if current_time - provided_time > required_duration:
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/FJ0FF")
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
        bot.reply_to(message, "ما تقدر تفحص اكثر من ملف بنفس الوقت انتظر الملف الاول يخلص فحص او انت وقفه و بعدين تعال افحص الملف الثاني")
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
𝘽𝙤𝙩 𝘽𝙮 @FJ0FF''',
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
• Bot By : @FJ0FF</b>'''
                        bot.send_message(call.from_user.id, msg_approved)
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
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/FJ0FF")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>
اهلا بك عزيزي >> {name}
البوت مدفوع وليس مجاني وسعر الاشتراك لليوم الكامل 2$
للاشتراك و الاستفسار : @FJ0FF
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
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/FJ0FF")
        keyboard.add(contact_button)
        bot.send_message(chat_id=message.chat.id, text=f'''<b>
اهلا بك عزيزي >> {name}
البوت مدفوع وليس مجاني وسعر الاشتراك لليوم الكامل 2$
للاشتراك و الاستفسار : @FJ0FF
</b>
        ''', reply_markup=keyboard)
        return

    current_time = datetime.now()
    required_duration = timedelta(hours=0)
    if current_time - provided_time > required_duration:
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ 𝗢𝗪𝗡𝗘𝗥  ✨", url="https://t.me/FJ0FF")
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
• Bot By : @FJ0FF</b>'''

    msg_ccn = f'''<b>CCN ☑️

• Card : <code>{cc}</code>
• Response : {raw_response}
• Gateway : {gate}
{info}
• Time : {"{:.1f}".format(execution_time)}
• Bot By : @FJ0FF</b>'''

    msg_declined = f'''<b>Declined ❌

• Card : <code>{cc}</code>
• Response : {raw_response}
• Gateway : {gate}		
{info}
• Time : {"{:.1f}".format(execution_time)}
• Bot By : @FJ0FF</b>'''

    if category == 'approved':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg_approved)
    elif category == 'ccn':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg_ccn)
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg_declined)

@bot.message_handler(func=lambda message: message.text.lower().startswith('.redeem') or message.text.lower().startswith('/redeem'))
def redeem(message):
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
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"حدث خطأ: {e}")
