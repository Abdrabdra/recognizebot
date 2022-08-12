import json

from keyboards.inline import language
from main import users_db, stats_db
from data.constants import ADMINS_ID

from utils.helpers import send_message
from utils.statistics import update_statistics


async def check_user_info(chat_id, user_lang_code, referral=None):
    # If the user exists in DB, return its language
    user_lang_db = users_db.get(chat_id)
    if user_lang_db is not None and str(user_lang_db, 'utf-8') != 'None':
        user_lang = str(user_lang_db, 'utf-8')
    else:
        await update_statistics('new', user_lang_code)
        await update_referrals(referral)

        if user_lang_code in ['uz', 'ru']:
            user_lang = user_lang_code
        else:
            await send_message(chat_id, 'lang', 'ru', markup=language)
            user_lang = 'en'

        users_db.set(chat_id, user_lang)

    return user_lang


async def update_referrals(referral):
    if referral is None:
        return

    referrals_stat_db = stats_db.get('REFERRALS')
    if referrals_stat_db is None:
        stats_db.set('REFERRALS', json.dumps({}))
        referrals_stat_db = stats_db.get('REFERRALS')

    referrals_stat = json.loads(referrals_stat_db)
    if referral not in referrals_stat.keys():
        referrals_stat[referral] = {'new': 0, 'old': 0}

    referrals_stat[referral]['new'] += 1

    stats_db.set('REFERRALS', json.dumps(referrals_stat))


# Send notification that bot started working
async def on_startup(args):
    for one_admin_id in ADMINS_ID:
        await send_message(one_admin_id, 'admin-bot-start', 'ru')
