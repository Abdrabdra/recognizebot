from aiogram.types import Message

from main import dp
from utils.advertisement.follow import check_following
from utils.help_functions import check_user_info
from utils.helpers import send_message
from utils.shazam.recognizer_main import recognizer_main


@dp.message_handler(chat_type='private', content_types=['voice'])  # Answer to all messages
@dp.throttled(rate=2)  # Prevent flooding
async def voice_messages(message: Message):
    chat_id = message.chat.id
    user_lang_code = message.from_user.language_code

    user_lang = await check_user_info(chat_id, user_lang_code)
    if not user_lang:
        return

    is_following = await check_following(chat_id, user_lang)
    if not is_following:
        return

    sent_message = await send_message(chat_id, 'wait', user_lang)

    audio_file_name = f'music/{chat_id}.ogg'
    await message.voice.download(audio_file_name)

    await recognizer_main(chat_id, user_lang, audio_file_name)

    await sent_message.delete()
