import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from random import *

API_TOKEN = 'Enter your API here'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

class Game:
    def __init__(self):
        self.isIngame = False
        self.cache = []
IDs = {}

bottom_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
upper_alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
ex = 'ъыь'

def universal(s):
    new = ''
    for e in s:
        if e != '-' and e != ' ':
            if e in upper_alphabet:
                new += bottom_alphabet[upper_alphabet.find(e)]
            elif e == 'ё':
                new += 'е'
            else:
                new += e
    return new


def wordforms(x):
    if 10 < x % 100 < 15:
        return ' наименований'
    elif x % 10 == 1:
        return ' наименование'
    elif 1 < x % 10 < 5:
        return ' наименования'
    else:
        return ' наименований'


with open('cities.json', encoding='utf-8') as f:
    data = json.load(f)
    cities = data['cities']
    rightNames = data['rightNames']
    '''for e in f:
        univ = universal(e[:-1])
        cities[univ[0]].append(univ)
        rightNames[univ] = e[:-1]'''


newgame_button = InlineKeyboardMarkup()
newgame_button.add(types.InlineKeyboardButton(text='Новая игра', callback_data='newgame'))

gu = [[types.KeyboardButton(text='/giveup')]]
giveup_button = types.ReplyKeyboardMarkup(keyboard=gu)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    print(123)
    IDs[message.from_user.id] = Game()
    await message.answer('Привет, я города-бот. Нажмите кнопку ниже чтобы начать', reply_markup=newgame_button)


@dp.callback_query_handler(text='newgame')
async def newgame(call: types.CallbackQuery):
    IDs[call.from_user.id].isIngame = True

    firstmove_button = InlineKeyboardMarkup()
    firstmove_button.add(types.InlineKeyboardButton(text='Уступить первый ход', callback_data='firstmove'))

    await call.message.answer("/giveup чтобы сдаться", reply_markup=giveup_button)
    await call.message.answer("Введите название города.", reply_markup=firstmove_button)


@dp.callback_query_handler(text='firstmove')
async def firstmove(call: types.CallbackQuery):
    if not IDs[call.from_user.id].isIngame or IDs[call.from_user.id].cache:
        return
    bot_city = choice(list(rightNames.keys()))
    IDs[call.from_user.id].cache.append(bot_city)
    await call.message.answer(rightNames[bot_city])


@dp.message_handler(commands=['сдаться', 'Сдаться', 'giveup'])
async def giveup(message: types.Message):
    if not IDs[message.from_user.id].isIngame:
        return
    IDs[message.from_user.id].isIngame = False

    citiesCount = len(IDs[message.from_user.id].cache) // 2
    await message.answer('Вы проиграли', reply_markup=ReplyKeyboardRemove())
    await message.answer('В этот раз вы вспомнили ' + str(citiesCount) + wordforms(citiesCount), reply_markup=newgame_button)
    IDs[message.from_user.id].cache = []


@dp.message_handler()
async def answer(message: types.Message):
    if not IDs[message.from_user.id].isIngame:
        return
    if IDs[message.from_user.id].cache:
        bot_city = IDs[message.from_user.id].cache[-1]
    print(message.from_user.id, IDs[message.from_user.id].cache)
    user_city = universal(str(message.text))
    print(message.from_user.id, user_city)
    if user_city not in rightNames.keys():
        await message.reply('Это не город')
    elif IDs[message.from_user.id].cache and not (bot_city[-1] == user_city[0] or (bot_city[-1] in ex and bot_city[-2] == user_city[0])):
        await message.reply('Не та буква')
    elif user_city in IDs[message.from_user.id].cache:
        await message.reply('Этот город уже был')
    else:
        IDs[message.from_user.id].cache.append(user_city)
        if user_city[-1] in ex:
            lastletter = user_city[-2]
        else:
            lastletter = user_city[-1]
        city_index = randint(0, len(cities[lastletter]) - 1)
        while cities[lastletter][city_index] in IDs[message.from_user.id].cache and city_index != -(len(cities[lastletter]) + 1):
            city_index -= 1
            if city_index == -(len(cities[lastletter]) + 1):
                break
        if city_index == -(len(cities[lastletter]) + 1):
            citiesCount = len(IDs[message.from_user.id].cache) // 2
            await message.answer('Вы проиграли. В этот раз вы вспомнили ' + str(citiesCount) + wordforms(citiesCount), reply_markup=newgame_button)
            IDs[message.from_user.id].cache = []
            IDs[message.from_user.id].isIngame = False
            return
        bot_city = cities[lastletter][city_index]
        await message.reply(rightNames[bot_city])
        print(bot_city)
        IDs[message.from_user.id].cache.append(bot_city)



if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)


