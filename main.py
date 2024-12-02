from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import sqlite3
import random

# اتصال به پایگاه داده SQLite
db_name = 'user_data.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# ایجاد جدول برای ذخیره اطلاعات کاربر
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    registered INTEGER DEFAULT 0
)
''')

cursor.execute("PRAGMA table_info(users);")
columns = [column[1] for column in cursor.fetchall()]
if 'registered' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN registered INTEGER DEFAULT 1;")
else:
    {

    }

conn.commit()

# سوالات آزمون
questions = [
    {"question": "پایتون چیست و چه کاربردهایی دارد؟", "options": ["زبان برنامه‌نویسی", "سیستم‌عامل", "سرویس وب", "پایگاه داده"], "answer": 0},
    {"question": "نحوه تعریف یک متغیر در پایتون چگونه است؟", "options": ["variable x = 10", "x := 10", "x = 10", "let x = 10"], "answer": 2},
    {"question": "چگونه یک رشته (string) در پایتون تعریف می‌شود؟", "options": ["\"Hello\"", "Hello", "\"Hello'", "'Hello\""], "answer": 0},
    {"question": "تفاوت بین int و float چیست؟", "options": ["int عدد صحیح است و float عدد اعشاری", "هر دو یکسان هستند", "int عدد اعشاری است و float عدد صحیح", "هیچکدام"], "answer": 0},
    {"question": "چگونه یک لیست در پایتون ایجاد می‌شود؟", "options": ["()", "{}", "[]", "<>"], "answer": 2},
    {"question": "نحوه دسترسی به عناصر یک لیست چگونه است؟", "options": ["list.element()", "list[element]", "list[element:]", "element in list"], "answer": 1},
    {"question": "یک دیکشنری در پایتون چیست و چطور می‌توان آن را تعریف کرد؟", "options": ["{}", "[]", "()", "<>"], "answer": 0},
    {"question": "عملگر == چه تفاوتی با = دارد؟", "options": ["== برای مقایسه استفاده می‌شود و = برای انتساب", "= برای مقایسه استفاده می‌شود و == برای انتساب", "هر دو برای انتساب هستند", "هر دو برای مقایسه هستند"], "answer": 0},
    {"question": "چگونه می‌توان طول یک لیست را پیدا کرد؟", "options": ["len(list)", "length(list)", "list.length()", "list.len()"], "answer": 0},
    {"question": "عملگرهای منطقی در پایتون چه مواردی هستند؟", "options": ["&&, ||", "and, or, not", "&&, ||, !", "and, or"], "answer": 1},
    {"question": "نحوه استفاده از دستور if برای شرط‌گذاری چگونه است؟", "options": ["if condition: pass", "if condition then pass", "if condition {pass}", "if (condition) {pass}"], "answer": 0},
    {"question": "چگونه می‌توان یک حلقه for نوشت که از 1 تا 10 را چاپ کند؟", "options": ["for i in range(1, 10): print(i)", "for i in range(10): print(i+1)", "for i in 1 to 10: print(i)", "for i in 10: print(i)"], "answer": 1},
    {"question": "عملگر and و or چه کاربردهایی دارند؟", "options": ["برای مقایسه دو مقدار", "برای انجام عملیات منطقی", "برای تقسیم دو عدد", "برای اضافه کردن دو مقدار"], "answer": 1},
    {"question": "چگونه می‌توان یک حلقه while نوشت که 10 بار تکرار شود؟", "options": ["while i < 10: print(i)", "while i < 10: i += 1", "while i < 10: print(i); i += 1", "for i in range(10): print(i)"], "answer": 2},
    {"question": "نحوه استفاده از دستور break در حلقه‌ها چگونه است؟", "options": ["به حلقه پایان می‌دهد", "یک حلقه را ادامه می‌دهد", "یک شرط را تغییر می‌دهد", "چیزی چاپ نمی‌کند"], "answer": 0},
    {"question": "تفاوت بین append() و extend() در لیست‌ها چیست؟", "options": ["append() یک عنصر را اضافه می‌کند و extend() یک لیست را به لیست دیگر اضافه می‌کند", "append() یک لیست را اضافه می‌کند و extend() یک عنصر را اضافه می‌کند", "هر دو مشابه هستند", "append() برای لیست‌ها و extend() برای دیکشنری‌ها استفاده می‌شود"], "answer": 0},
    {"question": "چگونه می‌توان یک تابع در پایتون تعریف کرد؟", "options": ["function my_function():", "my_function(): def", "def my_function():", "define my_function():"], "answer": 2},
    {"question": "نحوه فراخوانی یک تابع و ارسال آرگومان به آن چگونه است؟", "options": ["my_function()", "my_function(arg1, arg2)", "call my_function()", "function my_function()"], "answer": 1},
    {"question": "چگونه می‌توان یک رشته را به حروف بزرگ تبدیل کرد؟", "options": ["upper()", "toUpperCase()", "capitalize()", "lower()"], "answer": 0},
    {"question": "چگونه می‌توان در پایتون یک متغیر را حذف کرد؟", "options": ["remove()", "del", "clear()", "discard()"], "answer": 1},
    {"question": "نحوه استفاده از len() برای یافتن تعداد عناصر یک لیست چگونه است؟", "options": ["len(list)", "list.len()", "length(list)", "list.count()"], "answer": 0},
    {"question": "چگونه می‌توان عناصر یک لیست را معکوس کرد؟", "options": ["list.reverse()", "list.flip()", "reverse(list)", "list[::-1]"], "answer": 0},
    {"question": "نحوه بازگشت از یک تابع و بازگرداندن یک مقدار چگونه است؟", "options": ["return value", "yield value", "send value", "output value"], "answer": 0},
    {"question": "چگونه می‌توان با استفاده از input() از کاربر ورودی گرفت؟", "options": ["input('Enter value: ')", "read_input('Enter value: ')", "get_input('Enter value: ')", "input_value('Enter value: ')"], "answer": 0},
    {"question": "چگونه می‌توان یک رشته را به عدد صحیح (integer) تبدیل کرد؟", "options": ["int(string)", "float(string)", "str(string)", "eval(string)"], "answer": 0},
    {"question": "چگونه می‌توان یک ماژول در پایتون وارد کرد؟", "options": ["import module_name", "include module_name", "use module_name", "require module_name"], "answer": 0},
    {"question": "ماژول math برای چه کارهایی استفاده می‌شود؟", "options": ["برای انجام عملیات ریاضی", "برای کار با رشته‌ها", "برای ایجاد وب‌سایت", "برای پردازش فایل‌ها"], "answer": 0},
    {"question": "چگونه می‌توان از تابع range() در یک حلقه استفاده کرد؟", "options": ["range(start, stop)", "range(start, stop, step)", "for i in range(start, stop):", "range(start)"], "answer": 2},
    {"question": "چگونه می‌توان از تابع sum() برای جمع‌زدن عناصر یک لیست استفاده کرد؟", "options": ["sum(list)", "list.sum()", "add(list)", "total(list)"], "answer": 0},
    {"question": "چگونه می‌توان از تابع max() و min() استفاده کرد؟", "options": ["max(list), min(list)", "list.max(), list.min()", "max, min functions", "max(list) and min(list)"], "answer": 0},
    {"question": "نحوه استفاده از دستور import برای وارد کردن یک ماژول چگونه است؟", "options": ["import module_name", "use module_name", "include module_name", "require module_name"], "answer": 0},
    {"question": "چگونه می‌توان طول یک رشته را پیدا کرد؟", "options": ["len(string)", "string.len()", "length(string)", "string.count()"], "answer": 0},
    {"question": "چگونه می‌توان یک لیست را مرتب کرد؟", "options": ["list.sort()", "sort(list)", "sorted(list)", "list.order()"], "answer": 0},
    {"question": "چگونه می‌توان یک فایل را در پایتون خواند؟", "options": ["open(file_path, 'r')", "file.read()", "read(file_path)", "open(file_path)"], "answer": 0},
    {"question": "نحوه نوشتن یک حلقه while در پایتون چگونه است؟", "options": ["while condition: pass", "while (condition): pass", "while condition pass", "while {condition} pass"], "answer": 0},
    {"question": "چه زمانی از break استفاده می‌شود؟", "options": ["برای خروج از یک حلقه", "برای ادامه یک حلقه", "برای اضافه کردن شرط‌ها", "برای متوقف کردن یک تابع"], "answer": 0},
    {"question": "نحوه تبدیل یک عدد اعشاری به عدد صحیح در پایتون چگونه است؟", "options": ["int(number)", "float(number)", "str(number)", "round(number)"], "answer": 0},
    {"question": "چگونه می‌توان یک کلمه را در یک رشته جستجو کرد؟", "options": ["search('word', string)", "string.find('word')", "string.search('word')", "find('word', string)"], "answer": 1},
    {"question": "چه چیزی در پایتون برای نشان دادن یک بلوک کد استفاده می‌شود؟", "options": ["{} brackets", "()", "indentation", "[] brackets"], "answer": 2},
    {"question": "عملگر % در پایتون چه کار می‌کند؟", "options": ["برای تقسیم استفاده می‌شود", "برای محاسبه باقی‌مانده استفاده می‌شود", "برای جمع استفاده می‌شود", "برای مقایسه استفاده می‌شود"], "answer": 1},
    {"question": "چگونه می‌توان یک متغیر را در پایتون مقداردهی اولیه کرد؟", "options": ["var x = 5", "x = 5", "let x = 5", "int x = 5"], "answer": 1},
    {"question": "چگونه می‌توان از یک متغیر استفاده کرد و مقدار آن را چاپ کرد؟", "options": ["print(x)", "echo x", "console.log(x)", "show(x)"], "answer": 0},
    {"question": "چگونه می‌توان یک تابع را بدون پارامتر در پایتون تعریف کرد؟", "options": ["def function_name():", "function function_name():", "define function_name():", "func function_name(): "], "answer": 0},
    {"question": "چگونه می‌توان از حلقه for برای چاپ اعداد از 0 تا 5 استفاده کرد؟", "options": ["for i in range(5): print(i)", "for i in range(0, 6): print(i)", "for i in 0 to 5: print(i)", "for i in range(6): print(i)"], "answer": 1},
    {"question": "چگونه می‌توان یک رشته را به لیست تبدیل کرد؟", "options": ["str.split()", "list(string)", "split(string)", "string.list()"], "answer": 0},
    {"question": "چگونه می‌توان در پایتون از یک حلقه نامحدود استفاده کرد؟", "options": ["for i in range():", "while True:", "while 1:", "for i in infinity:"], "answer": 1},
    {"question": "چگونه می‌توان در پایتون از دستور continue استفاده کرد؟", "options": ["برای متوقف کردن یک حلقه", "برای ادامه اجرای حلقه", "برای بازگشت به ابتدای تابع", "برای پایان دادن به یک شرط"], "answer": 1},
    {"question": "چگونه می‌توان تعداد تکرار یک عنصر در یک لیست را پیدا کرد؟", "options": ["list.count(element)", "element.count(list)", "list.size(element)", "count(list, element)"], "answer": 0},
    {"question": "چگونه می‌توان یک رشته را با استفاده از متد replace() تغییر داد؟", "options": ["string.replace(old, new)", "string.replace(new, old)", "string.change(old, new)", "replace(string, old, new)"], "answer": 0},
    {"question": "چه نوع داده‌ای برای ذخیره مجموعه‌ای از مقادیر منحصر به فرد استفاده می‌شود؟", "options": ["list", "set", "tuple", "dictionary"], "answer": 1},
    {"question": "چگونه می‌توان از دستور pass استفاده کرد؟", "options": ["برای اجرای یک دستور", "برای رها کردن یک بلوک کد", "برای بازگشت از یک تابع", "برای توقف یک حلقه"], "answer": 1}
]

used_questions = set()

async def start_exam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        await update.callback_query.answer("شما باید ابتدا ثبت نام کنید.")
        return

    available_questions = [q for q in questions if q not in used_questions]
    if len(available_questions) < 10:
        await update.message.reply_text("سوالات کافی برای آزمون موجود نیست.")
        return

    selected_questions = random.sample(available_questions, 10)
    used_questions.update(selected_questions)

    user_data[user_id] = {
        "questions": selected_questions,
        "current_question": 0,
        "score": 0
    }
    await ask_question(update, context)
# ذخیره وضعیت کاربران
user_data = {}

# تابع مدیریت شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        await update.message.reply_text("لطفاً نام و نام خانوادگی خود را وارد کنید تا ثبت ‌نام انجام شود.")
        return

    first_name = user[1]
    await update.message.reply_text(
        f"سلام {first_name} عزیز! خوش آمدید. اگر آماده‌اید، روی دکمه زیر کلیک کنید تا آزمون را شروع کنید.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("شروع آزمون", callback_data="start_exam")]])
    )

# تابع مدیریت ثبت نام کاربر
async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    full_name = update.message.text.split()
    if len(full_name) < 2:
        await update.message.reply_text("لطفاً نام و نام خانوادگی کامل خود را وارد کنید.")
        return

    first_name, last_name = full_name[0], " ".join(full_name[1:])

    # ذخیره اطلاعات کاربر در پایگاه داده
    cursor.execute("INSERT INTO users (user_id, first_name, last_name, registered) VALUES (?, ?, ?, 1)",
                   (user_id, first_name, last_name))
    conn.commit()

    await update.message.reply_text(
        f"{first_name} عزیز! ثبت نام شما با موفقیت انجام شد، حالا می‌توانید آزمون را شروع کنید.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("شروع آزمون", callback_data="start_exam")]])
    )

# تابع راهنما
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "این ربات یک آزمون پایتون برای شما طراحی کرده است.\n"
        "برای شروع آزمون، کافیست نام و نام خانوادگی خود را وارد کنید.\n"
        "سپس، با کلیک بر روی دکمه شروع آزمون می‌توانید شروع کنید.\n"
        "در هر آزمون 10 سوال به صورت رندوم از پایگاه داده سوالات ارائه می‌شود."
    )
    await update.message.reply_text(help_text)

# تابع مدیریت پنل کاربری
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        user_info = f"نام: {user[1]}\nنام خانوادگی: {user[2]}"
        await update.message.reply_text(f"اطلاعات کاربری شما:\n\n{user_info}")
    else:
        await update.message.reply_text("شما هنوز ثبت نام نکرده‌اید. لطفاً ابتدا نام و نام خانوادگی خود را وارد کنید.")

# تابع شروع آزمون
async def start_exam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        await update.callback_query.answer("شما باید ابتدا ثبت نام کنید.")
        return

    user_data[user_id] = {
        "questions": random.sample(questions, 10),
        "current_question": 0,
        "score": 0
    }
    await ask_question(update, context)

# پرسیدن سوال
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    current_question = user_data[user_id]["current_question"]
    questions_list = user_data[user_id]["questions"]

    if current_question < len(questions_list):
        q = questions_list[current_question]
        question_number = current_question + 1
        question_text = f"سوال {question_number} از 10: {q['question']}"

        keyboard = [
            [InlineKeyboardButton(opt, callback_data=f"{current_question}-{i}")] for i, opt in enumerate(q["options"])
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.callback_query:
            query = update.callback_query
            await query.edit_message_text(question_text, reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text(question_text, reply_markup=reply_markup)
    else:
        await show_results(update, context)

# مدیریت پاسخ‌ها
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data.split('-')
    current_question = int(data[0])
    selected_option = int(data[1])
    questions_list = user_data[user_id]["questions"]
    correct_answer = questions_list[current_question]["answer"]

    # ذخیره پاسخ کاربر
    questions_list[current_question]["user_answer"] = selected_option

    if selected_option == correct_answer:
        user_data[user_id]["score"] += 1

    user_data[user_id]["current_question"] += 1
    if user_data[user_id]["current_question"] < len(questions_list):
        await ask_question(update, context)
    else:
        await show_results(update, context)

# نمایش نتیجه نهایی
async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    score = user_data[user_id]["score"]
    questions_list = user_data[user_id]["questions"]

    result_message = f"آزمون تمام شد! نمره شما: {score}/10\n\n"
    result_message += "برای شروع دوباره آزمون گزینه مورد نظر را انتخاب کنید."

    # افزودن دکمه جدید برای نمایش نتیجه کامل آزمون
    keyboard = [
        [InlineKeyboardButton("شروع مجدد آزمون", callback_data="restart_exam")],
        [InlineKeyboardButton("مشاهده نتیجه آزمون", callback_data="view_results")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        query = update.callback_query
        await query.edit_message_text(result_message, reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text(result_message, reply_markup=reply_markup)

async def view_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    questions_list = user_data[user_id]["questions"]
    score = user_data[user_id]["score"]

    results_message = f"نتایج آزمون شما:\n\nنمره شما: {score}/10\n\n"

    for i, question in enumerate(questions_list):
        question_text = f"سوال {i + 1}: {question['question']}\n"
        options = question["options"]
        user_answer = question.get("user_answer", None)  # پاسخ انتخابی کاربر
        correct_answer = question["answer"]  # پاسخ درست

        options_message = "\n".join([f"{idx + 1}. {option}" for idx, option in enumerate(options)])

        if user_answer is not None:
            user_answer_text = f"پاسخ شما: {options[user_answer]} (انتخاب شده)"
            if user_answer == correct_answer:
                user_answer_text += " - پاسخ صحیح"
            else:
                user_answer_text += f" - پاسخ اشتباه (پاسخ صحیح: {options[correct_answer]})"

            results_message += f"{question_text}\n{options_message}\n{user_answer_text}\n\n"
        else:
            results_message += f"{question_text}\n{options_message}\nپاسخ داده نشده\n\n"

        if update.message:
             await update.message.reply_text(results_message)
        else:
            print("پیام وجود ندارد.")

    await update.message.reply_text(results_message)


# افزودن مدیریت درخواست "نتیجه آزمون"
async def handle_final_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "restart_exam":
        await start_exam(update, context)
    elif query.data == "view_results":
        await view_results(update, context)

# مدیریت دکمه‌های نتیجه نهایی
async def handle_final_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "restart_exam":
        await start_exam(update, context)

# اجرای برنامه
def main():
    token = "7886776227:AAHWfeU-vr3pvabAHjR3WdkFyvX_jlkXBd4"
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, register_user))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^[0-9]-[0-9]$"))
    app.add_handler(CallbackQueryHandler(start_exam, pattern="^start_exam$"))
    app.add_handler(CallbackQueryHandler(handle_final_choice, pattern="^(restart_exam)$"))
    app.add_handler(CallbackQueryHandler(view_results, pattern="^view_results$"))

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()