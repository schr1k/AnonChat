import config
from config import RegState
from config import SetName, SetAge, SetSex, SetCountry, SetCity
import keyboards as kb
from db import DbWorker

import logging
import asyncio
from datetime import datetime, timedelta
from aiopayok import Payok

from aiogram import Bot
from aiogram.types import ParseMode
from aiogram.types.message import ContentTypes
from aiogram.utils import executor, exceptions
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

db = DbWorker(config.DB)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(filename="all_log.log", level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s')
warning_log = logging.getLogger("warning_log")
warning_log.setLevel(logging.WARNING)
fh = logging.FileHandler("warning_log.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
warning_log.addHandler(fh)

pay = Payok(api_id=config.API_ID, api_key=config.API_KEY, secret_key=config.SECRET_KEY, shop=config.SHOP_ID)


# Регистрация

@dp.message_handler(lambda message: message.text == '🔙 На главную')
@dp.message_handler(commands=['start'])
async def start(message):
	try:
		db.set_state(None, message.from_user.id)
		sp = message.text.split()
		if len(sp) > 1 and not db.user_exists(message.from_user.id):
			user_id = sp[1]
			db.edit_refs(1, user_id)
			db.edit_points(1, user_id)
			if bool(db.get_notifications(user_id)[0]):
				await bot.send_message(user_id, 'Кто-то присоединился к боту по вашей ссылке!')
				if db.get_refs(user_id)[0] % 10 == 0:
					await bot.send_message(user_id, 'Вы можете отключить уведомления о новых рефах в настройках.')
		if not db.user_exists(message.from_user.id):
			await message.answer(f"🎉Добро пожаловать в анонимный чат!🎉\n"
			                     f"Перед тем как начать общение необходимо пройти регистрацию.\n"
			                     f"После регистрации вы получите <b>вип на неделю бесплатно!</b>\n"
			                     f"Начать регистрацию - /registrate\n"
			                     f"Правила чата - /rules", parse_mode='HTML')
		else:
			await message.answer(f'Привет, {db.get_name(message.from_user.id)[0]}', reply_markup=kb.main_kb)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['help'])
async def help(message):
	try:
		await message.answer(f'/start - В начало\n'
		                     f'/rules - Правила\n'
		                     f'/search - Начать поиск\n'
		                     f'/stop - Остановить диалог\n'
		                     f'/vip - Купить вип\n'
		                     f'/ref - Рефералка')
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['registrate'])
async def registrate(message):
	if not db.user_exists(message.from_user.id):
		await message.answer("Введите ваше имя.")
		await RegState.name.set()


@dp.message_handler(state=RegState.name)
async def set_name(message, state: FSMContext):
	await state.update_data(name=message.text)
	await message.answer("Теперь введите ваш пол (М/Ж).")
	await RegState.sex.set()


@dp.message_handler(state=RegState.sex)
async def set_sex(message, state: FSMContext):
	if message.text == 'м' or message.text == 'М':
		await state.update_data(sex='male')
		await message.answer("Теперь введите ваш возраст.")
		await RegState.age.set()
	elif message.text == 'ж' or message.text == 'Ж':
		await state.update_data(sex='female')
		await message.answer("Теперь введите ваш возраст.")
		await RegState.age.set()
	else:
		await message.reply("Вы ввели некорректное значение, повторите ввод.")


@dp.message_handler(state=RegState.age)
async def set_age(message, state: FSMContext):
	if 5 < int(message.text) < 100:
		await state.update_data(age=message.text)
		await message.answer("В какой стране вы живете?")
		await RegState.country.set()
	else:
		await message.reply("Вы ввели некорректное значение, повторите ввод")


@dp.message_handler(state=RegState.country)
async def set_country(message, state: FSMContext):
	await state.update_data(country=message.text)
	await message.answer("В каком городе вы живете?")
	await RegState.city.set()


@dp.message_handler(state=RegState.city)
async def set_city(message, state: FSMContext):
	await state.update_data(city=message.text)
	await message.answer("Спасибо за регистрацию! Теперь вам доступен поиск - /search.",
	                     reply_markup=kb.main_kb)
	data = await state.get_data()
	db.new_user(data['name'], data['age'], data['sex'], data['country'], data['city'], message.from_user.id)
	await state.finish()
	if db.get_vip_ends(message.from_user.id)[0] is None:
		db.edit_vip_ends((datetime.now() + timedelta(days=7)).strftime('%d.%m.%Y %H:%M'),
		                 message.from_user.id)


@dp.message_handler(commands=['rules'])
@dp.message_handler(lambda message: message.text == 'Правила 📖')
async def rules(message):
	try:
		await message.answer(f'<b>В чате запрещены:</b>\n'
		                     f'1) Любые упоминания психоактивных веществ (наркотиков).\n'
		                     f'2) Обмен, распространение любых 18+ материалов\n'
		                     f'3) Любая реклама, спам, продажа чего либо.\n'
		                     f'4) Оскорбительное поведение.\n'
		                     f'5) Любые действия, нарушающие правила Telegram.\n',
		                     parse_mode='HTML', reply_markup=kb.to_main_kb)
	except Exception as e:
		warning_log.warning(e)


