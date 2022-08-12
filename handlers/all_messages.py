from aiogram.types import Message

from main import dp
from utils.help_functions import check_user_info
from utils.helpers import send_message


@dp.message_handler(chat_type='private')  # Answer to all messages
@dp.throttled(rate=2)  # Prevent flooding
async def all_messages(message: Message):
    chat_id = message.chat.id

    user_lang_code = message.from_user.language_code
    if user_lang_code in ['ru', 'uz']:
        user_lang = user_lang_code
    else:
        user_lang = await check_user_info(chat_id, user_lang_code)
        if not user_lang:
            return

    await send_message(chat_id, 'wrong', user_lang)
