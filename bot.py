import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import os

TOKEN = os.getenv("7614534867:AAFW6fSU3iJ6F3RRzAb4SyybiirGlYUZsh4")  # استدعاء التوكن من متغيرات البيئة
CHANNEL_ID = -1002512738615  # معرف القناة لإرسال إثباتات الدفع
bot = telebot.TeleBot(TOKEN)

# إعداد Flask
app = Flask(__name__)

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
        users_data[user_id] = {"points": 0}
        bot.send_message(user_id, "✅ تم تسجيلك بنجاح! لديك 0 نقاط.")

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
        users_data[user_id] = {"points": 0}
    users_data[user_id]["points"] += 10
    bot.send_message(user_id, f"🎁 تمت إضافة 10 نقاط! رصيدك الحالي: {users_data[user_id]['points']}")

# نقطة الدخول لـ Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

# تشغيل التطبيق
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
