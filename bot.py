from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, MessageHandler, filters, ContextTypes, ConversationHandler, CommandHandler
import os

# Токен и ID админа
TOKEN = os.getenv("TELEGRAM_TOKEN", "8350872775:AAHAyQAvOooptvSx8xG-QbmgAJpGRvtUaBo")
ADMIN_ID = "6978852648"

# Состояния для вопросов
NAME, BUSINESS, GOAL, BUDGET, PHONE = range(5)

# Постоянное меню
def get_menu():
    keyboard = [
        [KeyboardButton("ℹ️ Обо мне"), KeyboardButton("🌐 Соцсети"), KeyboardButton("📞 Поделись номером", request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'started' not in context.user_data:
        context.user_data['started'] = True
        await update.message.reply_text(
            "Привет! Я Леонид (@shvorob_leonid), специалист по автоматизации бизнеса.\n\n"
            "Я задам тебе 4 простых вопроса, чтобы понять твои задачи и предложить решение.\n"
            "После ответов я свяжусь с тобой, чтобы всё обсудить.\n\n"
            "Вопрос 1 из 4: Как тебя зовут?",
            reply_markup=get_menu()
        )
        return NAME
    return None

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Вопрос 2 из 4: Какой у тебя бизнес? (Например, интернет-магазин, услуги, производство)", reply_markup=get_menu())
    return BUSINESS

async def business(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['business'] = update.message.text
    await update.message.reply_text("Вопрос 3 из 4: Что хочешь автоматизировать? (Например, заявки, рассылки, учет)", reply_markup=get_menu())
    return GOAL

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal'] = update.message.text
    await update.message.reply_text("Вопрос 4 из 4: Какой бюджет на автоматизацию? (Пример: 50-100 тыс. руб.)", reply_markup=get_menu())
    return BUDGET

async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['budget'] = update.message.text
    context.user_data['phone'] = "Не указан"
    
    # Отправляем уведомление админу
    await send_admin_notification(update, context)
    
    await update.message.reply_text(
        "Спасибо! Я получил твои данные и скоро свяжусь.\n"
        "Если хочешь, можешь поделиться номером телефона через кнопку ниже.",
        reply_markup=get_menu()
    )
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data['phone'] = update.message.contact.phone_number
        await send_admin_notification(update, context)
        await update.message.reply_text(
            "Спасибо за номер! Я получил твои данные и скоро свяжусь.",
            reply_markup=get_menu()
        )
    return PHONE

async def send_admin_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or "Не указан"
    user_id = update.effective_user.id
    message = (
        f"📩 Новый клиент!\n"
        f"🆔 Telegram ID: {user_id}\n"
        f"@ Ник: @{username}\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"🏢 Бизнес: {context.user_data['business']}\n"
        f"🎯 Цель автоматизации: {context.user_data['goal']}\n"
        f"💰 Бюджет: {context.user_data['budget']}\n"
        f"📞 Номер телефона: {context.user_data['phone']}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=message)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я Леонид, эксперт по автоматизации бизнес-процессов.\n"
        "Настраиваю no-code и low-code решения, чтобы твой бизнес работал быстрее и эффективнее.",
        reply_markup=get_menu()
    )

async def socials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Мои контакты:\n"
        "💬 Telegram: @shvorob_leonid\n"
        "📸 Instagram: @ShvorobLeonid",
        reply_markup=get_menu()
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Процесс отменён.", reply_markup=get_menu())
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
            PHONE: [MessageHandler(filters.CONTACT, phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("^(ℹ️ Обо мне)$"), about))
    app.add_handler(MessageHandler(filters.Regex("^(🌐 Соцсети)$"), socials))
    
    app.run_polling()

if __name__ == "__main__":
    main()
