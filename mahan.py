import json
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

BOT_TOKEN = "7766760437:AAFj-vuC3jz3uOLNlAc3sxW4WioPDnQS-2M"
ADMIN_CHAT_ID = 961854122  # جایگزین کن با chat_id شما

STUDENTS_FILE = "students.json"
if not os.path.exists(STUDENTS_FILE):
    with open(STUDENTS_FILE, "w") as f:
        json.dump({}, f)

# مراحل گفتگوها
(
    STUDENT_ID,
    STUDENT_PASS,
    ADMIN_ADD_ID,
    ADMIN_ADD_NAME,
    ADMIN_ADD_PASS,
    ADMIN_UPDATE_ID,
    ADMIN_UPDATE_GRADE,
    ADMIN_DELETE_ID,
) = range(8)

# دکمه‌های منو
student_menu = [["ورود به سامانه"]]
admin_menu = [["افزودن دانشجو", "تغییر نمره"], ["اطلاعات دانشجوها", "حذف دانشجو"]]

# تابع برای بارگذاری دیتا
def load_students():
    with open(STUDENTS_FILE, "r") as f:
        return json.load(f)

def save_students(data):
    with open(STUDENTS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    if user_id == ADMIN_CHAT_ID:
        await update.message.reply_text("خوش آمدید مدیر محترم.", reply_markup=ReplyKeyboardMarkup(admin_menu, resize_keyboard=True))
    else:
        await update.message.reply_text("سلام دانشجو! گزینه مورد نظر را انتخاب کن.", reply_markup=ReplyKeyboardMarkup(student_menu, resize_keyboard=True))

# دانشجو وارد می‌شود
async def student_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("شماره دانشجویی خود را وارد کنید:")
    return STUDENT_ID

async def student_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["student_id"] = update.message.text.strip()
    students = load_students()
    if context.user_data["student_id"] not in students:
        await update.message.reply_text("❌ شماره دانشجویی یافت نشد.")
        return ConversationHandler.END
    await update.message.reply_text("رمز عبور را وارد کنید:")
    return STUDENT_PASS

async def student_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    std_id = context.user_data["student_id"]
    students = load_students()
    if students[std_id]["password"] == password:
        grade = students[std_id].get("grade", "ثبت نشده")
        await update.message.reply_text(f"✅ خوش آمدی {students[std_id]['name']}!\nنمره شما: {grade}")
    else:
        await update.message.reply_text("❌ رمز عبور اشتباه است.")
    return ConversationHandler.END

# افزودن دانشجو توسط ادمین
async def admin_add_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("شماره دانشجویی دانشجو را وارد کنید:")
    return ADMIN_ADD_ID

async def admin_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_id"] = update.message.text.strip()
    await update.message.reply_text("نام دانشجو را وارد کنید:")
    return ADMIN_ADD_NAME

async def admin_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_name"] = update.message.text.strip()
    await update.message.reply_text("رمز عبور اولیه را وارد کنید:")
    return ADMIN_ADD_PASS

async def admin_add_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = load_students()
    std_id = context.user_data["add_id"]
    students[std_id] = {
        "name": context.user_data["add_name"],
        "password": update.message.text.strip(),
        "grade": None
    }
    save_students(students)
    await update.message.reply_text(f"✅ دانشجو با شماره {std_id} افزوده شد.")
    return ConversationHandler.END

# تغییر نمره
async def admin_update_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("شماره دانشجویی مورد نظر را وارد کنید:")
    return ADMIN_UPDATE_ID

async def admin_update_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["update_id"] = update.message.text.strip()
    await update.message.reply_text("نمره جدید را وارد کنید:")
    return ADMIN_UPDATE_GRADE

async def admin_update_grade_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    std_id = context.user_data["update_id"]
    grade = float(update.message.text.strip())
    students = load_students()
    if std_id in students:
        students[std_id]["grade"] = grade
        save_students(students)
        await update.message.reply_text(f"✅ نمره دانشجو {students[std_id]['name']} به {grade} تغییر کرد.")
    else:
        await update.message.reply_text("❌ شماره دانشجویی یافت نشد.")
    return ConversationHandler.END

# حذف دانشجو توسط ادمین
async def admin_delete_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("شماره دانشجویی دانشجویی که می‌خواهید حذف کنید را وارد کنید:")
    return ADMIN_DELETE_ID

async def admin_delete_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    std_id = update.message.text.strip()
    students = load_students()
    if std_id in students:
        del students[std_id]
        save_students(students)
        await update.message.reply_text(f"✅ دانشجو با شماره {std_id} حذف شد.")
    else:
        await update.message.reply_text("❌ شماره دانشجویی یافت نشد.")
    return ConversationHandler.END

# نمایش لیست دانشجوها
async def admin_list_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = load_students()
    msg = "📋 لیست دانشجویان:\n"
    for sid, info in students.items():
        grade = info.get("grade", "ثبت نشده")
        msg += f"{sid} - {info['name']} - نمره: {grade}\n"
    await update.message.reply_text(msg)

# لغو
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # دانشجو
    student_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(ورود به سامانه)$"), student_login)],
        states={
            STUDENT_ID: [MessageHandler(filters.TEXT, student_id)],
            STUDENT_PASS: [MessageHandler(filters.TEXT, student_pass)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # افزودن دانشجو
    add_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(افزودن دانشجو)$") & filters.Chat(chat_id=ADMIN_CHAT_ID), admin_add_student)],
        states={
            ADMIN_ADD_ID: [MessageHandler(filters.TEXT, admin_add_id)],
            ADMIN_ADD_NAME: [MessageHandler(filters.TEXT, admin_add_name)],
            ADMIN_ADD_PASS: [MessageHandler(filters.TEXT, admin_add_pass)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # تغییر نمره
    update_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(تغییر نمره)$") & filters.Chat(chat_id=ADMIN_CHAT_ID), admin_update_grade)],
        states={
            ADMIN_UPDATE_ID: [MessageHandler(filters.TEXT, admin_update_id)],
            ADMIN_UPDATE_GRADE: [MessageHandler(filters.TEXT, admin_update_grade_final)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # حذف دانشجو
    delete_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(حذف دانشجو)$") & filters.Chat(chat_id=ADMIN_CHAT_ID), admin_delete_student)],
        states={
            ADMIN_DELETE_ID: [MessageHandler(filters.TEXT, admin_delete_id)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(student_conv)
    app.add_handler(add_conv)
    app.add_handler(update_conv)
    app.add_handler(delete_conv)
    app.add_handler(MessageHandler(filters.Regex("^(اطلاعات دانشجوها)$") & filters.Chat(chat_id=ADMIN_CHAT_ID), admin_list_students))

    print("ربات اجرا شد ✅")
    app.run_polling()
