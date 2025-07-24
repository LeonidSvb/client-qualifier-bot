from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, filters, ContextTypes, ConversationHandler
import os

# Токен и ID админа
TOKEN = os.getenv("TELEGRAM_TOKEN", "8350872775:AAHAyQAvOooptvSx8xG-QbmgAJpGRvtUaBo")
ADMIN_ID = "6978852648"

# Состояния для вопросов
NAME, BUSINESS, GOAL, BUDGET = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'started' not in context.user_data:
        context.user_data['started'] = True
        await update.message.reply_text(
            "👋 Привет! Я Леонид (@shvorob_leonid), помогу автоматизировать твой бизнес! 🚀 "
            "Ответь на пару вопросов, чтобы я сразу получил всю нужную информацию. "
            "Как только ты заполнишь, я свяжусь с тобой, и мы всё обсудим. 😊 Как тебя зовут?"
        )
        return NAME
    return None

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Какой у тебя бизнес? (Например, интернет-магазин, услуги, производство)")
    return BUSINESS

async def business(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['business'] = update.message.text
    await update.message.reply_text("Что хочешь автоматизировать? (Например, заявки, рассылки, учет)")
    return GOAL

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal'] = update.message.text
    await update.message.reply_text("Какой бюджет на автоматизацию? (Пример: 50-100 тыс. руб.)")
    return BUDGET

async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['budget'] = update.message.text
    
    # Уведомление админу
    message = (
        f"📩 Новый клиент!\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"🏢 Бизнес: {context.user_data['business']}\n"
        f"🎯 Цель автоматизации: {context.user_data['goal']}\n"
        f"💰 Бюджет: {context.user_data['budget']}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    
    # Меню
    keyboard = [
        [KeyboardButton("ℹ️ Обо мне"), KeyboardButton("🌐 Соцсети")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Спасибо! Я получил твои данные и скоро свяжусь. 😊 Выбери опцию:", reply_markup=reply_markup)
    return ConversationHandler.END

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Я Леонид, эксперт по автоматизации бизнес-процессов. Настраиваю no-code/low-code решения, чтобы твой бизнес работал эффективнее! 🚀"
    )

async def socials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 Мои соцсети:\n"
        "💬 Telegram: @shvorob_leonid\n"
        "📸 Instagram: @shvorob_leonid"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Процесс отменён.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            BUSINESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, business)],
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, goal)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("^(ℹ️ Обо мне)$"), about))
    app.add_handler(MessageHandler(filters.Regex("^(🌐 Соцсети)$"), socials))
    
    app.run_polling()

if __name__ == "__main__":
    main()
