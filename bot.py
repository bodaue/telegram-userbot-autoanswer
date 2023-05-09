from pyrogram import Client, idle

from userbot.config import config

app = Client(api_id=config.bot.api_id,
             api_hash=config.bot.api_hash,
             name='my_account',
             plugins=dict(root='userbot'))

if __name__ == '__main__':
    app.start()
    idle()
    app.stop()