# Настройки


@dp.message_handler(commands=['edit_name'])
@dp.callback_query_handler(lambda call: call.data == 'name')
async def edit_name(call):
	await bot.answer_callback_query(call.id, 'Введите имя:')
	db.set_state(SetName.waiting.value, call.from_user.id)


@dp.message_handler(lambda message: db.get_state(message.from_user.id)[0] == SetName.waiting.value)
async def editing_name(message):
	try:
		db.edit_name(message.text, message.from_user.id)
		await bot.send_message(message.from_user.id, "Имя сохранено!", reply_markup=kb.main_kb)
		db.set_state(SetName.nothing.value, message.from_user.id)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['edit_age'])
@dp.callback_query_handler(lambda call: call.data == 'age')
async def edit_age(call):
	await bot.answer_callback_query(call.id, 'Введите возраст:')
	db.set_state(SetAge.waiting.value, call.from_user.id)


@dp.message_handler(lambda message: db.get_state(message.from_user.id)[0] == SetAge.waiting.value)
async def editing_age(message):
	try:
		db.edit_age(message.text, message.from_user.id)
		await bot.send_message(message.from_user.id, "Возраст сохранен!", reply_markup=kb.main_kb)
		db.set_state(SetAge.nothing.value, message.from_user.id)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['edit_sex'])
@dp.callback_query_handler(lambda call: call.data == 'sex')
async def edit_sex(call):
	await call.message.edit_reply_markup(reply_markup=kb.sex_kb)
	await bot.answer_callback_query(call.id, 'Выберите пол:')
	db.set_state(SetSex.waiting.value, call.from_user.id)


@dp.callback_query_handler(lambda call: call.data == 'male' or call.data == 'female')
async def editing_sex(call):
	try:
		if call.data == 'male':
			db.edit_sex('male', call.from_user.id)
			await bot.send_message(call.from_user.id, "Пол сохранен!", reply_markup=kb.main_kb)
			await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
			db.set_state(SetSex.nothing.value, call.from_user.id)
		elif call.data == 'female':
			db.edit_sex('female', call.from_user.id)
			await bot.send_message(call.from_user.id, "Пол сохранен!", reply_markup=kb.main_kb)
			await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
			db.set_state(SetSex.nothing.value, call.from_user.id)
		else:
			await call.reply("Вы ввели некорректное значение, повторите ввод")
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['edit_country'])
@dp.callback_query_handler(lambda call: call.data == 'country')
async def edit_country(call):
	await bot.answer_callback_query(call.id, 'Введите страну:')
	db.set_state(SetCountry.waiting.value, call.from_user.id)


@dp.message_handler(lambda message: db.get_state(message.from_user.id)[0] == SetCountry.waiting.value)
async def editing_country(message):
	try:
		db.edit_country(message.text, message.from_user.id)
		await bot.send_message(message.from_user.id, "Страна сохранена!", reply_markup=kb.main_kb)
		db.set_state(SetCountry.nothing.value, message.from_user.id)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['edit_city'])
@dp.callback_query_handler(lambda call: call.data == 'city')
async def edit_city(call):
	await bot.answer_callback_query(call.id, 'Введите город:')
	db.set_state(SetCity.waiting.value, call.from_user.id)


@dp.message_handler(lambda message: db.get_state(message.from_user.id)[0] == SetCity.waiting.value)
async def editing_city(message):
	try:
		db.edit_city(message.text, message.from_user.id)
		await bot.send_message(message.from_user.id, "Город сохранен!", reply_markup=kb.main_kb)
		db.set_state(SetCity.nothing.value, message.from_user.id)
	except Exception as e:
		warning_log.warning(e)


# @dp.message_handler(commands=['edit_op_sex'])
# @dp.callback_query_handler(lambda call: call.data == 'op_sex')
# async def edit_op_sex(call):
#     await bot.answer_callback_query(call.id, 'Введите пол собеседника:')
#     db.set_state(SetSets.waiting.value, call.from_user.id)


# @dp.message_handler(lambda message: db.get_state(message.from_user.id)[0] == SetOpSex.waiting.value)
# async def editing_op_sex(message):
#     try:
#         db.edit_op_sex(message.text, message.from_user.id)
#         await bot.send_message(message.from_user.id, "Пол собеседника сохранен!")
#         db.set_state(SetSets.nothing.value, message.from_user.id)
#     except Exception as e:
#         warning_log.warning(e)


# Профиль


@dp.message_handler(commands=['profile'])
@dp.message_handler(lambda message: message.text == 'Профиль 👤')
async def profile(message):
	try:
		sex = 'Неизвестно'
		user_id = message.from_user.id
		if db.get_sex(user_id)[0] == 'male':
			sex = 'Мужской'
		elif db.get_sex(user_id)[0] == 'female':
			sex = 'Женский'
		await message.answer(
			f'🅰️ Имя: {db.get_name(user_id)[0]}\n\n'
			f'🔞 Возраст: {db.get_age(user_id)[0]}\n\n'
			f'👫 Пол: {sex}\n\n'
			f'🌍 Страна: {db.get_country(user_id)[0]}\n\n'
			f'🏙️ Город: {db.get_city(user_id)[0]}',
			reply_markup=kb.profile_kb)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['settings'])
