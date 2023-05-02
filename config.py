from aiogram.dispatcher.filters.state import State, StatesGroup
from enum import Enum
# тут достаточно pip install aiogram

TOKEN = 'Токен от BotFather'
ADMINS = ['id админов через запятую']  # пока что в боте это нигде не используется ):
DB = 'db.db'  # имя файла базы данных

RETURN_URL = 'https://t.me/anonchik_chat_bot'  # ссылка для возврата после оплаты

# payok
API_ID = 'int'
API_KEY = 'str'
SHOP_ID = 'int'
SECRET_KEY = 'str'


class RegState(StatesGroup):
	name = State()
	sex = State()
	age = State()
	country = State()
	city = State()
	op_sex = State()


class SetName(Enum):
	nothing = 'nothing_name'
	waiting = 'waiting_name'


class SetAge(Enum):
	nothing = 'nothing_age'
	waiting = 'waiting_age'


class SetSex(Enum):
	nothing = 'nothing_sex'
	waiting = 'waiting_sex'


class SetCountry(Enum):
	nothing = 'nothing_country'
	waiting = 'waiting_country'


class SetCity(Enum):
	nothing = 'nothing_city'
	waiting = 'waiting_waiting'


class SetOpSex(Enum):
	nothing = 'nothing_op_sex'
	waiting = 'waiting_op_sex'
