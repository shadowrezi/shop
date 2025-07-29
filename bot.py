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
        async with session.post(API_URL_APPROVE, json={"withdraw_id": withdraw_id, 'reason': None}) as resp:
            if 1 or resp.status == 200:
                await callback.answer("✅ Request approved")
                await callback.message.edit_text(
                    text=callback.message.text + '\n\n' + '✅ Request approved'
                )
            else:
                print(await resp.text())
                await callback.answer("❌ Erorr request", show_alert=True)
    await callback.message.edit_reply_markup()


@router.callback_query(F.data.startswith("decline:"))
async def decline_start(callback: CallbackQuery, state: FSMContext):
    withdraw_id = callback.data.split(":")[1]

    await state.set_data({
        "withdraw_id": withdraw_id,
        "chat_id": callback.message.chat.id,
        "message_id": callback.message.message_id,
        'message_text': callback.message.text
    })

    await callback.message.edit_reply_markup()
    await callback.message.answer("Please enter the reason for rejection:", reply_markup=ForceReply())
    await state.set_state(DeclineReason.waiting_reason)


@router.message(DeclineReason.waiting_reason)
async def decline_reason_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    withdraw_id = data.get("withdraw_id")
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")
    message_text = data.get('message_text')

    reason = message.text

    if not withdraw_id or not chat_id or not message_id:
        await message.answer("⚠️ No active withdrawal request to decline.")
        await state.clear()
        return

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL_DECLINE, json={"withdraw_id": withdraw_id, "reason": reason}) as resp:
            if 1 or resp.status == 200:
                await message.answer("❌ Withdrawal request declined. Reason has been saved.")

                try:
                    await message.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=message_text + "\n\n❌ Request declined",
                        reply_markup=None
                    )
                except Exception as e:
                    print("Failed to edit the original message:", e)
            else:
                print(await resp.text())
                await message.answer("❌ Error occurred while saving the reason.")

    await state.clear()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
