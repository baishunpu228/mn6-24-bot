import os
import asyncio
from datetime import datetime, timedelta
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Update

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip('/')

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

FULL_SCHEDULE = {
    "2026-09-14": [
        "1. 09:00 - 10:20 | 🟢 Семінар | Основи економічного прогнозування | проф. Телевата М.Т. | Ауд. 002[span_0](start_span)[span_0](end_span)",
        "2. 10:30 - 11:50 | 🔵 Лекція | Патентний маркетинг | доц. Грущенко О.А. | Ауд. 201[span_1](start_span)[span_1](end_span)"
    ],
    "2026-09-15": [
        "1. 09:00 - 10:20 | 🟡 Практична | Іноземна мова | доц. Буну І. | Ауд. 604[span_2](start_span)[span_2](end_span)",
        "2. 10:30 - 11:50 | 🔵 Лекція | Бухгалтерський облік та аудит | проф. Васюренко О.В. | Ауд. 203[span_3](start_span)[span_3](end_span)",
        "3. 12:40 - 14:00 | 🔵 Лекція | Бухгалтерський облік та аудит | проф. Васюренко О.В. | Ауд. 203[span_4](start_span)[span_4](end_span)",
        "4. 14:10 - 15:30 | 🔵 Лекція | Патентний маркетинг | доц. Грущенко О.А. | Ауд. 602[span_5](start_span)[span_5](end_span)"
    ],
    "2026-09-16": [
        "3. 12:40 - 14:00 | 🔵 Лекція | Системи управління документообігом | доц. Дяченко В.С. / Н.П. | Ауд. 005[span_6](start_span)[span_6](end_span)",
        "4. 14:10 - 15:30 | 🔵 Лекція | Системи управління документообігом | доц. Дяченко В.С. / Н.П. | Ауд. 005[span_7](start_span)[span_7](end_span)"
    ],
    "2026-09-17": [
        "4. 14:10 - 15:30 | 🟢 Семінар | Управління інтелектуальним капіталом | доц. Дяченко Н.П. | Ауд. 307[span_8](start_span)[span_8](end_span)",
        "5. 15:40 - 17:00 | 🔵 Лекція | Управління інтелектуальним капіталом | доц. Дяченко Н.П. | Ауд. 307[span_9](start_span)[span_9](end_span)",
        "6. 17:10 - 18:30 | 🟢 Семінар | Системи управління документообігом | доц. Дяченко В.С. / Н.П. | Ауд. 307[span_10](start_span)[span_10](end_span)"
    ],
    "2026-09-18": [
        "1. 09:00 - 10:20 | 🔵 Лекція | Основи економічного прогнозування | проф. Телевата М.Т. | Ауд. 102[span_11](start_span)[span_11](end_span)",
        "2. 10:30 - 11:50 | 🟡 Практична | Іноземна мова | доц. Буну І. | Ауд. 102[span_12](start_span)[span_12](end_span)"
    ]
}

def get_main_keyboard():
    kb = [
        [KeyboardButton(text="Сьогодні"), KeyboardButton(text="Завтра")],
        [KeyboardButton(text="Легенда кольорів")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_schedule_for_date(date_str):
    if date_str in FULL_SCHEDULE:
        lessons = FULL_SCHEDULE[date_str]
        res = f"📅 **Розклад на {date_str}**:\n\n"
        res += "\n\n".join(lessons)
        return res
    return f"📅 **Розклад на {date_str}**:\nПар немає або дата відсутня у розкладі! 🎉"

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! Бот розкладу готовий до роботи.\nОбери потрібну кнопку нижче:",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "Сьогодні")
async def show_today(message: types.Message):
    today_str = datetime.now().strftime("%Y-%m-%d")
    await message.answer(get_schedule_for_date(today_str))

@dp.message(F.text == "Завтра")
async def show_tomorrow(message: types.Message):
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    await message.answer(get_schedule_for_date(tomorrow_str))

@dp.message(F.text == "Легенда кольорів")
async def show_legend(message: types.Message):
    legend = (
        "📌 **Маркування типів занять:**\n\n"
        "🟢 **Зелений** — Семінар\n"
        "🔵 **Синій** — Лекція\n"
        "🟡 **Жовтий** — Практична / Залік"
    )
    await message.answer(legend)

async def handle_webhook(request):
    url_path = request.match_info.get("tail", "")
    if url_path == BOT_TOKEN:
        try:
            request_body = await request.json()
            update = Update.model_validate(request_body, context={"bot": bot})
            asyncio.create_task(dp.feed_update(bot, update))
        except Exception as e:
            pass
        return web.Response(text="OK", status=200)
    return web.Response(status=403)

async def health_check(request):
    return web.Response(text="OK", status=200)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

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
    

