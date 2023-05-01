from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


to_main = KeyboardButton('🔙 На главную')

cancel_search_kb = ReplyKeyboardMarkup(
    resize_keyboard=True).add('🚫 Отменить поиск')

stop_kb = ReplyKeyboardMarkup(one_time_keyboard=True,
                              resize_keyboard=True).add('🛑 Остановить диалог')

like = KeyboardButton('👍 Лайк')
dislike = KeyboardButton('👎 Дизлайк')
next_dialog = KeyboardButton('➡️ Следующий диалог')
search_kb = ReplyKeyboardMarkup(
    one_time_keyboard=True, resize_keyboard=True).row(like, dislike).add(next_dialog).add(to_main)

like = KeyboardButton('👍 Лайк')
dislike = KeyboardButton('👎 Дизлайк')
next_dialog = KeyboardButton('➡️ Следующий диалог (♂️)')
search_male_kb = ReplyKeyboardMarkup(
    one_time_keyboard=True, resize_keyboard=True).row(like, dislike).add(next_dialog).add(to_main)

like = KeyboardButton('👍 Лайк')
dislike = KeyboardButton('👎 Дизлайк')
next_dialog = KeyboardButton('➡️ Следующий диалог (♀️)')
search_female_kb = ReplyKeyboardMarkup(
    one_time_keyboard=True, resize_keyboard=True).row(like, dislike).add(next_dialog).add(to_main)

man = KeyboardButton('Найти ♂️')
random = KeyboardButton('Рандом 🔀')
woman = KeyboardButton('Найти ♀️')
vip = KeyboardButton('Вип 👑')
rules = KeyboardButton('Правила 📖')
profile = KeyboardButton('Профиль 👤')
main_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(man, random, woman).row(vip, rules, profile)

name = InlineKeyboardButton('🅰️ Имя', callback_data='name')
age = InlineKeyboardButton('🔞 Возраст', callback_data='age')
sex = InlineKeyboardButton('👫 Пол', callback_data='sex')
country = InlineKeyboardButton('🌍 Страна', callback_data='country')
city = InlineKeyboardButton('🏙️ Город', callback_data='city')
# op_sex = InlineKeyboardButton('🚺 Пол собеседника 🚹', callback_data='op_sex')
settings_kb = InlineKeyboardMarkup(
    resize_keyboard=True).add(name).add(age).add(sex).add(country).add(city)

change_profile = KeyboardButton('⚙️ Изменить профиль')
statistic = KeyboardButton('📈 Статистика')
ref = KeyboardButton('💼 Рефералка')
profile_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(change_profile).add(
    statistic).add(ref).add(to_main)

vip_kb = ReplyKeyboardMarkup(resize_keyboard=True).add('🆓 Получить вип бесплатно').add(
    '💰 Купить/Продлить вип').add(to_main)

day = KeyboardButton('👑 Вип на день - 20₽')
week = KeyboardButton('👑 Вип на неделю - 100₽')
month = KeyboardButton('👑 Вип на месяц - 300₽')
buy_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(day).add(week).add(month).add(to_main)

to_main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(to_main)

male = InlineKeyboardButton('Мужской ♂️', callback_data='male')
female = InlineKeyboardButton('Женский ♀️', callback_data='female')
sex_kb = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(male, female)

on = KeyboardButton('Включить уведомления 🔔')
off = KeyboardButton('Выключить уведомления 🔕')
on_kb = ReplyKeyboardMarkup(resize_keyboard=True).add('Обменять 💎').add(on).add(to_main)
off_kb = ReplyKeyboardMarkup(resize_keyboard=True).add('Обменять 💎').add(off).add(to_main)

top = KeyboardButton('🏆 Рейтинги')
statistic_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(top).add(to_main)

top_messages = KeyboardButton('🔝 Топ 5 по сообщениям')
top_likes = KeyboardButton('🔝 Топ 5 по лайкам')
top_refs = KeyboardButton('🔝 Топ 5 по рефам')
top_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(top_messages).add(top_likes).add(top_refs).add(to_main)
