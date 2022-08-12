from random import randint

from keyboards.inline import generate_follow_markup
from utils.helpers import send_message, get_chat_member
from data.messages.admin import ALL_LANGUAGES

necessary_follow_lang = {'ru': {}, 'en': {}, 'uz': {}}


async def check_following(chat_id, user_lang):
    # Check if necessary follow is set to user lang
    user_channel_follow = necessary_follow_lang[user_lang]
    if not user_channel_follow:
        return True

    channel_link = user_channel_follow['link']
    channel_id = user_channel_follow['id']
    follow_range = user_channel_follow['follow_range']

    # Choose randomly, if the user should follow to channel or not
    random_number = randint(0, follow_range)
    if random_number != 0:
        return True

    # Check, if the user follows the channel
    user_info = await get_chat_member(channel_id, chat_id)
    if user_info is not None and user_info['status'] != 'member':
        follow_markup = await generate_follow_markup(channel_link, user_lang)
        await send_message(chat_id, 'follow', user_lang, markup=follow_markup, parse='markdown')
        return False

    return True


async def update_following(follow_lang, channel_link=None, channel_id=None, follow_range=None, remove=False):
    global necessary_follow_lang

    if remove:
        necessary_follow_lang[follow_lang] = {}
    else:
        necessary_follow_lang[follow_lang]['link'] = channel_link
        necessary_follow_lang[follow_lang]['id'] = channel_id
        necessary_follow_lang[follow_lang]['follow_range'] = follow_range


async def get_active_following():
    list_active_langs = []
    for one_lang in necessary_follow_lang:
        lang_follow_info = necessary_follow_lang[one_lang]
        if not lang_follow_info:
            continue

        follow_url = lang_follow_info['link']
        follow_range = lang_follow_info['follow_range']
        lang_text = ALL_LANGUAGES[one_lang]
        admin_text = f'{lang_text} - {follow_url} - {follow_range}'
        list_active_langs.append(admin_text)

    if not list_active_langs:
        list_joined_text = 'Все языки стоят без обязательной подписки'
    else:
        list_joined_text = '\n'.join(list_active_langs)
    return list_joined_text

