import csv
import json
import os
from datetime import date

from utils.advertisement.views import update_views, send_views_stat
from utils.helpers import send_document
from main import stats_db, active_users
from data.constants import STATS_GROUP_ID, LIST_LANG_CODES, BOT_USERNAME

current_date = str(date.today())


async def update_statistics(action, user_lang):
    global current_date

    today_date = str(date.today())

    action_db = f'{today_date}_{action}_{user_lang}'
    total_action_db = stats_db.get(action_db)
    if total_action_db is None:
        stats_db.set(action_db, 0)
        total_action_db = 0

    if current_date != today_date:
        # Send bot and views statistics
        stat_date = current_date
        await send_day_statistics(stat_date)
        await send_views_stat(stat_date)

        # Update date and views
        current_date = str(today_date)
        await update_views(current_date)

    total_action = int(total_action_db) + 1
    stats_db.set(action_db, total_action)


async def send_day_statistics(stat_date):
    file_name, today_total_stat = await get_today_statistics(stat_date)
    await send_document(STATS_GROUP_ID, file_name, current_date)
    os.remove(file_name)

    # Update statistics
    statistics_db = stats_db.get('STATISTICS')
    if statistics_db is None:
        statistics = {'downloads': 0, 'errors': 0}
    else:
        statistics = json.loads(statistics_db)

    statistics['downloads'] += today_total_stat['download']
    statistics['errors'] += today_total_stat['error']
    stats_db.set('STATISTICS', json.dumps(statistics))

    active_users.flushdb(asynchronous=True)


async def get_today_statistics(stat_date):
    today_stat = {'download': 0, 'new': 0, 'error': 0}

    file_name = f'{stat_date} {BOT_USERNAME}.csv'
    with open(file_name, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Язык пользователя', 'Новых пользователей', 'Распизнаваний', 'Ошибок'])

        list_data = []
        for one_lang in LIST_LANG_CODES:
            list_data.append(one_lang)
            for one_action in ['new', 'download', 'error']:
                action_db_key = f'{stat_date}_{one_action}_{one_lang}'
                action_stat_db = stats_db.get(action_db_key)
                stats_db.delete(action_db_key)
                if action_stat_db is None:
                    action_stat_db = 0

                list_data.append(int(action_stat_db))
                today_stat[one_action] += int(action_stat_db)

            writer.writerow(list_data)
            list_data = []

        list_data = ['Всего', today_stat['new'], today_stat['download'], today_stat['error']]
        writer.writerow(list_data)

    return file_name, today_stat

