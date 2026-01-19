from aiogram import Bot, Dispatcher
import asyncio
from app.handlers import router
import os
from dotenv import load_dotenv

async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('bot_token')) # Создание бота
    dp = Dispatcher() # Обработчик событий
    dp.include_router(router) # Подключаем обработчик события из другого файла
    await dp.start_polling(bot) # Активация бота

if __name__ == '__main__':
    asyncio.run(main())
