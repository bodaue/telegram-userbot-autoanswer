from pyrogram import filters
from pyrogram.types import Message


def is_first_message_func(_, __, message: Message):
    return message.id == 1


is_first_message = filters.create(is_first_message_func)
