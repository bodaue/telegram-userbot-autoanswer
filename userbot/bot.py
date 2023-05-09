from pyrogram import Client, idle

from config import config

app = Client(api_id=config.bot.api_id,
             api_hash=config.bot.api_hash,
             name='my_account',
             plugins=dict(root='handlers'))

if __name__ == '__main__':
    app.start()
    idle()
    app.stop()
