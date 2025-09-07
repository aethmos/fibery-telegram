import os

from telegram.client import Telegram
# from telegram.text import Spoiler

def get_messages():

    tg = Telegram(
        api_id=int(os.environ.get('TELEGRAM_API_ID')),
        api_hash=os.environ.get('TELEGRAM_API_HASH'),
        bot_token=os.environ.get('TELEGRAM_BOT_TOKEN'),  # you can pass 'bot_token' instead
        database_encryption_key=os.environ.get('TELEGRAM_DB_CRYPT_KEY'),
        files_directory='/tmp/.tdlib_files/',
    )
    tg.login()

    # If this is the first run, the library needs to preload all chats.
    # Otherwise, the message will not be sent.
    result = tg.get_chats()
    result.wait()
    return result

    # chat_id: int
    # result = tg.send_message(chat_id, Spoiler('Hello world!'))
    #
    # # `tdlib` is asynchronous, so `python-telegram` always returns an `AsyncResult` object.
    # # You can receive a result with the `wait` method of this object.
    # result.wait()
    # print(result.update)
    #
    # tg.stop()  # You must call `stop` at the end of the script.
    # return {}