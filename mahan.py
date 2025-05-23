import json
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

BOT_TOKEN = ""
ADMIN_CHAT_IDS = {1111111, 123456789}  # اینجا میشه چند تا ادمین رو اضاف کرد

STUDENTS_FILE = "students.json"
if not os.path.exists(STUDENTS_FILE):
    with open(STUDENTS_FILE, "w") as f:
        json.dump({}, f)

# مراحل گفتگوها
(
    STUDENT_ID,
    STUDENT_PASS,
    STUDENT_PASS_CURRENT,
    STUDENT_PASS_NEW,
    STUDENT_PASS_CONFIRM,
    ADMIN_ADD_ID,
    ADMIN_ADD_NAME,
    ADMIN_ADD_GRADE,
    ADMIN_UPDATE_ID,
    ADMIN_UPDATE_GRADE,
    ADMIN_DELETE_ID,
) = range(11)

# دکمه‌های منو دستکاری شه کار نمیکنه زنجیروار به هم متصلن
student_menu = [["ورود به سامانه"]]
student_logged_in_menu = [["تغییر رمز عبور", "خروج"]]
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
    if user_id in ADMIN_CHAT_IDS:
        await update.message.reply_text("خوش آمدید مدیر محترم.", reply_markup=ReplyKeyboardMarkup(admin_menu, resize_keyboard=True))
    else:
        await update.message.reply_text("سلام دانشجو! گزینه مورد نظر را انتخاب کن.", reply_markup=ReplyKeyboardMarkup(student_menu, resize_keyboard=True))

# دانشجو وارد می‌شود
async def student_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("شماره دانشجویی خود را وارد کنید:")
    return STUDENT_ID

async def student_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    std_id = update.message.text.strip()
    students = load_students()
    if std_id not in students:
        await update.message.reply_text("❌ شماره دانشجویی یافت نشد.")
        return ConversationHandler.END
    context.user_data["student_id"] = std_id
    await update.message.reply_text("رمز عبور خود را وارد کنید:")
    return STUDENT_PASS

