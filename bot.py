import os
import json
import logging
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart
import uvicorn

# Настройки
TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")

# Сохранение в постоянное хранилище Amvera /data
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

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_SETTINGS

def save_settings(data):
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
            promo_text = f" (Промокод: {promo})" if promo else " (Тестовый запуск)"
            user = message.from_user
            user_mention = f"@{user.username}" if user.username else f"{user.first_name} (ID: {user.id})"

            await message.answer(
                f"🎉 Поздравляем! Ваш приз: <b>{prize}</b> успешно зафиксирован!{promo_text}\n\n"
                f"Покажите это сообщение нашему сотруднику, чтобы забрать свой подарок.",
                parse_mode="HTML"
            )

            admin_id = 7008640180
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
    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке данных: {e}")

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
