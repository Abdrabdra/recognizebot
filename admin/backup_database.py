import csv
import os

from data.constants import BOT_USERNAME
from main import users_db, bot
from utils.helpers import wrap


# Function to backup all users id and their info
async def backup_database_func(chat_id):
    waiting_message = await bot.send_message(chat_id, 'Пожалуйста, подождите...')

    file_name, file_name_1 = await get_files()

    await bot.send_document(chat_id, open(file_name, 'rb'))
    await bot.send_document(chat_id, open(file_name_1, 'rb'))

    await bot.delete_message(chat_id, waiting_message.message_id)

    os.remove(file_name)
    os.remove(file_name_1)


@wrap
def get_files():
    file_name = '{} all users id with lang 1.csv'.format(BOT_USERNAME)
    file_name_1 = '{} all users id.csv'.format(BOT_USERNAME)
    list_users_id = users_db.keys()

    with open(file_name, 'a', newline='') as csv_file:
        with open(file_name_1, 'a', newline='') as csv_file_1:
            writer = csv.writer(csv_file)
            writer_1 = csv.writer(csv_file_1)

            for i, user_id in enumerate(list_users_id):
                str_user_id = str(user_id, 'utf-8')
                if not str_user_id.isdigit():
                    continue

                user_lang_db = users_db.get(str_user_id)
                user_lang = str(user_lang_db, 'utf')

                writer.writerow([str_user_id, user_lang])
                writer_1.writerow([str_user_id])

    return file_name, file_name_1

