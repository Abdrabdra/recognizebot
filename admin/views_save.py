from datetime import date, timedelta
import json

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from keyboards.buttons import reject_markup, admin_markup, dates_markup, views_markup, lang_markup
from main import bot, AdminSaveAdd, dp, stats_db
from utils.advertisement.views import update_views
from data.messages.admin import REJECT_MSG, TODAY_MSG, TOMORROW_MSG, VIEWS_PREMIUM_MSG, VIEWS_UNIQUE_MSG,\
    VIEWS_SIMPLE_MSG, LIST_LANG, ALL_LANGUAGES, ALL_VIEWS_TYPES


async def views_save_func(chat_id):
    await bot.send_message(chat_id, 'На какой язык сохранить рекламу?', reply_markup=lang_markup)
    await AdminSaveAdd.ask_lang.set()


# Check admin sent message or file
@dp.message_handler(state=AdminSaveAdd.all_states, text=REJECT_MSG)
async def admin_reject_handler(message: Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Вы отменили действия', reply_markup=admin_markup)
    await state.finish()


@dp.message_handler(state=AdminSaveAdd.ask_lang, text=LIST_LANG)
async def admin_ask_lang(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    await state.update_data(views_lang=admin_message)
    await bot.send_message(chat_id, 'На когда сохранить рекламу?', reply_markup=dates_markup)
    await AdminSaveAdd.ask_date.set()


@dp.message_handler(state=AdminSaveAdd.ask_date, text=[TODAY_MSG, TOMORROW_MSG])
async def admin_ask_date(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    await state.update_data(date_to_save=admin_message)
    await bot.send_message(chat_id, 'Выберите вид показов по кнопкам ниже', reply_markup=views_markup)
    await AdminSaveAdd.ask_type.set()


@dp.message_handler(state=AdminSaveAdd.ask_type, text=[VIEWS_PREMIUM_MSG, VIEWS_UNIQUE_MSG, VIEWS_SIMPLE_MSG])
async def admin_ask_type(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    await state.update_data(ad_type=admin_message)
    await bot.send_message(chat_id, 'Перешлите пост для рекламы', reply_markup=reject_markup)
    await AdminSaveAdd.ask_post.set()


@dp.message_handler(state=AdminSaveAdd.ask_post)
async def admin_ask_post(message: Message, state: FSMContext):
    chat_id = message.chat.id
    message_id = message.forward_from_message_id

    data = await state.get_data()
    date_to_save = data['date_to_save']

    views_lang = str(data['views_lang'])
    views_lang_code = ALL_LANGUAGES[views_lang]

    admin_ad_type = data['ad_type']
    ad_type = ALL_VIEWS_TYPES[admin_ad_type]

    today_date = date.today()
    if date_to_save == TODAY_MSG:
        save_date = str(today_date)
    else:
        save_date = str(today_date + timedelta(days=1))

    views_advertisement_db = stats_db.get(f'{save_date}_VIEWS')
    if views_advertisement_db is None:
        views_advertisement = {'unique': {}, 'simple': {}, 'premium': {}}
    else:
        views_advertisement = json.loads(views_advertisement_db)

    post_info_dict = {'start_date': save_date, 'message_id': message_id, 'downloads': 0}
    views_advertisement[ad_type][views_lang_code] = post_info_dict

    stats_db.set(f'{save_date}_VIEWS', json.dumps(views_advertisement))

    text_to_send = f'Реклама сохранена на *{save_date}*\n' \
                   f'Тип рекламы: *{admin_ad_type}*\n' \
                   f'Язык: *{views_lang}*'
    await bot.send_message(chat_id, text_to_send, parse_mode='markdown', reply_markup=admin_markup)

    if date_to_save == TODAY_MSG:
        await update_views(save_date)

    await state.finish()
