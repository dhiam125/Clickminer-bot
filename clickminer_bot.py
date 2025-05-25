
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = 8035703916:AAGWMl61OI-9t4CmEGzD3lNlS0HKpn7DH_c

# قاعدة البيانات
conn = sqlite3.connect("miner_bot.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    coins INTEGER DEFAULT 0,
    wallet_address TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS withdrawals (
    user_id INTEGER,
    coins INTEGER,
    status TEXT DEFAULT 'pending',
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()
conn.close()

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    conn = sqlite3.connect("miner_bot.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()
    await update.message.reply_text("أهلاً بك في ClickMiner!")

async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("miner_bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    coins = c.fetchone()[0]
    conn.close()
    await update.message.reply_text(f"تم التعدين! رصيدك الآن: {coins} عملة")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("miner_bot.db")
    c = conn.cursor()
    c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        await update.message.reply_text(f"رصيدك الحالي: {result[0]} عملة")
    else:
        await update.message.reply_text("الرجاء استخدام /start أولاً.")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("miner_bot.db")
    c = conn.cursor()
    c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    if result and result[0] >= 10:
        c.execute("INSERT INTO withdrawals (user_id, coins) VALUES (?, ?)", (user_id, result[0]))
        c.execute("UPDATE users SET coins = 0 WHERE user_id = ?", (user_id,))
        msg = f"تم طلب السحب {result[0]} عملة، سيتم المراجعة من قبل المسؤول."
    else:
        msg = "يجب أن تمتلك 10 عملات على الأقل للسحب."
    conn.commit()
    conn.close()
    await update.message.reply_text(msg)

# التشغيل
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mine", mine))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("withdraw", withdraw))

app.run_polling()
