import os
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Update

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SCHEDULE = {
    "monday": {
        "title": "Понділок",
        "lessons": [
            "1. 09:00 - 10:20 | Основи економічного прогнозування (с.) | Ауд. 002[span_1](start_span)[span_1](end_span)",
            "2. 10:30 - 11:50 | Патентний маркетинг (л.) | Ауд. 201[span_2](start_span)[span_2](end_span)"
        ]
    },
    "tuesday": {
        "title": "Вівторок",
        "lessons": [
            "1. 09:00 - 10:20 | Іноземна мова (за професійним спрямуванням) (пр.) | Ауд. 604[span_3](start_span)[span_3](end_span)",
            "2. 10:30 - 11:50 | Бухгалтерський облік та аудит (л./с.) | Ауд. 203[span_4](start_span)[span_4](end_span)",
            "3. 12:40 - 14:00 | Бухгалтерський облік та аудит (л./с.) | Ауд. 203[span_5](start_span)[span_5](end_span)",
            "4. 14:10 - 15:30 | Патентний маркетинг (л./залік) | Ауд. 602[span_6](start_span)[span_6](end_span)"
        ]
    },
    "wednesday": {
        "title": "Середа",
        "lessons": [
            "3. 12:40 - 14:00 | Системи управління документообігом (л./с.) | Ауд. 005[span_7](start_span)[span_7](end_span)",
            "4. 14:10 - 15:30 | Системи управління документообігом (л./с.) | Ауд. 005[span_8](start_span)[span_8](end_span)"
        ]
    },
    "thursday": {
        "title": "Четвер",
        "lessons": [
            "4. 14:10 - 15:30 | Управління інтелектуальним капіталом (с./залік) | Ауд. 307[span_9](start_span)[span_9](end_span)",
            "5. 15:40 - 17:00 | Управління інтелектуальним капіталом (л./с.) | Ауд. 307[span_10](start_span)[span_10](end_span)",
            "6. 17:10 - 18:30 | Системи управління документообігом (с.) | Ауд. 307[span_11](start_span)[span_11](end_span)"
        ]
    },
    "friday": {
        "title": "П'ятниця",
        "lessons": [
            "1. 09:00 - 10:20 | Основи економічного прогнозування (л./залік) | Ауд. 102[span_12](start_span)[span_12](end_span)",
            "2. 10:30 - 11:50 | Іноземна мова (за професійним спрямуванням) (пр./залік) | Ауд. 102[span_13](start_span)[span_13](end_span)"
        ]
    }
}

WEEKDAYS_MAP = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday"
}

def get_main_keyboard():
    kb = [
        [KeyboardButton(text="Сьогодні"), KeyboardButton(text="Завтра")],
        [KeyboardButton(text="Понеділок"), KeyboardButton(text="Вівторок"), KeyboardButton(text="Середа")],
        [KeyboardButton(text="Четвер"), KeyboardButton(text="П'ятниця")],
        [KeyboardButton(text="Весь розклад")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def format_day_schedule(day_key):
    day_info = SCHEDULE.get(day_key)
    if not day_info or not day_info["lessons"]:
        return f"📌 **{day_info['title']}**: Пар немає 🎉"
    
    res = f"📅 **{day_info['title']}**:\n\n"
    res += "\n\n".join(day_info["lessons"])
    return res

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! Я бот з розкладом занять.\nОбери потрібний варіант на клавіатурі нижче:",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "Сьогодні")
async def show_today(message: types.Message):
    weekday = datetime.now().weekday()
    if weekday in WEEKDAYS_MAP:
        text = format_day_schedule(WEEKDAYS_MAP[weekday])
    else:
        text = "Сьогодні вихідний! Пар немає 🥳"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "Завтра")
async def show_tomorrow(message: types.Message):
    weekday = (datetime.now().weekday() + 1) % 7
    if weekday in WEEKDAYS_MAP:
        text = format_day_schedule(WEEKDAYS_MAP[weekday])
    else:
        text = "Завтра вихідний! Пар немає 🥳"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "Понеділок")
async def show_mon(message: types.Message):
    await message.answer(format_day_schedule("monday"), parse_mode="Markdown")

@dp.message(F.text == "Вівторок")
async def show_tue(message: types.Message):
    await message.answer(format_day_schedule("tuesday"), parse_mode="Markdown")

@dp.message(F.text == "Середа")
async def show_wed(message: types.Message):
    await message.answer(format_day_schedule("wednesday"), parse_mode="Markdown")

@dp.message(F.text == "Четвер")
async def show_thu(message: types.Message):
    await message.answer(format_day_schedule("thursday"), parse_mode="Markdown")

@dp.message(F.text == "П'ятниця")
async def show_fri(message: types.Message):
    await message.answer(format_day_schedule("friday"), parse_mode="Markdown")

@dp.message(F.text == "Весь розклад")
async def show_all(message: types.Message):
    all_text = []
    for day_key in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        all_text.append(format_day_schedule(day_key))
    full_schedule = "\n\n-------------------\n\n".join(all_text)
    await message.answer(full_schedule, parse_mode="Markdown")

async def handle_webhook(request):
    url_path = request.match_info.get("tail", "")
    if url_path == BOT_TOKEN:
        request_body = await request.json()
        update = Update.model_validate(request_body, context={"bot": bot})
        await dp.feed_update(bot, update)
        return web.Response(text="OK")
    return web.Response(status=403)

async def health_check(request):
    return web.Response(text="OK", status=200)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

app = web.Application()
app.router.add_post(f"/webhook/{{tail:.+}}", handle_webhook)
app.router.add_get("/", health_check)

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
