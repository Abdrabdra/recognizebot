from data.constants import AD_CHANNEL_LINK
from data.messages.admin import ALL_LANGUAGES, ALL_VIEWS_TYPES
from keyboards.buttons import admin_markup
from utils.advertisement.views import get_active_views
from main import bot


async def views_active_func(chat_id):
    active_views = await get_active_views()

    i = 0
    for one_view_type in active_views:
        view_type_advertisement = active_views[one_view_type]

        for one_lang in view_type_advertisement:
            i += 1
            one_lang_advertisement = view_type_advertisement[one_lang]
            message_id = one_lang_advertisement['message_id']
            downloads = one_lang_advertisement['downloads']
            lang_views = ALL_LANGUAGES[one_lang]

            args = downloads, ALL_VIEWS_TYPES[one_view_type], lang_views, AD_CHANNEL_LINK, message_id
            text_to_send = 'Всего показов: *{0:,}*\n' \
                           'Тип показов: *{1}*\n' \
                           'Язык: *{2}*\n' \
                           'Ссылка на рекламу: {3}/{4}'.format(*args)
            await bot.send_message(chat_id, text_to_send, parse_mode='markdown', disable_web_page_preview=True)

    if i == 0:
        await bot.send_message(chat_id, 'Нет сохраненной рекламы.', reply_markup=admin_markup)
