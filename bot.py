import telebot
import os
from flask import Flask, request

TOKEN = os.getenv("7614534867:AAFW6fSU3iJ6F3RRzAb4SyybiirGlYUZsh4")  # استدعاء التوكن من متغيرات البيئة
CHANNEL_ID = -1002512738615  # معرف القناة لإرسال إثباتات الدفع
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # رابط Webhook الخاص بـ Vercel
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# بيانات المستخدمين (محاكاة قاعدة بيانات بسيطة)
users_data = {}
referrals = {}

# قائمة المنتجات
products = [
    {"name": "0.04 TON", "price": 5},
    {"name": "0.08 TON", "price": 10}
]

# التحقق من المستخدمين لمنع الحسابات المكررة وإضافة الإحالات
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    referrer_id = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if user_id in users_data:
        bot.send_message(user_id, "🚫 لديك حساب مسجل بالفعل!")
    else:
        users_data[user_id] = {"points": 0}
        bot.send_message(user_id, "✅ تم تسجيلك بنجاح! لديك 0 نقاط.")
        
        # إضافة نقاط للإحالة
        if referrer_id and referrer_id.isdigit():
            referrer_id = int(referrer_id)
            if referrer_id in users_data:
                users_data[referrer_id]["points"] += 1
                bot.send_message(referrer_id, "🎉 لقد حصلت على 1 نقطة بسبب إحالة جديدة!")

# عرض المتجر
@bot.message_handler(commands=['shop'])
def show_shop(message):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    for product in products:
        btn = telebot.types.InlineKeyboardButton(
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
        users_data[user_id] = {"points": 0}
    users_data[user_id]["points"] += 10
    bot.send_message(user_id, f"🎁 تمت إضافة 10 نقاط! رصيدك الحالي: {users_data[user_id]['points']}")

# إعداد Webhook
@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'Received', 200

@server.route('/')
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    return 'Webhook Set!', 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