async def student_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    std_id = context.user_data["student_id"]
    students = load_students()
    if students[std_id]["password"] == password:
        context.user_data["student_id"] = std_id
        grade = students[std_id].get("grade", "ثبت نشده")
        name = students[std_id].get("name", "")
        await update.message.reply_text(
            f"✅ خوش آمدید {name}!\nنمره شما: {grade}",
            reply_markup=ReplyKeyboardMarkup(student_logged_in_menu, resize_keyboard=True)
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ رمز عبور اشتباه است. لطفاً دوباره شماره دانشجویی خود را وارد کنید:")
        return STUDENT_ID

from telegram import ReplyKeyboardMarkup

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
    await update.message.reply_text("نمره دانشجو را وارد کنید:")
    return ADMIN_ADD_GRADE

async def admin_add_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    grade_text = update.message.text.strip()
    try:
        grade = float(grade_text)
    except ValueError:
        await update.message.reply_text("❌ لطفاً نمره را به صورت عددی وارد کنید:")
        return ADMIN_ADD_GRADE

    context.user_data["add_grade"] = grade

    students = load_students()
    std_id = context.user_data["add_id"]
    students[std_id] = {
        "name": context.user_data["add_name"],
        "password": "Aa123456",
        "grade": grade
    }
    save_students(students)
    await update.message.reply_text(f"✅ دانشجو با شماره {std_id} افزوده شد.\nرمز عبور پیش‌فرض: Aa123456")
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
        password = info.get("password", "ثبت نشده")
        msg += (
            f"شماره دانشجویی: {sid}\n"
            f"نام: {info['name']}\n"
            f"نمره: {grade}\n"
            f"رمز عبور: {password}\n"
            f"---\n"
        )
    await update.message.reply_text(msg)

# لغو
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

# هندلر منوی دانشجو پس از ورود
async def student_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "تغییر رمز عبور":
        await update.message.reply_text("رمز عبور فعلی خود را وارد کنید:")
        return STUDENT_PASS_CURRENT
    elif text == "خروج":
        await update.message.reply_text("از سیستم خارج شدید.", reply_markup=ReplyKeyboardMarkup(student_menu, resize_keyboard=True))
        return ConversationHandler.END
    else:
        await update.message.reply_text("گزینه نامعتبر است. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END

# مراحل تغییر رمز عبور
async def student_pass_current(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Entered student_pass_current")
    current_pass = update.message.text.strip()
    std_id = context.user_data["student_id"]
    students = load_students()
    if students[std_id]["password"] == current_pass:
        await update.message.reply_text("رمز عبور جدید را وارد کنید:")
        return STUDENT_PASS_NEW
    else:
        await update.message.reply_text("❌ رمز عبور فعلی اشتباه است. دوباره وارد کنید:")
        return STUDENT_PASS_CURRENT

async def student_pass_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_pass = update.message.text.strip()
    context.user_data["new_password"] = new_pass
    await update.message.reply_text("رمز عبور جدید را دوباره وارد کنید برای تایید:")
    return STUDENT_PASS_CONFIRM

async def student_pass_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    confirm_pass = update.message.text.strip()
    new_pass = context.user_data.get("new_password")
    if confirm_pass == new_pass:
        std_id = context.user_data["student_id"]
        students = load_students()
        students[std_id]["password"] = new_pass
        save_students(students)
        await update.message.reply_text("✅ رمز عبور با موفقیت تغییر کرد.", reply_markup=ReplyKeyboardMarkup(student_logged_in_menu, resize_keyboard=True))
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ رمز عبورها تطابق ندارند. دوباره رمز جدید را وارد کنید:")
        return STUDENT_PASS_NEW

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # دانشجو
    student_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(ورود به سامانه)$"), student_login)],
        states={
            STUDENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_id)],
            STUDENT_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_pass)],
            STUDENT_PASS_CURRENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_pass_current)],
            STUDENT_PASS_NEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_pass_new)],
            STUDENT_PASS_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_pass_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    change_pass_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(تغییر رمز عبور)$"), student_menu_handler)],
        states={
            STUDENT_PASS_CURRENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_pass_current)],
            STUDENT_PASS_NEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_pass_new)],
            STUDENT_PASS_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_pass_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # افزودن دانشجو
    add_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(افزودن دانشجو)$") & filters.Chat(chat_id=ADMIN_CHAT_IDS), admin_add_student)],
        states={
            ADMIN_ADD_ID: [MessageHandler(filters.TEXT, admin_add_id)],
            ADMIN_ADD_NAME: [MessageHandler(filters.TEXT, admin_add_name)],
            ADMIN_ADD_GRADE: [MessageHandler(filters.TEXT, admin_add_grade)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # تغییر نمره
    update_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(تغییر نمره)$") & filters.Chat(chat_id=ADMIN_CHAT_IDS), admin_update_grade)],
        states={
            ADMIN_UPDATE_ID: [MessageHandler(filters.TEXT, admin_update_id)],
            ADMIN_UPDATE_GRADE: [MessageHandler(filters.TEXT, admin_update_grade_final)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # حذف دانشجو
    delete_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(حذف دانشجو)$") & filters.Chat(chat_id=ADMIN_CHAT_IDS), admin_delete_student)],
        states={
            ADMIN_DELETE_ID: [MessageHandler(filters.TEXT, admin_delete_id)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(student_conv)
    app.add_handler(change_pass_conv)
    app.add_handler(add_conv)
    app.add_handler(update_conv)
    app.add_handler(delete_conv)
    app.add_handler(MessageHandler(filters.Regex("^(اطلاعات دانشجوها)$") & filters.Chat(chat_id=ADMIN_CHAT_IDS), admin_list_students))
    app.add_handler(MessageHandler(filters.Regex("^(خروج)$"), student_menu_handler))

    print("runing🤪")
    app.run_polling()
