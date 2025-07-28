import os
import aiohttp
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from dotenv import load_dotenv

load_dotenv('.env')

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_URL = os.getenv('API_URL')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start_command(message: Message):
    await message.answer(
        'Hi, send me your token from <a href="shop-auf1.onrender.com">ShadowShop</a>'
    )


@dp.message()
async def handle_token(message: Message):
    token = message.text.strip().upper()
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json={
                'token': token,
                'chat_id': message.chat.id
            }) as response:
                data = await response.json()
        except Exception as ex:
            await message.answer('Error on server, 400')
            print(ex)
    if data.get('status') == 'ok':
        await message.answer('Account is successfully connected!')
    else:
        await message.answer(f'Erorr: {data.get('message')}')


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
