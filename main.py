import asyncio
import redis
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import BOT_TOKEN

loop = asyncio.get_event_loop()
bot = Bot(BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)

stats_db = redis.StrictRedis(host='localhost', port=6379, db=1)
files_id = redis.StrictRedis(host='localhost', port=6379, db=2)
users_db = redis.StrictRedis(host='localhost', port=6379, db=3)
active_users = redis.StrictRedis(host='localhost', port=6379, db=4)


class AdminSendEveryOne(StatesGroup):
    ask_lang = State()
    ask_post = State()
    ask_send = State()


class AdminReferrals(StatesGroup):
    ask_referral = State()


class AdminSaveAdd(StatesGroup):
    ask_lang = State()
    ask_date = State()
    ask_type = State()
    ask_post = State()


class AdminFollowAdd(StatesGroup):
    ask_state = State()
    ask_lang = State()
    ask_link = State()
    ask_post = State()
    ask_range = State()

