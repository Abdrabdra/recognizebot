import json
from datetime import date

from data.constants import LIST_LANG_CODES
from main import bot, users_db, stats_db, active_users


# Function to get bot statistics
async def bot_statistics_func(chat_id):
    waiting_message = await bot.send_message(chat_id, 'Пожалуйста, подождите...')

    statistics_db = stats_db.get('STATISTICS')
    if statistics_db is None:
        statistics = {'downloads': 0, 'errors': 0}
    else:
        statistics = json.loads(statistics_db)

    total_downloads = statistics['downloads']
    total_errors = statistics['errors']
    total_users = users_db.dbsize()

    today_date = str(date.today())

    today_total_stat = {'new': 0, 'download': 0, 'error': 0}

    for one_action in ['new', 'download', 'error']:
        for one_lang in LIST_LANG_CODES:
            action_stat_db = stats_db.get(f'{today_date}_{one_action}_{one_lang}')
            if action_stat_db is None:
                action_stat_db = 0

            today_total_stat[one_action] += int(action_stat_db)

    today_new = today_total_stat['new']
    today_downloads = today_total_stat['download']
    today_error = today_total_stat['error']

    today_active = active_users.dbsize()
    total_downloads += int(today_downloads)
    total_errors += int(today_error)

    admin_text_first = '*Статистика за все время:*\n' \
                       '   Пользователей: *{0:,}*\n' \
                       '   Скачиваний: *{1:,}*\n' \
                       '   Ошибок: *{2:,}*\n\n' \
                       '*Статистика за сегодня:*\n' \
                       '   Новых пользователей: *{3:,}*\n' \
                       '   Активных пользователей: *{4:,}*\n' \
                       '   Скачиваний: *{5:,}*\n' \
                       '   Ошибок: *{6:,}*'.format(total_users, total_downloads, total_errors, int(today_new),
                                                   int(today_active), int(today_downloads),
                                                   int(today_error))

    await bot.send_message(chat_id, admin_text_first, parse_mode='markdown')
    await waiting_message.delete()


