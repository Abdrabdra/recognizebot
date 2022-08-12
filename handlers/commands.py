from aiogram.types import Message

from keyboards.inline import language
from utils.help_functions import check_user_info
from utils.helpers import send_message
from main import dp


@dp.message_handler(lambda message: message.get_args(), commands=['start'], chat_type='private')
async def start_ref_command(message: Message):
    chat_id = message.chat.id
    referral = message.get_args()

    user_lang_code = message.from_user.language_code
    user_lang = await check_user_info(chat_id, user_lang_code, referral)

    if user_lang:
        await send_message(chat_id, 'start', user_lang, parse='markdown')
        await send_message(chat_id, 'our_bots', user_lang, parse='markdown')


# Answer to all bot commands
@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    chat_id = message.chat.id

    if message.chat.type == 'private':
        user_lang_code = message.from_user.language_code
        user_lang = await check_user_info(chat_id, user_lang_code)
    else:
        user_lang = 'ru'

    if user_lang:
        await send_message(chat_id, 'start', user_lang, parse='markdown')
        await send_message(chat_id, 'our_bots', user_lang, parse='markdown')


@dp.message_handler(commands=['lang'], chat_type='private')
async def lang_command(message: Message):
    await send_message(message.chat.id, 'lang', 'ru', markup=language)
