from aiogram.types import Message

from main import bot, dp
from keyboards.buttons import admin_markup

from admin.necessary_following import necessary_following_func
from admin.views_save import views_save_func
from admin.bot_statistics import bot_statistics_func
from admin.mailing_everyone import mailing_everyone_func
from admin.backup_database import backup_database_func
from admin.bot_users_lang import bot_users_lang_func
from admin.views_active import views_active_func

from data.constants import ADMINS_ID
from data.messages.admin import LIST_ADMIN_COMMANDS, MAILING_MSG, BACKUP_MSG, STATISTICS_MSG,\
    NECESSARY_FOLLOWING_MSG, USERS_LANG_MSG, VIEWS_STAT_MSG, VIEWS_SAVE_MSG


# Answer to admin commands
@dp.message_handler(chat_id=ADMINS_ID, commands=['admin'])
async def get_admin_commands_handler(message: Message):
    await bot.send_message(message.chat.id, 'Все команды админа', reply_markup=admin_markup)


# Answer to admin commands
@dp.message_handler(chat_id=ADMINS_ID, text=LIST_ADMIN_COMMANDS)
async def answer_admin_command_handler(message: Message):
    chat_id = message.chat.id
    admin_command = message.text

    if admin_command == MAILING_MSG:
        await mailing_everyone_func(chat_id)

    elif admin_command == BACKUP_MSG:
        await backup_database_func(chat_id)

    elif admin_command == STATISTICS_MSG:
        await bot_statistics_func(chat_id)

    elif admin_command == NECESSARY_FOLLOWING_MSG:
        await necessary_following_func(chat_id)

    elif admin_command == USERS_LANG_MSG:
        await bot_users_lang_func(chat_id)

    elif admin_command == VIEWS_STAT_MSG:
        await views_active_func(chat_id)

    elif admin_command == VIEWS_SAVE_MSG:
        await views_save_func(chat_id)