@dp.message_handler(lambda message: message.text == '⚙️ Изменить профиль')
async def settings(message):
	await message.answer('Выберите параметр который вы хотите изменить:', reply_markup=kb.settings_kb)


@dp.message_handler(commands=['statistic'])
@dp.message_handler(lambda message: message.text == '📈 Статистика')
async def profile(message):
	try:
		user_id = message.from_user.id
		await message.answer(
			f'💬 Чатов: {db.get_chats(user_id)[0]}\n\n'
			f'⌨️ Сообщений: {db.get_messages(user_id)[0]}\n\n'
			f'👍 Лайков: {db.get_likes(user_id)[0]}\n\n'
			f'👎 Дизлайков: {db.get_dislikes(user_id)[0]}\n\n'
			f'👨‍💻 Пользователей приглашено: {db.get_refs(user_id)[0]}',
			reply_markup=kb.statistic_kb)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['ref'])
@dp.message_handler(lambda message: message.text == '💼 Рефералка' or message.text == '🆓 Получить вип бесплатно')
async def ref(message):
	try:
		user_id = message.from_user.id
		await message.answer(f'Распространяйте свою реферальую ссылку, чтобы получать 💎\n'
		                     f'1 переход по ссылке = 1 💎\n'
		                     f'5 💎 = 1 день VIP-статуса 👑\n')
		await message.answer(f'У вас {db.get_points(user_id)[0]} 💎')
		if bool(db.get_notifications(message.from_user.id)[0]):
			await message.answer(f'🆔 Ваша реферальная ссылка:\n'
			                     f'{"https://t.me/anonchik_chat_bot?start=" + str(user_id)}',
			                     disable_web_page_preview=True, reply_markup=kb.off_kb)
		else:
			await message.answer(f'🆔 Ваша реферальная ссылка:\n'
			                     f'{"https://t.me/anonchik_chat_bot?start=" + str(user_id)}',
			                     disable_web_page_preview=True, reply_markup=kb.on_kb)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['trade'])
@dp.message_handler(lambda message: message.text == 'Обменять 💎')
async def trade(message):
	try:
		if db.get_points(message.from_user.id)[0] >= 5:
			db.edit_points(-5, message.from_user.id)
			if db.get_vip_ends(message.from_user.id)[0] is None:
				db.edit_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'),
				                 message.from_user.id)
				await message.answer('Успешно!')
			else:
				db.edit_vip_ends((datetime.strptime(db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') +
				                  timedelta(days=1)).strftime('%d.%m.%Y %H:%M'), message.from_user.id)
			await message.answer('Успешно!')
		else:
			await message.answer('У вас недостаточно баллов')
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(lambda message: message.text == 'Включить уведомления 🔔')
async def notifications(message):
	try:
		db.edit_notifications(1, message.from_user.id)
		await message.answer('Уведомления о новых рефералах включены!', reply_markup=kb.to_main_kb)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(lambda message: message.text == 'Выключить уведомления 🔕')
async def notifications(message):
	try:
		db.edit_notifications(0, message.from_user.id)
		await message.answer('Уведомления о новых рефералах выключены!', reply_markup=kb.to_main_kb)
	except Exception as e:
		warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data == 'on')
async def notifications_on(call):
	await db.edit_notifications(1, call.from_user.id)
	await call.reply('Уведомления включены')


@dp.callback_query_handler(lambda call: call.data == 'off')
async def notifications_off(call):
	await db.edit_notifications(1, call.from_user.id)
	await call.reply('Уведомления выключены')


@dp.message_handler(commands=['top'])
@dp.message_handler(lambda message: message.text == '🏆 Рейтинги')
async def top(message):
	try:
		await message.answer('Ниже представлены рейтинги по разным критериям', reply_markup=kb.top_kb)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(lambda message: message.text == '🔝 Топ 5 по сообщениям')
