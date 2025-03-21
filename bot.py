import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import os

# 🔹 جلب متغيرات البيئة
TOKEN = os.getenv("TOKEN")  # توكن البوت
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "webhook_endpoint")  # مسار Webhook
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # معرف قناة إثباتات الدفع
PORT = int(os.getenv("PORT", 5000))  # البورت الافتراضي

# 🔹 تهيئة البوت
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 🔹 بيانات المستخدمين (محاكاة قاعدة بيانات)
users_data = {}

# 🔹 قائمة المنتجات
products = [
    {"name": "0.04 TON", "price": 5},
    {"name": "0.08 TON", "price": 10}
]

# ✅ التحقق من الإحالة
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    referral_id = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if user_id not in users_data:
        users_data[user_id] = {"points": 0, "referrals": 0}
        bot.send_message(user_id, "✅ **تم تسجيلك بنجاح!** لديك 0 نقاط.")
        
        # إذا كان هناك إحالة، أضف نقطة للمُحيل
        if referral_id and referral_id.isdigit():
            referral_id = int(referral_id)
            if referral_id in users_data:
                users_data[referral_id]["points"] += 1
                users_data[referral_id]["referrals"] += 1
                bot.send_message(referral_id, f"🎉 حصلت على 1 نقطة بسبب إحالة جديدة!\n💰 رصيدك: {users_data[referral_id]['points']} نقطة.")
    else:
        bot.send_message(user_id, "🚫 لديك حساب مسجل بالفعل!")

# 🛒 عرض المتجر
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

# 🛍️ معالجة طلب الشراء
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def process_purchase(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    _, product_name, product_price = call.data.split("_")
    product_price = int(product_price)

    if users_data.get(user_id, {}).get("points", 0) >= product_price:
        users_data[user_id]["points"] -= product_price
        bot.send_message(chat_id, f"✅ **تم شراء {product_name} بنجاح!**\n💰 **رصيدك الحالي:** {users_data[user_id]['points']} نقاط")
        send_payment_proof(call.from_user.username, user_id, product_name, product_price)
    else:
        bot.send_message(chat_id, "❌ لديك نقاط غير كافية!")

# 📌 إرسال إثبات الدفع إلى القناة
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

# 🎁 إضافة نقاط للمستخدم (للاختبار فقط)
@bot.message_handler(commands=['add_points'])
def add_points(message):
    user_id = message.chat.id
    users_data.setdefault(user_id, {"points": 0})
    users_data[user_id]["points"] += 10
    bot.send_message(user_id, f"🎁 تمت إضافة 10 نقاط! رصيدك الحالي: {users_data[user_id]['points']}")

# 🌐 نقطة الدخول لـ Webhook
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# 🚀 تشغيل التطبيق على Vercel
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
