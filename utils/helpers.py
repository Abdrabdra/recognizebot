import asyncio
from functools import wraps, partial

from main import bot
from data.messages.bot import msg_dict
from data.constants import BOT_USERNAME


# Function to send waiting message
async def send_message(chat_id, msg_str, lang, args=None, markup=None, parse=None):
    try:
        msg_to_send = await user_msg(msg_str, args, lang)
        sent_message = await bot.send_message(chat_id, msg_to_send, reply_markup=markup, parse_mode=parse,
                                              disable_web_page_preview=True, disable_notification=True)
        return sent_message
    except Exception as err:
        print('[ERROR] in send_message\nException: {}\n\n'.format(err))


async def send_document(chat_id, file_to_send, caption):
    await bot.send_document(chat_id, open(file_to_send, 'rb'), caption=caption)


async def send_music(chat_id, file_to_send, duration=None, title=None, performer=None):
    try:
        sent_music = await bot.send_audio(chat_id, file_to_send, caption=BOT_USERNAME, title=title,
                                          performer=performer, duration=duration)
        return sent_music.audio.file_id

    except Exception as err:
        print(err, 'important_functions.send_music music file is more 20 or 50 mb')
        return False


async def get_chat_member(channel_id, chat_id):
    try:
        user_following_info = await bot.get_chat_member(channel_id, chat_id)
        return user_following_info
    except Exception as err:
        print('[ERROR] in get_chat_member\nException: {}\n\n'.format(err))


async def copy_message(chat_id, from_chat_id, message_id):
    try:
        copied_message = await bot.copy_message(chat_id, from_chat_id, message_id)
        return copied_message.message_id
    except Exception as err:
        print('[ERROR] in copy_message\nException: {}\n\n'.format(err))


# Get user language
async def user_msg(message_str, args, lang):
    if args is None:
        user_message = msg_dict[lang][message_str]
    else:
        if type(args) != tuple:
            user_message = msg_dict[lang][message_str].format(args)
        else:
            user_message = msg_dict[lang][message_str].format(*args)

    if message_str == 'downloaded':
        user_message = user_message.replace('_', '\_')

    return user_message


def wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run
