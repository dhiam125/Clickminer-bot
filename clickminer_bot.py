import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# الحصول على التوكن من المتغير البيئي
TOKEN = os.environ.get("TOKEN")

# إعداد قاعدة البيانات
conn = sqlite3.connect("clickminer.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
''')
conn.commit()

# أوامر البوت
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    update.message.reply_text("🎮 مرحبًا بك في لعبة ClickMiner! استخدم /mine للتعدين. 💰")

def mine(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    cursor.execute("UPDATE users SET balance = balance + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()[0]
    update.message.reply_text(f"🪙 نقرت! رصيدك الآن: {balance} قطعة رقمية.")

def balance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        update.message.reply_text(f"💼 رصيدك الحالي: {result[0]} قطعة.")
    else:
        update.message.reply_text("❌ لم يتم العثور على حساب. استخدم /start أولاً.")

def withdraw(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result and result[0] >= 10:
        cursor.execute("UPDATE users SET balance = balance - 10 WHERE user_id = ?", (user_id,))
        conn.commit()
        update.message.reply_text("✅ تم سحب 10 عملات. سيتم تحويل المكافأة لاحقًا.")
    else:
        update.message.reply_text("❌ تحتاج إلى 10 عملات على الأقل للسحب.")

# التشغيل
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("mine", mine))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("withdraw", withdraw))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