async def top(message):
	try:
		sp = list(db.top_messages())
		for i in range(len(sp)):
			if i == 0:
				c = '🥇'
			elif i == 1:
				c = '🥈'
			elif i == 2:
				c = '🥉'
			else:
				c = str(i + 1) + '.'
			await message.answer(f'{c} {sp[i][0]} — <b>{sp[i][1]}</b> <i>сообщений</i>', parse_mode='HTML')
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(lambda message: message.text == '🔝 Топ 5 по лайкам')
async def top(message):
	try:
		sp = list(db.top_likes())
		for i in range(len(sp)):
			if i == 0:
				c = '🥇'
			elif i == 1:
				c = '🥈'
			elif i == 2:
				c = '🥉'
			else:
				c = str(i + 1) + '.'
			await message.answer(f'{c} {sp[i][0]} — <b>{sp[i][1]}</b> <i>лайков</i>', parse_mode='HTML')
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(lambda message: message.text == '🔝 Топ 5 по рефам')
async def top(message):
	try:
		sp = list(db.top_refs())
		for i in range(len(sp)):
			if i == 0:
				c = '🥇'
			elif i == 1:
				c = '🥈'
			elif i == 2:
				c = '🥉'
			else:
				c = str(i + 1) + '.'
			await message.answer(f'{c} {sp[i][0]} — <b>{sp[i][1]}</b> <i>рефов</i>', parse_mode='HTML')
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['vip'])
@dp.message_handler(lambda message: message.text == 'Вип 👑')
async def vip(message):
	try:
		if db.get_vip_ends(message.from_user.id)[0] is not None:
			if datetime.strptime(db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') > datetime.now():
				delta = datetime.strptime(db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') - datetime.now()
				await message.answer(
					f'Осталось {delta.days} дней, {delta.seconds // 3600} часов, {delta.seconds // 60 % 60} минут Випа',
					reply_markup=kb.vip_kb)
			else:
				await message.answer(f'Вип дает:\n'
				                     f'1) Поиск по полу.\n'
				                     f'2) Подробная информацию о собеседнике: отзывы, имя, пол, возраст, страна...\n'
				                     f'3) <b>Первое место в очереди.\n</b>'
				                     f'<i>Это далеко не все, функции будут постоянно добавляться</i>',
				                     reply_markup=kb.vip_kb, parse_mode='HTML')
		else:
			await message.answer(f'Вип дает:\n'
			                     f'1) Поиск по полу.\n'
			                     f'2) Подробная информацию о собеседнике: отзывы, имя, возраст, пол, страна, город\n'
			                     f'3) <b>Первое место в очереди.\n</b>'
			                     f'<i>Это далеко не все, функции будут постоянно добавляться</i>',
			                     reply_markup=kb.vip_kb, parse_mode='HTML')
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['buy_vip'])
@dp.message_handler(lambda message: message.text == '💰 Купить/Продлить вип')
async def buy_vip(message):
	try:
		await message.answer('Выберите длительность:', reply_markup=kb.buy_kb)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(lambda message: message.text == '👑 Вип на день - 20₽')
async def buy_day(message):
	try:
		c = 0
		tg_id = message.from_user.id
		db.edit_order_id(1, tg_id)
		payment_id = f'{tg_id}-{int(db.get_order_id(tg_id)[0]) + 1}'
		payments = await pay.create_pay(amount=20, currency='RUB', success_url=config.RETURN_URL, desc=payment_id,
		                                payment=payment_id)
		await message.answer(f'<a href="{payments}">Оплатить 20 рублей</a>', parse_mode='HTML')
		flag1 = False
		while not flag1:
			for i in [dict(i) for i in list(await pay.get_transactions())]:
				if i['payment_id'] == payment_id:
					if c >= 3600:
						flag1 = True
						break
					if i['transaction_status'] == 1:
						await message.answer('Успешно')
						if db.get_vip_ends(tg_id)[0] is None:
							db.edit_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'), tg_id)
						else:
							db.edit_vip_ends(
								(datetime.strptime(db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') +
								 timedelta(days=1)).strftime('%d.%m.%Y %H:%M'), message.from_user.id)
						flag1 = True
						break
					else:
						await asyncio.sleep(3)
						c += 3
				else:
					await asyncio.sleep(3)
					c += 3
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(lambda message: message.text == '👑 Вип на неделю - 100₽')
async def buy_week(message):
	try:
		c = 0
		tg_id = message.from_user.id
		db.edit_order_id(1, tg_id)
		payment_id = f'{tg_id}-{int(db.get_order_id(tg_id)[0]) + 1}'
		payments = await pay.create_pay(amount=100, currency='RUB', success_url=config.RETURN_URL, desc=payment_id,
		                                payment=payment_id)
		await message.answer(f'<a href="{payments}">Оплатить 100 рублей</a>', parse_mode='HTML')
		flag1 = False
		while not flag1:
			for i in [dict(i) for i in list(await pay.get_transactions())]:
				if i['payment_id'] == payment_id:
					if c >= 3600:
						flag1 = True
						break
					if i['transaction_status'] == 1:
						await message.answer('Успешно')
						if db.get_vip_ends(tg_id)[0] is None:
							db.edit_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'), tg_id)
						else:
							db.edit_vip_ends(
								(datetime.strptime(db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') +
								 timedelta(days=7)).strftime('%d.%m.%Y %H:%M'), message.from_user.id)
						flag1 = True
						break
					else:
						await asyncio.sleep(3)
						c += 3
				else:
					await asyncio.sleep(3)
					c += 3
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(lambda message: message.text == '👑 Вип на месяц - 300₽')
async def buy_month(message):
	try:
		c = 0
		tg_id = message.from_user.id
		db.edit_order_id(1, tg_id)
		payment_id = f'{tg_id}-{int(db.get_order_id(tg_id)[0]) + 1}'
		payments = await pay.create_pay(amount=300, currency='RUB', success_url=config.RETURN_URL, desc=payment_id,
		                                payment=payment_id)
		await message.answer(f'<a href="{payments}">Оплатить 300 рублей</a>', parse_mode='HTML')
		flag1 = False
		while not flag1:
			for i in [dict(i) for i in list(await pay.get_transactions())]:
				if i['payment_id'] == payment_id:
					if c >= 3600:
						flag1 = True
						break
					if i['transaction_status'] == 1:
						await message.answer('Успешно')
						if db.get_vip_ends(tg_id)[0] is None:
							db.edit_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'), tg_id)
						else:
							db.edit_vip_ends(
								(datetime.strptime(db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') +
								 timedelta(days=31)).strftime('%d.%m.%Y %H:%M'), message.from_user.id)
						flag1 = True
						break
					else:
						await asyncio.sleep(3)
						c += 3
				else:
					await asyncio.sleep(3)
					c += 3
	except Exception as e:
		warning_log.warning(e)


# Поиск


@dp.message_handler(commands=['cancel_search'])
@dp.message_handler(lambda message: message.text == '🚫 Отменить поиск')
async def cancel_search(message):
	try:
		await message.answer('Поиск отменен. 😥\nОтправьте /search, чтобы начать поиск',
		                     reply_markup=kb.main_kb)
		db.delete_from_queue(message.from_user.id)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['like'])
@dp.message_handler(lambda message: message.text == '👍 Лайк')
async def like(message):
	try:
		await message.answer('Спасибо за отзыв!', reply_markup=kb.main_kb)
		db.edit_likes(1, db.get_last_connect(message.from_user.id)[0])
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['dislike'])
@dp.message_handler(lambda message: message.text == '👎 Дизлайк')
async def dislike(message):
	try:
		await message.answer('Спасибо за отзыв!', reply_markup=kb.main_kb)
		db.edit_dislikes(1, db.get_last_connect(message.from_user.id)[0])
	except Exception as e:
		warning_log.warning(e)


class Chatting(StatesGroup):
	msg = State()


@dp.message_handler(commands=['search'])
@dp.message_handler(lambda message: message.text == 'Рандом 🔀' or message.text == '➡️ Следующий диалог')
async def search(message):
	try:
		db.add_to_queue(message.from_user.id, db.get_sex(message.from_user.id)[0])
		await message.answer('Ищем для вас человечка.. 🔍', reply_markup=kb.cancel_search_kb)
		while True:
			await asyncio.sleep(0.5)
			if db.search(message.from_user.id)[0] is not None:
				db.update_connect_with(db.search(message.from_user.id)[0], message.from_user.id)
				db.update_connect_with(message.from_user.id, db.search(message.from_user.id)[0])
				break
		while True:
			await asyncio.sleep(0.5)
			if db.get_connect_with(message.from_user.id)[0] is not None:
				db.delete_from_queue(message.from_user.id)
				db.delete_from_queue(db.get_connect_with(message.from_user.id)[0])
				break
		if db.get_vip_ends(message.from_user.id)[0] is not None and datetime.strptime(
			db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') > datetime.now():
			sex = 'Неизвестно'
			user_id = db.get_connect_with(message.from_user.id)[0]
			if db.get_sex(user_id)[0] == 'male':
				sex = 'Мужской'
			elif db.get_sex(user_id)[0] == 'female':
				sex = 'Женский'
			await bot.send_message(message.from_user.id,
			                       f'Нашёл кое-кого для тебя 💕\n'
			                       f'🅰️ Имя: {db.get_name(user_id)[0]}\n'
			                       f'🔞 Возраст: {db.get_age(user_id)[0]}\n'
			                       f'👫 Пол: {sex}\n'
			                       f'🌍 Страна: {db.get_country(user_id)[0]}\n'
			                       f'🏙️ Город: {db.get_city(user_id)[0]}\n'
			                       f'👍: {db.get_likes(user_id)[0]} 👎: {db.get_dislikes(user_id)[0]}\n',
			                       reply_markup=kb.stop_kb)
		else:
			await bot.send_message(message.from_user.id, 'Нашёл кое-кого для тебя 💕', reply_markup=kb.stop_kb)
		if db.get_vip_ends(db.get_connect_with(message.from_user.id)[0])[0] is not None and datetime.strptime(
			db.get_vip_ends(db.get_connect_with(message.from_user.id)[0])[0], '%d.%m.%Y %H:%M') > datetime.now():
			sex = 'Неизвестно'
			user_id = message.from_user.id
			if db.get_sex(user_id)[0] == 'male':
				sex = 'Мужской'
			elif db.get_sex(user_id)[0] == 'female':
				sex = 'Женский'
			await bot.send_message(db.get_connect_with(message.from_user.id)[0],
			                       f'Нашёл кое-кого для тебя 💕\n'
			                       f'🅰️ Имя: {db.get_name(user_id)[0]}\n'
			                       f'🔞 Возраст: {db.get_age(user_id)[0]}\n'
			                       f'👫 Пол: {sex}\n'
			                       f'🌍 Страна: {db.get_country(user_id)[0]}\n'
			                       f'🏙️ Город: {db.get_city(user_id)[0]}\n'
			                       f'👍: {db.get_likes(user_id)[0]} 👎: {db.get_dislikes(user_id)[0]}\n',
			                       reply_markup=kb.stop_kb)
		else:
			await bot.send_message(db.get_connect_with(message.from_user.id)[0], 'Нашёл кое-кого для тебя 💕',
			                       reply_markup=kb.stop_kb)
		await Chatting.msg.set()
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['search_male'])
@dp.message_handler(lambda message: message.text == 'Найти ♂️')
async def search_male(message):
	try:
		if db.get_vip_ends(message.from_user.id)[0] is not None and datetime.strptime(
			db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') > datetime.now():
			db.add_to_queue_vip(message.from_user.id, db.get_sex(message.from_user.id)[0], 'male')
			await message.answer('Ищем для вас человечка.. 🔍', reply_markup=kb.cancel_search_kb)
			while True:
				await asyncio.sleep(0.5)
				if db.search_vip(message.from_user.id, db.get_sex(message.from_user.id)[0], 'male')[0] is not None:
					db.update_connect_with(
						db.search_vip(message.from_user.id, db.get_sex(message.from_user.id)[0], 'male')[0],
						message.from_user.id)
					db.update_connect_with(
						message.from_user.id, db.search_vip(message.from_user.id,
						                                    db.get_sex(message.from_user.id)[0], 'male')[0])
					break
			while True:
				await asyncio.sleep(0.5)
				if db.get_connect_with(message.from_user.id)[0] is not None:
					db.delete_from_queue(message.from_user.id)
					db.delete_from_queue(db.get_connect_with(message.from_user.id)[0])
					break
				if db.get_vip_ends(message.from_user.id)[0] is not None and datetime.strptime(
					db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') > datetime.now():
					sex = 'Неизвестно'
					user_id = db.get_connect_with(message.from_user.id)[0]
					if db.get_sex(user_id)[0] == 'male':
						sex = 'Мужской'
					elif db.get_sex(user_id)[0] == 'female':
						sex = 'Женский'
					await bot.send_message(message.from_user.id,
					                       f'Нашёл кое-кого для тебя 💕\n'
					                       f'🅰️ Имя: {db.get_name(user_id)[0]}\n'
					                       f'🔞 Возраст: {db.get_age(user_id)[0]}\n'
					                       f'👫 Пол: {sex}\n'
					                       f'🌍 Страна: {db.get_country(user_id)[0]}\n'
					                       f'🏙️ Город: {db.get_city(user_id)[0]}\n'
					                       f'👍: {db.get_likes(user_id)[0]} 👎: {db.get_dislikes(user_id)[0]}\n',
					                       reply_markup=kb.stop_kb)
				else:
					await bot.send_message(message.from_user.id, 'Нашёл кое-кого для тебя 💕', reply_markup=kb.stop_kb)
				if db.get_vip_ends(db.get_connect_with(message.from_user.id)[0])[0] is not None and datetime.strptime(
					db.get_vip_ends(db.get_connect_with(message.from_user.id)[0])[0],
					'%d.%m.%Y %H:%M') > datetime.now():
					sex = 'Неизвестно'
					user_id = message.from_user.id
					if db.get_sex(user_id)[0] == 'male':
						sex = 'Мужской'
					elif db.get_sex(user_id)[0] == 'female':
						sex = 'Женский'
					await bot.send_message(db.get_connect_with(message.from_user.id)[0],
					                       f'Нашёл кое-кого для тебя 💕\n'
					                       f'🅰️ Имя: {db.get_name(user_id)[0]}\n'
					                       f'🔞 Возраст: {db.get_age(user_id)[0]}\n'
					                       f'👫 Пол: {sex}\n'
					                       f'🌍 Страна: {db.get_country(user_id)[0]}\n'
					                       f'🏙️ Город: {db.get_city(user_id)[0]}\n'
					                       f'👍: {db.get_likes(user_id)[0]} 👎: {db.get_dislikes(user_id)[0]}\n',
					                       reply_markup=kb.stop_kb)
				else:
					await bot.send_message(db.get_connect_with(message.from_user.id)[0], 'Нашёл кое-кого для тебя 💕',
					                       reply_markup=kb.stop_kb)
				await Chatting.msg.set()
		else:
			await message.answer('Поиск по полу доступен только для 👑 вип пользователей')
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(commands=['search_female'])
@dp.message_handler(lambda message: message.text == 'Найти ♀️')
async def search_female(message):
	try:
		if db.get_vip_ends(message.from_user.id)[0] is not None and datetime.strptime(
			db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') > datetime.now():
			db.add_to_queue_vip(message.from_user.id, db.get_sex(message.from_user.id)[0], 'female')
			await message.answer('Ищем для вас человечка.. 🔍', reply_markup=kb.cancel_search_kb)
			while True:
				await asyncio.sleep(0.5)
				if db.search_vip(message.from_user.id, db.get_sex(message.from_user.id)[0], 'female')[0] is not None:
					db.update_connect_with(
						db.search_vip(message.from_user.id, db.get_sex(message.from_user.id)[0], 'female')[0],
						message.from_user.id)
					db.update_connect_with(
						message.from_user.id, db.search_vip(message.from_user.id,
						                                    db.get_sex(message.from_user.id)[0], 'female')[0])
					break
			while True:
				await asyncio.sleep(0.5)
				if db.get_connect_with(message.from_user.id)[0] is not None:
					db.delete_from_queue(message.from_user.id)
					db.delete_from_queue(db.get_connect_with(message.from_user.id)[0])
					break
				if db.get_vip_ends(message.from_user.id)[0] is not None and datetime.strptime(
					db.get_vip_ends(message.from_user.id)[0], '%d.%m.%Y %H:%M') > datetime.now():
					sex = 'Неизвестно'
					user_id = db.get_connect_with(message.from_user.id)[0]
					if db.get_sex(user_id)[0] == 'male':
						sex = 'Мужской'
					elif db.get_sex(user_id)[0] == 'female':
						sex = 'Женский'
					await bot.send_message(message.from_user.id,
					                       f'Нашёл кое-кого для тебя 💕\n'
					                       f'🅰️ Имя: {db.get_name(user_id)[0]}\n'
					                       f'🔞 Возраст: {db.get_age(user_id)[0]}\n'
					                       f'👫 Пол: {sex}\n'
					                       f'🌍 Страна: {db.get_country(user_id)[0]}\n'
					                       f'🏙️ Город: {db.get_city(user_id)[0]}\n'
					                       f'👍: {db.get_likes(user_id)[0]} 👎: {db.get_dislikes(user_id)[0]}\n',
					                       reply_markup=kb.stop_kb)
				else:
					await bot.send_message(message.from_user.id, 'Нашёл кое-кого для тебя 💕', reply_markup=kb.stop_kb)
				if db.get_vip_ends(db.get_connect_with(message.from_user.id)[0])[0] is not None and datetime.strptime(
					db.get_vip_ends(db.get_connect_with(message.from_user.id)[0])[0],
					'%d.%m.%Y %H:%M') > datetime.now():
					sex = 'Неизвестно'
					user_id = message.from_user.id
					if db.get_sex(user_id)[0] == 'male':
						sex = 'Мужской'
					elif db.get_sex(user_id)[0] == 'female':
						sex = 'Женский'
					await bot.send_message(db.get_connect_with(message.from_user.id)[0],
					                       f'Нашёл кое-кого для тебя 💕\n'
					                       f'🅰️ Имя: {db.get_name(user_id)[0]}\n'
					                       f'🔞 Возраст: {db.get_age(user_id)[0]}\n'
					                       f'👫 Пол: {sex}\n'
					                       f'🌍 Страна: {db.get_country(user_id)[0]}\n'
					                       f'🏙️ Город: {db.get_city(user_id)[0]}\n'
					                       f'👍: {db.get_likes(user_id)[0]} 👎: {db.get_dislikes(user_id)[0]}\n',
					                       reply_markup=kb.stop_kb)
				else:
					await bot.send_message(db.get_connect_with(message.from_user.id)[0], 'Нашёл кое-кого для тебя 💕',
					                       reply_markup=kb.stop_kb)
				await Chatting.msg.set()
		else:
			await message.answer('Поиск по полу доступен только для 👑 вип пользователей')
	except Exception as e:
		warning_log.warning(e)


# @dp.message_handler(lambda message: message.text == '🙎‍♂️ Парня' or message.text == '🙍‍♀️ Девушку')
# async def choose_sex(message):
#     try:
#         if db.queue_exists(message.from_user.id):
#             db.delete_from_queue(message.from_user.id)
#         if message.text == '🙎‍♂️ Парня':
#             db.add_to_queue(message.from_user.id, db.get_sex(message.from_user.id)[0], 'male')
#             await message.answer('Ищем для вас человечка.. 🔍', reply_markup=kb.stop_kb)
#         elif message.text == '🙍‍♀️ Девушку':
#             db.add_to_queue(message.from_user.id, db.get_sex(message.from_user.id)[0], 'female')
#             await message.answer('Ищем для вас человечка.. 🔍', reply_markup=kb.stop_kb)
#
#         while True:
#             await asyncio.sleep(0.5)
#             if db.search(message.from_user.id)[0] is not None:
#                 if db.get_op_sex(db.search(message.from_user.id)[0])[0] == db.get_sex(message.from_user.id)[0]:
#                     try:
#                         db.update_connect_with(db.search(message.from_user.id)[0], message.from_user.id)
#                         db.update_connect_with(message.from_user.id, db.search(message.from_user.id)[0])
#                         break
#                     except Exception as e:
#                         print(e)
#             while True:
#                 await asyncio.sleep(0.5)
#                 if db.get_connect_with(message.from_user.id)[0] is not None:
#                     break
#             try:
#                 db.delete_from_queue(message.from_user.id)
#                 db.delete_from_queue(db.get_connect_with(message.from_user.id)[0])
#             except:
#                 pass
#             await Chatting.msg.set()
#             await bot.send_message(db.get_connect_with(message.from_user.id)[0], 'Нашёл кое-кого для тебя 💕',
#                                    reply_markup=kb.stop_kb)
#             await bot.send_message(message.from_user.id, 'Нашёл кое-кого для тебя 💕',
#                                    reply_markup=kb.stop_kb)
#             return
#     except Exception as e:
#         warning_log.warning(e)
#         await send_to_channel_log_exception(message, e)


@dp.message_handler(content_types=ContentTypes.TEXT)
@dp.message_handler(state=Chatting.msg)
async def chatting(message, state: FSMContext):
	try:
		await state.update_data(msg=message.text)
		user_data = await state.get_data()

		if user_data['msg'] == '🏹Отправить ссылку на себя' or user_data['msg'] == '/link':
			if message.from_user.username is None:
				await bot.send_message(db.get_connect_with(message.from_user.id)[0],
				                       'Пользователь не заполнил никнейм в настройках телеграма!')
			else:
				await message.answer('@' + message.from_user.username)
		elif user_data['msg'] == '🛑 Остановить диалог' or user_data['msg'] == '/stop':
			await state.finish()
			await bot.send_message(message.from_user.id,
			                       'Диалог остановлен 😞\nВы можете оценить собеседника ниже',
			                       reply_markup=kb.search_kb, parse_mode=ParseMode.HTML)
			await bot.send_message(db.get_connect_with(message.from_user.id)[0],
			                       'Диалог остановлен 😞\nВы можете оценить собеседника ниже',
			                       reply_markup=kb.search_kb, parse_mode=ParseMode.HTML)
			db.delete_from_queue(db.get_connect_with(message.from_user.id)[0])
			db.delete_from_queue(message.from_user.id)
			db.edit_chats(1, db.get_connect_with(message.from_user.id)[0])
			db.edit_chats(1, message.from_user.id)
			db.save_last_connect(db.get_connect_with(message.from_user.id)[0])
			db.save_last_connect(message.from_user.id)
			db.update_connect_with(None, db.get_connect_with(message.from_user.id)[0])
			db.update_connect_with(None, message.from_user.id)

		elif user_data['msg'].startswith('/admin'):
			if str(message.from_user.id) in config.ADMINS:
				msg = user_data['msg'].strip('/admin')
				print(msg)
				await bot.send_message(db.get_connect_with(message.from_user.id)[0], f'Cообщение от админа:\n{msg}')
			else:
				await message.answer('Отказано в доступе')

		# elif user_data['msg'] == '➡️Следующий диалог':
		#     await search(message, state)
		#
		# elif user_data['msg'] == 'Подбросить монетку🎲':
		#     coin = random.randint(1, 2)
		#
		#     if coin == 1:
		#         coin = text(italic('Решка'))
		#     else:
		#         coin = text(italic('Орёл'))
		#
		#     await message.answer(coin, parse_mode=ParseMode.MARKDOWN)
		#     await bot.send_message(db.get_connect_with(message.from_user.id)[0], coin,
		#     parse_mode=ParseMode.MARKDOWN)
		#
		# elif user_data['msg'] == 'Назад':
		#     await state.finish()

		else:
			await bot.send_message(db.get_connect_with(message.from_user.id)[0], user_data['msg'])
			db.log_message(message.from_user.id, user_data['msg'])
			db.edit_messages(1, message.from_user.id)

	except exceptions.ChatIdIsEmpty:
		await state.finish()

	except exceptions.BotBlocked:
		await message.answer('Пользователь вышел из чат бота!')
		await state.finish()

	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(content_types=['photo'])
@dp.message_handler(state=Chatting.msg)
async def chatting_photo(message, state: FSMContext):
	try:
		await state.update_data(msg=message.text, photo=message.photo[-1])
		user_data = await state.get_data()
		await bot.send_photo(db.get_connect_with(message.from_user.id)[0], user_data['photo'].file_id,
		                     caption=user_data['msg'])
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(content_types=['video'])
@dp.message_handler(state=Chatting.msg)
async def chatting_video(message, state: FSMContext):
	try:
		await bot.send_video(db.get_connect_with(message.from_user.id)[0], message.video.file_id,
		                     caption=message.text)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(content_types=['animation'])
@dp.message_handler(state=Chatting.msg)
async def chatting_gif(message, state: FSMContext):
	try:
		await bot.send_animation(db.get_connect_with(message.from_user.id)[0], message.animation.file_id,
		                         caption=message.text)
	except Exception as e:
		warning_log.warning(e)


@dp.message_handler(content_types=['sticker'])
@dp.message_handler(state=Chatting.msg)
async def chatting_sticker(message, state: FSMContext):
	try:
		await bot.send_sticker(db.get_connect_with(message.from_user.id)[0], message.sticker.file_id)
	except Exception as e:
		warning_log.warning(e)


# @dp.message_handler(commands=['back'])
# @dp.message_handler(lambda message: message.text == 'Назад')
# async def back(message, state: FSMContext):
#     await state.finish()


# логи в телеграм канал
# async def send_to_channel_log(message):
#     await bot.send_message(-1111111,
#                            f'ID - {str(message.from_user.id)}\nusername - {str(
#                            message.from_user.username)}\nmessage - {str(message.text)}')
#
#
# async def send_to_channel_log_exception(message, except_name):
#     await bot.send_message(-111111111, f'Ошибка\n\n{except_name}')


@dp.message_handler()
async def end(message):
	await message.answer('Я не знаю, что с этим делать 😲\nЯ просто напомню, что есть команды /start и /help')


if __name__ == '__main__':
	print('Работаем👌')
	executor.start_polling(dp, skip_updates=True)
