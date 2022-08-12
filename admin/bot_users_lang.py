from utils.helpers import wrap
from main import bot, users_db


async def bot_users_lang_func(chat_id):
    waiting_message = await bot.send_message(chat_id, 'Пожалуйста, подождите...')

    total, active, russian, english, uzbek, brazil, spanish, indonesian, malaysian, arabic = await get_users_id()
    user_lang_stat = 'Всего пользователей: *{0:,}*\n' \
                     'Активных: *{1:,}*\n' \
                     'Пользователи по яызкам:\n' \
                     '🇷🇺 Русский: *{2:,}*\n' \
                     '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Английский: *{3:,}*\n' \
                     '🇺🇿 Узбекский: *{4:,}*\n' \
                     '🇧🇷 Португальский: *{5:,}*\n' \
                     '🇪🇸 Испанский: *{6:,}*\n' \
                     '🇮🇩 Индонезийский: *{7:,}*\n' \
                     '🇲🇾 Малайский: *{8:,}*\n' \
                     '🇦🇪 Арабский: *{9:,}*\n'.format(total, active, russian, english, uzbek,
                                                        brazil, spanish, indonesian, malaysian, arabic)

    await bot.send_message(chat_id, user_lang_stat, parse_mode='markdown')
    await waiting_message.delete()


@wrap
def get_users_id():
    users_id = users_db.keys()

    russian = 0
    english = 0
    uzbek = 0
    brazil = 0
    spanish = 0
    indonesian = 0
    malaysian = 0
    arabic = 0
    active = 0
    total = len(users_id)

    for user_id in users_db.keys():
        str_user_id = str(user_id, 'utf-8')
        if not str_user_id.isdigit():
            continue

        user_lang_db = users_db.get(str_user_id)
        user_lang = str(user_lang_db, 'utf-8')
        if user_lang == 'None':
            continue

        active += 1

        if user_lang == 'ru':
            russian += 1
        elif user_lang == 'en':
            english += 1
        elif user_lang == 'uz':
            uzbek += 1
        elif user_lang == 'br':
            brazil += 1
        elif user_lang == 'es':
            spanish += 1
        elif user_lang == 'id':
            indonesian += 1
        elif user_lang == 'my':
            malaysian += 1
        elif user_lang == 'ar':
            arabic += 1

    return total, active, russian, english, uzbek, brazil, spanish, indonesian, malaysian, arabic
