import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("7614534867:AAFW6fSU3iJ6F3RRzAb4SyybiirGlYUZsh4")  # استدعاء التوكن من متغيرات البيئة
CHANNEL_ID = -1002512738615  # معرف القناة لإرسال إثباتات الدفع
bot = telebot.TeleBot(TOKEN)

# بيانات المستخدمين (محاكاة قاعدة بيانات بسيطة)
users_data = {}

# قائمة المنتجات
products = [
    {"name": "0.04 TON", "price": 5},
    {"name": "0.08 TON", "price": 10}
]

# التحقق من المستخدمين لمنع الحسابات المكررة
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id in users_data:
        bot.send_message(user_id, "🚫 لديك حساب مسجل بالفعل!")
    else:
        users_data[user_id] = {"points": 0, "referrals": []}
        bot.send_message(user_id, "✅ تم تسجيلك بنجاح! لديك 0 نقاط.")

# نظام الإحالة - كل إحالة تمنح 1 نقطة
@bot.message_handler(commands=['referral'])
def referral(message):
    user_id = message.chat.id
    referral_link = f"https://t.me/TON0001StoreBot?start={user_id}"
    bot.send_message(user_id, f"🔗 رابط الإحالة الخاص بك: {referral_link}\n🎁 لكل إحالة تحصل على 1 نقطة!")

@bot.message_handler(func=lambda message: message.text.startswith('/start '))
def handle_referral(message):
    referrer_id = int(message.text.split()[1])
    new_user_id = message.chat.id
    
    if new_user_id not in users_data:
        users_data[new_user_id] = {"points": 0, "referrals": []}
        if referrer_id in users_data and new_user_id not in users_data[referrer_id]["referrals"]:
            users_data[referrer_id]["points"] += 1
            users_data[referrer_id]["referrals"].append(new_user_id)
            bot.send_message(referrer_id, f"🎉 لقد حصلت على 1 نقطة لإحالة مستخدم جديد!\n💰 رصيدك الحالي: {users_data[referrer_id]['points']} نقاط")
    bot.send_message(new_user_id, "✅ تم تسجيلك بنجاح!")

# عرض المتجر
@bot.message_handler(commands=['shop'])
def show_shop(message):
    chat_id = message.chat.id
    keyboard = InlineKeyboardMarkup()
    for product in products:
        btn = InlineKeyboardButton(
            text=f"{product['name']} - {product['price']} نقاط 💰",
            callback_data=f"buy_{product['name']}_{product['price']}"
        )
        keyboard.add(btn)
    bot.send_message(chat_id, "🛒 **متجر العملات:**\nاختر السلعة التي تريد شراءها:", reply_markup=keyboard, parse_mode="Markdown")

# معالجة طلب الشراء
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def process_purchase(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    _, product_name, product_price = call.data.split("_")
    product_price = int(product_price)

    if users_data[user_id]["points"] >= product_price:
        users_data[user_id]["points"] -= product_price
        bot.send_message(chat_id, f"✅ **تم شراء {product_name} بنجاح!**\n💰 **رصيدك الحالي:** {users_data[user_id]['points']} نقاط")
        send_payment_proof(call.from_user.username, user_id, product_name, product_price)
    else:
        bot.send_message(chat_id, "❌ لديك نقاط غير كافية!")

# إرسال إثبات الدفع إلى القناة
def send_payment_proof(username, user_id, product, price):
    proof_message = f"""
✅ **تم تسليم طلب جديد!** ✅
📦 **الماركت:** @TON0001StoreBot 🤍
🏷 **السلعة:** {product}
💰 **السعر:** {price} نقاط
👤 **المشتري:** {username}
🆔 **الأيدي:** {user_id}
🔗 **قناة الإثباتات:** [ton_bot_money](https://t.me/ton_bot_money)
    """
    bot.send_message(CHANNEL_ID, proof_message, parse_mode="Markdown")

# إضافة نقاط للمستخدم (للاختبار فقط)
@bot.message_handler(commands=['add_points'])
def add_points(message):
    user_id = message.chat.id
    if user_id not in users_data:
        users_data[user_id] = {"points": 0, "referrals": []}
    users_data[user_id]["points"] += 10
    bot.send_message(user_id, f"🎁 تمت إضافة 10 نقاط! رصيدك الحالي: {users_data[user_id]['points']}")

bot.polling()
