import os
import asyncio 
from aiogram import Bot, Dispatcher, types 
from aiogram.filters import Command
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
@dp.message(Command("start"))
async def start_handler(message: types.Message):
     await message.answer("Привіт! Я бот з розкладом універу. Напиши /schedule щоб побачити розклад.")
@dp.message(Command("schedule"))
async def schedule_handler(message: types.Message): 
    schedule_text = ( "Розклад занять:\n\n" "Понеділок:\n1. Математика\n2. Програмування\n\n" "Вівторок:\n1. Фізика\n2. Англійська мова" )    
    await message.answer(schedule_text)
async def main(): 
    print("Бот запущений!") 
    await dp.start_polling(bot)
if __name__ == "__main__": 
    asyncio.run(main())
