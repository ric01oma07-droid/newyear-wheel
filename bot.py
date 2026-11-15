import os
import json
import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart
import uvicorn

TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")

DATA_DIR = "/data" if os.path.exists("/data") else "."
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "currentTheme": "newyear",
    "validPromos": ["NEWYEAR2027", "SNOW2027", "XMAS", "GIFT", "SANTA"],
    "prizes": [
        { "label": "Скидка 15%", "icon": "🎄", "chance": 30, "wins": 0 },
        { "label": "Чашка какао", "icon": "☕", "chance": 25, "wins": 0 },
        { "label": "Подарок-сюрприз", "icon": "🎁", "chance": 15, "wins": 0 },
        { "label": "Кэшбэк 500₽", "icon": "✨", "chance": 10, "wins": 0 },
        { "label": "Скидка 25%", "icon": "⭐", "chance": 10, "wins": 0 },
        { "label": "+300 бонусов", "icon": "❄️", "chance": 6, "wins": 0 },
        { "label": "Билет на елку", "icon": "🎟️", "chance": 3, "wins": 0 },
        { "label": "СУПЕРПРИЗ", "icon": "🎅", "chance": 1, "wins": 0 }
    ]
}

_settings_cache = None

def load_settings():
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache
        
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                _settings_cache = json.load(f)
                return _settings_cache
        except Exception:
            pass
    _settings_cache = DEFAULT_SETTINGS
    return _settings_cache

def save_settings(data):
    global _settings_cache
    _settings_cache = data
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SettingsModel(BaseModel):
    currentTheme: str = "newyear"
    validPromos: List[str]
    prizes: List[Dict[str, Any]]

@app.get("/api/settings")
def api_get_settings():
    return load_settings()

@app.post("/api/settings")
def api_save_settings(settings: SettingsModel):
    data = {
        "currentTheme": settings.currentTheme,
        "validPromos": settings.validPromos,
        "prizes": settings.prizes
    }
    save_settings(data)
    return {"status": "success"}

@dp.message(CommandStart())
async def cmd_start(message: Message):
    web_app_url = "https://ric01oma07-droid.github.io/newyear-wheel/"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎄 Новогоднее Колесо Удачи", web_app=WebAppInfo(url=web_app_url))]
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
            settings = load_settings()
            for p in settings["prizes"]:
                if p["label"] == prize:
                    p["wins"] = p.get("wins", 0) + 1
                    break
            save_settings(settings)

            promo_text = f" (Промокод: {promo})" if promo else " (Без промокода)"
            user = message.from_user
            user_mention = f"@{user.username}" if user.username else f"{user.first_name} (ID: {user.id})"

            # Отправляем сообщение пользователю в чат с призом
            await message.answer(
                f"🎉 <b>Поздравляем с выигрышем!</b>\n\n"
                f"🎁 Ваш приз: <b>{prize}</b>\n"
                f"🎟️ {promo_text}\n\n"
                f"Покажите это сообщение нашему сотруднику, чтобы забрать подарок!",
                parse_mode="HTML"
            )

            # Безопасное уведомление администратору
            admin_id = 7008640180
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"🚨 <b>Новый выигрыш в колесе!</b>\n\n"
                        f"👤 Игрок: {user_mention}\n"
                        f"🎁 Выиграл приз: <b>{prize}</b>\n"
                        f"🎟️ {promo_text}"
                    ),
                    parse_mode="HTML"
                )
            except Exception as admin_err:
                print(f"Не удалось отправить уведомление админу: {admin_err}")

    except Exception as e:
        print(f"Ошибка в web_app_data: {e}")
        await message.answer("Произошла ошибка при регистрации приза. Попробуйте еще раз.")

async def main():
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("PORT", 8080))
    
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    print("Запуск сервера и Telegram-бота...")
    await asyncio.gather(
        server.serve(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
