from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import logging
import os
from dotenv import load_dotenv

load_dotenv()  # .env fayldan o'qish

API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_modes = {}

def format_number(num):
    return '{:,.0f}'.format(num).replace(',', ' ')

@dp.message_handler(commands=['start'])
async def start(msg: Message):
    user_modes[msg.from_user.id] = None
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("📊 Binance & Telegram foydasi"),
        KeyboardButton("💹 Faqat Binance foydasi")
    )
    await msg.answer(
        "👋 P2P Foyda Hisoblash Botiga xush kelibsiz!\n\n"
        "Quyidagilardan birini tanlang:",
        reply_markup=keyboard
    )

@dp.message_handler(lambda msg: msg.text in ["📊 Binance & Telegram foydasi", "💹 Faqat Binance foydasi"])
async def select_mode(msg: Message):
    if msg.text == "📊 Binance & Telegram foydasi":
        user_modes[msg.from_user.id] = "full"
        await msg.answer(
            "✅ Tanlandi: Binance + Telegram foyda hisoblash\n\n"
            "Format: `13040, 13250, 12500000, 2000`",
            parse_mode="Markdown"
        )
    else:
        user_modes[msg.from_user.id] = "binance_only"
        await msg.answer(
            "✅ Tanlandi: Faqat Binance foyda hisoblash\n\n"
            "Format: `13040, 13250, 12500000, 2000`",
            parse_mode="Markdown"
        )

@dp.message_handler()
async def calculate(msg: Message):
    user_id = msg.from_user.id
    mode = user_modes.get(user_id)

    if not mode:
        await msg.answer("❗️ Avval hisoblash turini tanlang. /start buyrug'ini bosing.")
        return

    try:
        parts = msg.text.replace(" ", "").split(',')
        if len(parts) < 4:
            await msg.answer("❗️ Format noto‘g‘ri. 4 ta qiymat kiriting: buy, sell, amount, commission")
            return

        buy_price = float(parts[0])
        sell_price = float(parts[1])
        amount = float(parts[2])
        extra_commission = float(parts[3])

        usdt_amount = amount / buy_price

        if mode == "full":
            usdt_amount -= 0.03
            total_sell = usdt_amount * sell_price
            total_sell *= 0.991
        elif mode == "binance_only":
            total_sell = usdt_amount * sell_price
            total_sell *= 0.9999

        total_sell -= extra_commission
        profit = total_sell - amount

        label = "📊 Binance & Telegram foyda:" if mode == "full" else "💹 Faqat Binance foyda:"
        await msg.answer(f"{label}\n\n💸 Sof foyda: {format_number(profit)} so'm")

    except Exception:
        await msg.answer("❌ Xatolik yuz berdi. Iltimos, maʼlumotlarni to‘g‘ri kiriting.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
