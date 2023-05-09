from pyrogram import filters, Client
from pyrogram.types import Message

from userbot.db.db_api import users


async def is_first_message_func(_, client: Client, message: Message):
    count_messages = await client.get_chat_history_count(message.from_user.id)
    return count_messages == 1


async def is_user_func(_, __, message: Message):
    user_id = message.from_user.id
    user = await users.find_one(filter={'_id': user_id})
    print(user)
    return user


is_first_message = filters.create(is_first_message_func)
is_user = filters.create(is_user_func)
