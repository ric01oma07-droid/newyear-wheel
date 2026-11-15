import os
import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart

# Токен вашего бота (можно указать прямо здесь или настроить через переменные окружения в Amvera)
TOKEN = os.getenv("9270543689:AAHgRIhk0rwYJD7WSgswR3Hx66z28qiXQXA")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    # ⚠️ ВНИМАНИЕ: Убедитесь, что здесь указана ваша точная и рабочая ссылка на GitHub Pages
    web_app_url = "https://github.com/ric01oma07-droid/newyear-wheel.git"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎄 Новогоднее Колесо Удачи",
                    web_app=WebAppInfo(url=web_app_url)
                )
            ]
        ]
    )
    
    await message.answer(
        "Привет! Добро пожаловать в новогоднее мини-приложение.\n"
        "Нажми на кнопку ниже, чтобы открыть Колесо Удачи и выиграть подарки! 🎁",
        reply_markup=keyboard
    )

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get("action")
        prize = data.get("prize")
        promo = data.get("promo")

        if action == "prize_claimed":
            promo_text = f" (Промокод: {promo})" if promo else " (Тестовый запуск)"
            await message.answer(
                f"🎉 <b>Пользователь забрал приз!</b>\n\n"
                f"🎁 Приз: <b>{prize}</b>\n"
                f"🎟️ {promo_text}\n"
                f"👤 Игрок: @{message.from_user.username or message.from_user.id}",
                parse_mode="HTML"
            )
    except Exception as e:
        await message.answer(f"Ошибка при обработке данных из мини-приложения: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен и ожидает сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
