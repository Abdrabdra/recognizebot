from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from main import bot, AdminFollowAdd, dp
from data.messages.admin import REJECT_MSG, ADD_MSG, REMOVE_MSG, LIST_LANG, ALL_LANGUAGES, ALL_LANG_MSG
from utils.advertisement.follow import update_following, get_active_following
from keyboards.buttons import following_markup, admin_markup, reject_markup, necessary_lang_markup


async def necessary_following_func(chat_id):
    active_necessary_lang = await get_active_following()
    await bot.send_message(chat_id, f'Добавить обязательную подписку или убрать?\n\n'
                                    f'На данный момент поставлены:\n{active_necessary_lang}',
                           reply_markup=following_markup, disable_web_page_preview=True)
    await AdminFollowAdd.ask_state.set()


# Handler to receive reject message
@dp.message_handler(state=AdminFollowAdd.all_states, text=REJECT_MSG)
async def admin_reject_handler(message: Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Вы отменили действия', reply_markup=admin_markup)
    await state.finish()


@dp.message_handler(state=AdminFollowAdd.ask_state, text=[ADD_MSG, REMOVE_MSG])
async def admin_ask_state_following(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    await state.update_data(admin_state=admin_message)

    if admin_message == ADD_MSG:
        await bot.send_message(chat_id, 'На какой язык поставить обязательную подписку?',
                               reply_markup=necessary_lang_markup)

    else:
        await bot.send_message(chat_id, 'С какого языка убрать обязательную подписку?',
                               reply_markup=necessary_lang_markup)

    await AdminFollowAdd.ask_lang.set()


@dp.message_handler(state=AdminFollowAdd.ask_lang, text=LIST_LANG + [ALL_LANG_MSG])
async def admin_ask_lang_following(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    data = await state.get_data()
    admin_state = data['admin_state']

    list_follow_lang = []
    if admin_message == ALL_LANG_MSG:
        for one_lang in LIST_LANG:
            list_follow_lang.append(ALL_LANGUAGES[one_lang])
    else:
        list_follow_lang.append(ALL_LANGUAGES[admin_message])

    if admin_state == ADD_MSG:
        await state.update_data(list_follow_lang=list_follow_lang)
        await bot.send_message(chat_id, 'Пришлите ссылку для обязательной подписки', reply_markup=reject_markup)
        await AdminFollowAdd.ask_link.set()
    else:
        for one_lang_code in list_follow_lang:
            removed_lang = ALL_LANGUAGES[one_lang_code]
            await update_following(one_lang_code, remove=True)
            await bot.send_message(message.chat.id, f'Вы убрали обязательную подписку с языка: {removed_lang}',
                                   reply_markup=admin_markup)
        await state.finish()


@dp.message_handler(state=AdminFollowAdd.ask_link)
async def admin_ask_link_following(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    await state.update_data(channel_link=admin_message)
    await bot.send_message(chat_id, 'Перешлите любой пост с этого канала', reply_markup=reject_markup)
    await AdminFollowAdd.ask_post.set()


@dp.message_handler(state=AdminFollowAdd.ask_post, content_types=['video', 'photo', 'text'])
async def admin_ask_post_following(message: Message, state: FSMContext):
    chat_id = message.chat.id
    channel_id = message.forward_from_chat.id

    await state.update_data(channel_id=channel_id)

    await bot.send_message(chat_id, 'Введите рандомное количество запросов на подписку, '
                                    'где 0 просьба подписаться при каждом скачивании', reply_markup=reject_markup)
    await AdminFollowAdd.ask_range.set()


@dp.message_handler(lambda message: message.text.isdigit(), state=AdminFollowAdd.ask_range)
async def admin_ask_range_following(message: Message, state: FSMContext):
    chat_id = message.chat.id
    follow_range = int(message.text)

    data = await state.get_data()
    channel_link = data['channel_link']
    channel_id = data['channel_id']
    list_follow_lang = data['list_follow_lang']

    for one_lang_code in list_follow_lang:
        added_lang = ALL_LANGUAGES[one_lang_code]
        await update_following(one_lang_code, channel_link, channel_id, follow_range)

        follow_range_text = 'Каждому {} пользователю'.format(follow_range + 1)
        admin_text = f'Вы добавили обязательную подписку на язык: {added_lang}.\n' \
                     f'Ссылка на канал: {channel_link}\n' \
                     f'Частота подписки: {follow_range_text}'

        await bot.send_message(chat_id, admin_text, reply_markup=admin_markup, disable_web_page_preview=True)
    await state.finish()

