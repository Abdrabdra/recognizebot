from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.messages.bot import msg_dict

language = InlineKeyboardMarkup(row_width=2)
lang_ru = InlineKeyboardButton(text='English 🏴󠁧󠁢󠁥󠁮󠁧󠁿󠁢󠁥󠁮󠁧󠁿󠁢󠁥󠁮󠁧󠁿', callback_data='en')
lang_en = InlineKeyboardButton(text='Русский 🇷🇺', callback_data='ru')
lang_uz = InlineKeyboardButton(text='O\'zbek 🇺🇿󠁧󠁢󠁥󠁮󠁧󠁿󠁢󠁥󠁮󠁧󠁿󠁢󠁥󠁮󠁧󠁿', callback_data='uz')
languages = lang_ru, lang_en, lang_uz
language.add(*languages)


async def generate_follow_markup(channel_link, user_lang):
    button_text1 = msg_dict[user_lang]['follow-channel-button']
    button_text2 = msg_dict[user_lang]['check-channel-button']

    follow_markup = InlineKeyboardMarkup(row_width=1)
    follow_button = InlineKeyboardButton(text=button_text1, url=channel_link)
    check_button = InlineKeyboardButton(text=button_text2, callback_data=f'check-channel!{user_lang}')
    follow_markup.add(*[follow_button, check_button])

    return follow_markup
