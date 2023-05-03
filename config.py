from aiogram.dispatcher.filters.state import State, StatesGroup
from enum import Enum

TOKEN = ''  # token from BotFather
ADMINS = ['first_example', 'second_example']  # telegram identifiers (id) of admins (not necassary).
DB = 'db.db'  # database file name

# These variables are needed only if you use Payok
RETURN_URL = 'https://t.me/anonchik_chat_bot' # Your bot link
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
