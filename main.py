from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import setup_handlers

# Bot va Dispatcher yaratish
BOT_TOKEN = "7535590465:AAEeFKakIc3jR5z9HW9G5HAAGCtkHmPzVNY"  # Sizning tokeningiz
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Handlerlarni sozlash
setup_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)