import asyncio
import os
from pathlib import Path

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    WebAppInfo,
)

BASE = Path(__file__).parent
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# Bo'sh qoldirsangiz, to'lov o'tkazib yuboriladi (faqat sinash uchun)
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")
# Render manzilni o'zi beradi (RENDER_EXTERNAL_URL). Boshqa joyda WEBAPP_URL ni yozing.
WEBAPP_URL = os.getenv("WEBAPP_URL") or os.getenv("RENDER_EXTERNAL_URL", "")
PORT = int(os.getenv("PORT", "8080"))
PRICE_SUM = 15000  # so'mda

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Testni boshlash", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Salom! Bu 20 ta savoldan iborat IQ-uslubidagi test.\n"
        "Natija taxminiy IQ ball bilan chiqadi, rasmiy test emas."
    )
    if not PAYMENT_TOKEN:
        await message.answer("Testni boshlashingiz mumkin:", reply_markup=start_kb())
        return
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="IQ test",
        description="20 savol, 25 daqiqa, natija va tushuntirishlar bilan",
        payload=f"iq_test_{message.from_user.id}",
        provider_token=PAYMENT_TOKEN,
        currency="UZS",
        prices=[LabeledPrice(label="IQ test", amount=PRICE_SUM * 100)],  # tiyinda
    )


@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def paid(message: Message):
    await message.answer("To'lov qabul qilindi. Testni boshlashingiz mumkin:", reply_markup=start_kb())


async def index(request):
    return web.FileResponse(BASE / "index.html")


async def health(request):
    return web.Response(text="ok")


async def main():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
