import os
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import CallbackQuery, Message, ForceReply
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.environ['TELEGRAM_TOKEN']
API_URL_APPROVE = "https://shop-auf1.onrender.com/withdraw/approve"
API_URL_DECLINE = "https://shop-auf1.onrender.com/withdraw/decline"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()


class DeclineReason(StatesGroup):
    waiting_reason = State()


pending_declines = {}


@router.callback_query(F.data.startswith("approve:"))
async def approve_handler(callback: CallbackQuery):
    withdraw_id = callback.data.split(":")[1]
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL_APPROVE, json={"withdraw_id": withdraw_id}) as resp:
            if resp.status == 200:
                await callback.answer("✅ Запит підтверджено")
                await callback.message.edit_reply_markup()
            else:
                await callback.answer("❌ Помилка при підтвердженні", show_alert=True)


@router.callback_query(F.data.startswith("decline:"))
async def decline_start(callback: CallbackQuery, state: FSMContext):
    withdraw_id = callback.data.split(":")[1]
    pending_declines[callback.from_user.id] = withdraw_id
    await callback.message.edit_reply_markup()
    await callback.message.answer("Введіть причину відхилення:", reply_markup=ForceReply())
    await state.set_state(DeclineReason.waiting_reason)


@router.message(DeclineReason.waiting_reason)
async def decline_reason_handler(message: Message, state: FSMContext):
    admin_id = message.from_user.id
    reason = message.text
    withdraw_id = pending_declines.pop(admin_id, None)
    if not withdraw_id:
        await message.answer("⚠️ Немає активного запиту для відхилення.")
        await state.clear()
        return

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL_DECLINE, json={"withdraw_id": withdraw_id, "reason": reason}) as resp:
            if resp.status == 200:
                await message.answer("Причина відхилення надіслана")
            else:
                await message.answer("❌ Помилка при відхиленні")

    await state.clear()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
