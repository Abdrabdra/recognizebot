import json

from main import files_id, stats_db
from data.constants import AD_CHANNEL_ID, AD_CHANNEL_LINK, STATS_GROUP_ID
from utils.helpers import copy_message, send_message
from data.messages.admin import ALL_LANGUAGES, ALL_VIEWS_TYPES

views_advertisement = {'unique': {}, 'simple': {}, 'premium': {}}


async def check_views(chat_id, user_lang):
    global views_advertisement

    premium_advertisement = views_advertisement['premium']
    simple_advertisement = views_advertisement['simple']
    unique_advertisement = views_advertisement['unique']

    # Check premium advertisement
    if user_lang in premium_advertisement:
        premium_lang_advertisement = premium_advertisement[user_lang]

        message_id = premium_lang_advertisement['message_id']
        await copy_message(chat_id, AD_CHANNEL_ID, message_id)
        files_id.set(chat_id, '')

        views_advertisement['premium'][user_lang]['downloads'] += 1
        return True

    # Check unique advertisement
    if user_lang in unique_advertisement and not files_id.exists(chat_id):
        unique_lang_advertisement = unique_advertisement[user_lang]

        message_id = unique_lang_advertisement['message_id']
        await copy_message(chat_id, AD_CHANNEL_ID, message_id)
        files_id.set(chat_id, '')

        views_advertisement['unique'][user_lang]['downloads'] += 1
        return True

    # Check simple advertisement
    if user_lang in simple_advertisement and files_id.exists(chat_id):
        simple_lang_advertisement = simple_advertisement[user_lang]

        message_id = simple_lang_advertisement['message_id']
        await copy_message(chat_id, AD_CHANNEL_ID, message_id)

        views_advertisement['simple'][user_lang]['downloads'] += 1
        return True

    files_id.set(chat_id, '')
    return False


async def send_views_stat(yesterday_date):
    for one_view_type in views_advertisement:
        view_type_advertisement = views_advertisement[one_view_type]

        for one_lang in view_type_advertisement:
            one_lang_advertisement = view_type_advertisement[one_lang]
            message_id = one_lang_advertisement['message_id']
            downloads = one_lang_advertisement['downloads']
            lang_views = ALL_LANGUAGES[one_lang]

            args = downloads, ALL_VIEWS_TYPES[one_view_type], lang_views, AD_CHANNEL_LINK, message_id
            await send_message(STATS_GROUP_ID, 'advertisement', 'ru', args=args, parse='markdown')

    stats_db.delete(f'{yesterday_date}_VIEWS')


async def update_views(ad_date):
    global views_advertisement

    views_advertisement_db = stats_db.get(f'{ad_date}_VIEWS')
    if views_advertisement_db is not None:
        views_advertisement = json.loads(views_advertisement_db)


async def get_active_views():
    return views_advertisement

