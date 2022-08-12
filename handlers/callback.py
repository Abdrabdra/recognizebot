from aiogram.types import CallbackQuery

from utils.advertisement.follow import check_following
from utils.helpers import send_message
from main import dp, users_db
from data.constants import LIST_LANG_CODES


# Answer to called button
@dp.callback_query_handler(text=LIST_LANG_CODES, chat_type='private')
async def lang_callback(call: CallbackQuery):
    chat_id = call.message.chat.id
    call_data = call.data

    await call.answer()

    try:
        await call.message.delete()
    except Exception as err:
        print(err, 'lang_callback, delete language message')

    await send_message(chat_id, 'start', call_data, parse='markdown')
    await send_message(chat_id, 'our_bots', call_data, parse='markdown')
    users_db.set(chat_id, call_data)


# Answer to called button
@dp.callback_query_handler(chat_type='private')
async def check_callback(call: CallbackQuery):
    chat_id = call.message.chat.id
    split_data = call.data.split('!')
    if len(split_data) == 1:
        return
    user_lang = split_data[1]

    is_following = await check_following(chat_id, user_lang)
    if not is_following:
        await call.message.delete()
        return

    await send_message(chat_id, 'follow-success', user_lang)

