import asyncio
import json  # <-- Добавлен импорт json
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# 1. Ваш токен от @BotFather
TOKEN = "9270543689:AAHgRIhk0rwYJD7WSgswR3Hx66z28qiXQXA"

# 2. Ваша ссылка на сайт с GitHub Pages (обязательно со слэшем на конце)
WEB_APP_URL = "https://ric01oma07-droid.github.io/newyear-wheel/"

# 3. Ваш цифровой Telegram ID
ADMIN_IDS = [7008640180]

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    is_admin = user_id in ADMIN_IDS

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎄 Крутить Новогоднее Колесо!",
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    
    greeting = f"Привет, {message.from_user.first_name}! 🎅\n\nДобро пожаловать в новогодний розыгрыш призов!"
    
    if is_admin:
        greeting += "\n\n⚙️ *Статус:* Активен режим администратора (доступны настройки)."

    await message.answer(greeting, reply_markup=keyboard, parse_mode="Markdown")

# ====== ВСТАВЛЯЕМ СЮДА (МЕЖДУ cmd_start И main) ======
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        # Распаковываем JSON, который прилетел из мини-приложения
        data = json.loads(message.web_app_data.data)
        
        prize = data.get("prize", "Подарок")
        promo = data.get("promo") or "Тестовый запуск (без промокода)"
        
        # Красивый ответ пользователю в чат
        await message.answer(
            f"🎉 **Поздравляем с выигрышем!** 🎉\n\n"
            f"🎁 **Приз:** {prize}\n"
            f"🎟 **Промокод:** `{promo}`\n\n"
            f"Покажите это сообщение нашему администратору или кассиру, чтобы забрать ваш подарок!",
            parse_mode="Markdown"
        )
    except Exception:
        # На случай, если прилетит нестандартный текст
        await message.answer(f"🎁 Получен приз из приложения:\n`{message.web_app_data.data}`", parse_mode="Markdown")
# ====================================================

async def main():
    bot = Bot(token=TOKEN)
    print("Бот успешно запущен и ожидает сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())