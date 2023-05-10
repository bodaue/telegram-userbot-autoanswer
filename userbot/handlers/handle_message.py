import re
from asyncio import sleep
from datetime import datetime
from random import randint

import pytz as pytz
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import Message

from userbot.config import config
from userbot.db.db_api import users
from userbot.filters.filter import is_user, is_first_message


def format_greeting(date: datetime) -> str:
    hours = date.hour
    if hours in (4, 5, 6, 7, 8, 9, 10, 11):
        return 'Доброе утро'

    if hours in (12, 13, 14, 15, 16):
        return 'Добрый день'

    if hours in (17, 18, 19, 20, 21, 22, 23):
        return 'Добрый вечер'

    if hours in (0, 1, 2, 3):
        return 'Доброй ночи'


AVERAGE_TYPING_DURATION = 5


async def send_chat_action_typing(client: Client, user_id: int, duration: int = 10):
    for i in range(duration // AVERAGE_TYPING_DURATION):
        await client.send_chat_action(chat_id=user_id,
                                      action=ChatAction.TYPING)
        await sleep(AVERAGE_TYPING_DURATION)


@Client.on_message(filters.private & filters.incoming & is_first_message & ~is_user & ~filters.bot)
async def get_first_incoming_message(client: Client, message: Message):
    """ловит первое сообщение от пользователя, записывает текст в гугл-таблицу и отвечает с задержкой"""
    user_id = message.from_user.id

    username = message.from_user.username if message.from_user.username else '-'
    phone = message.from_user.phone_number if message.from_user.phone_number else '-'
    text = message.text if message.text else message.caption if message.caption else '-'

    tz = pytz.timezone('America/Los_Angeles')
    date_time = datetime.now(tz=tz)
    date = date_time.date().strftime('%d.%m.%Y')
    time = date_time.time().strftime('%H:%M')

    google_client_manager = config.misc.google_client_manager
    google_client = await google_client_manager.authorize()
    spreadsheet = await google_client.open_by_key(config.misc.google_sheet_key)
    worksheet = await spreadsheet.get_worksheet(0)
    update_info = await worksheet.append_row([date, time, username, phone, text])

    cell_range = update_info['updates']['updatedRange']  # Формат: 'Название_листа'!A1:E1
    comp = re.compile(r'(![A-Z])(\d+)')
    row = int(comp.search(cell_range).group(2))

    await users.insert_one(document={'_id': user_id,
                                     'date': date_time,
                                     'row': row})
    # задержка перед чтением сообщения
    seconds = randint((3 * 60), (5 * 60))
    await sleep(delay=seconds)
    await client.read_chat_history(chat_id=user_id)

    # задержка перед началом печати
    seconds = randint(4, 11)
    await sleep(delay=seconds)

    # рандомное время печати
    seconds = randint(10, 20)
    await send_chat_action_typing(client, user_id, duration=seconds)

    greeting = format_greeting(date_time)
    text = f'{greeting}, напишите свой номер я буду в офисе наберу.'
    await client.send_message(chat_id=user_id,
                              text=text)


@Client.on_message(
    filters.private & filters.incoming & is_user & (filters.text | filters.caption) & ~filters.bot)
async def get_incoming_message(_: Client, message: Message):
    """ловит НЕ первое сообщение, просто дописывает текст сообщения в ячейку с текстом"""
    user_id = message.from_user.id
    user = await users.find_one(filter={'_id': user_id})
    row = user['row']
    print(user, 2)

    google_client_manager = config.misc.google_client_manager
    google_client = await google_client_manager.authorize()
    spreadsheet = await google_client.open_by_key(config.misc.google_sheet_key)
    worksheet = await spreadsheet.get_worksheet(0)

    cell = await worksheet.cell(row=row,
                                col=5)
    previous_text = cell.value
    text = message.text if message.text else message.caption
    text = f'{previous_text}\n' \
           f'{text}'

    await worksheet.update_cell(row=row,
                                col=5,
                                value=text)
