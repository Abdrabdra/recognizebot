from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data.messages.admin import REJECT_MSG, START_MAILING_MSG, LIST_ADMIN_COMMANDS, LIST_LANG, REMOVE_MSG, ADD_MSG, \
    LIST_VIEWS_TYPES, TOMORROW_MSG, TODAY_MSG

admin_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
for admin_command in LIST_ADMIN_COMMANDS:
    admin_button = KeyboardButton(admin_command)
    admin_markup.add(admin_button)


# Markup with languages
lang_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
list_buttons = []
for one_lang in LIST_LANG:
    list_buttons.append(KeyboardButton(one_lang))
lang_markup.add(*list_buttons)
lang_markup.add(KeyboardButton(REJECT_MSG))


reject_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
reject_button = KeyboardButton(REJECT_MSG)
reject_markup.add(reject_button)


sure_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
send_button = KeyboardButton(START_MAILING_MSG)
reject_button = KeyboardButton(REJECT_MSG)
sure_markup.add(*[send_button, reject_button])


following_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
following_button_1 = KeyboardButton(ADD_MSG)
following_button_2 = KeyboardButton(REMOVE_MSG)
following_button_3 = KeyboardButton(REJECT_MSG)
following_markup.add(*[following_button_1, following_button_2, following_button_3])


necessary_lang_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
for lang in LIST_LANG:
    necessary_lang_markup.add(KeyboardButton(lang))
necessary_lang_markup.add(KeyboardButton(REJECT_MSG))


views_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
for view_type in LIST_VIEWS_TYPES:
    views_markup.add(KeyboardButton(view_type))
views_markup.add(KeyboardButton(REJECT_MSG))


dates_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
today_button = KeyboardButton(TODAY_MSG)
tomorrow_button = KeyboardButton(TOMORROW_MSG)
reject_button = KeyboardButton(REJECT_MSG)
dates_markup.add(*[today_button, tomorrow_button, reject_button])
