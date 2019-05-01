from app import *
import requests
import math
import datetime
import xml.etree.ElementTree as ET
import locale
import re


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Я - валютный бот. Помогу с '
                                      'курсом и переводами')
    bot.send_message(message.chat.id, 'Для начала, нужно зарегестрироваться,'
                                      ' чтобы я мог сохранять историю твоих '
                                      'запросов.\nНапиши /reg')


@bot.message_handler(commands=['update_rate'])
def handle_currency_message(message):
    if update_rate():
        bot.send_message(message.chat.id, 'Курс валют обновлён')
    else:
        bot.send_message(message.chat.id, 'Я валяюсь...')


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, '/reg - регистрация (если ты еще не '
                                      'с нами)\n/codes - узнать коды '
                                      'валют\n/update_rates - обновить курс '
                                      '(если мне не доверяешь)\n'
                                      '\nТы можешь попросить меня:\nУзнать '
                                      'курс /rate\nКонвертировать в рубли '
                                      '/to_rubles\nКонвертировать из рублей '
                                      '/from_rubles\nИстория за период '
                                      '/old_transactions')


@bot.message_handler(commands=['codes'])
def handle_codes(message):
    update_rate()
    output = ''
    for currency in Currency.select():
        output += '{} - {}\n'.format(currency.name, currency.cur_code)
    bot.send_message(message.chat.id, output)


@bot.message_handler(commands=['reg'])
def handle_reg(message):
    bot.send_message(message.chat.id, "Как тебя зовут?")
    bot.register_next_step_handler(message, get_name)


@bot.message_handler(commands=['to_rubles'])
def handle_to_rubles(message):
    bot.send_message(message.chat.id, "Какая валюта интересует?\nВведи сумму и"
                                      " через пробел код валюты\nПодсказка: "
                                      "узнать коды валют  можно при помощи "
                                      "команды /codes")
    bot.register_next_step_handler(message, convert)


@bot.message_handler(commands=['from_rubles'])
def handle_from_rubles(message):
    bot.send_message(message.chat.id, "Какая валюта интересует?\nВведи код  "
                                      "валюты и сумму через пробел "
                                      "\nПодсказка: "
                                      "узнать коды валют  можно при помощи "
                                      "команды /codes")
    bot.register_next_step_handler(message, convert)


@bot.message_handler(commands=['rate'])
def handle_rate(message):
    bot.send_message(message.chat.id, "Какая валюта интересует?\nВведи код "
                                      "валюты, или, если не знаешь код, "
                                      "введи название")
    bot.register_next_step_handler(message, get_rate)


@bot.message_handler(commands=['old_transactions'])
def handle_rate(message):
    bot.send_message(message.chat.id, "Какая период интересует?\nВведи "
                                      "диапазон дат в формате  \"YYYY-MM-DD "
                                      ": YYYY-MM-DD\"\nПримечание: период "
                                      "должен быть корректен, иначе ничего "
                                      "не найду")
    bot.register_next_step_handler(message, get_old_transactions)


# Handles all text messages that match the regular expression
@bot.message_handler(content_types=['text'], regexp="python")
def handle_python_message(message):
    bot.send_message(message.chat.id, "Я обожаю python!")


@bot.message_handler(content_types=['text'], regexp="Конвертировать в рубли")
def handle_python_message(message):
    bot.send_message(message.chat.id, "Какая валюта интересует?\nВведи сумму и"
                                      " через пробел код валюты\nПодсказка: "
                                      "узнать коды валют  можно при помощи "
                                      "команды /codes")
    bot.register_next_step_handler(message, convert)


@bot.message_handler(content_types=['text'], regexp="История за период")
def handle_python_message(message):
    bot.send_message(message.chat.id, "Какая период интересует?\nВведи "
                                      "диапазон дат в формате  \"YYYY-MM-DD "
                                      ": YYYY-MM-DD\"\nПримечание: период "
                                      "должен быть корректен, иначе ничего "
                                      "не найду")
    bot.register_next_step_handler(message, get_old_transactions)


@bot.message_handler(content_types=['text'], regexp="Конвертировать из рублей")
def handle_python_message(message):
    bot.send_message(message.chat.id, "Какая валюта интересует?\nВведи код  "
                                      "валюты и сумму через пробел "
                                      "\nПодсказка: "
                                      "узнать коды валют  можно при помощи "
                                      "команды /codes")
    bot.register_next_step_handler(message, convert)


@bot.message_handler(content_types=['text'], regexp="Узнать курс")
def handle_python_message(message):
    bot.send_message(message.chat.id, "Какая валюта интересует?\nВведи код "
                                      "валюты, или, если не знаешь код, "
                                      "введи название")
    bot.register_next_step_handler(message, get_rate)


@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    bot.send_message(message.chat.id, 'Я тут вообще-то делом занят')


def get_old_transactions(message):
    if message.text is None:
        bot.send_message(message.chat.id, 'Я все вижу и читаю)\nТекст, '
                                          'пожалуйста')
        bot.register_next_step_handler(message, get_rate)

    message_input = message.text.split(' : ')
    if len(message_input) != 2:
        bot.send_message(message.chat.id, 'Ты промахнулся с '
                                          'вводом\nИспользуй формат выше')
        bot.register_next_step_handler(message, get_old_transactions)
        return

    start_date = datetime.datetime.now()
    end_date = datetime.datetime.now()

    try:
        start_date = datetime.datetime.strptime(message_input[0],
                                                '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(message_input[1],
                                              '%Y-%m-%d').date()
    except:
        bot.send_message(message.chat.id, 'Введи корректную дату, пожалуйста')
        bot.register_next_step_handler(message, get_rate)
        return

    output_print = ''
    output = Transaction.select().where(
        (Transaction.id == message.chat.id)
        & (Transaction.transaction_data >= start_date)
        & (Transaction.transaction_data <= end_date))

    if not output.exists():
        bot.send_message(message.chat.id, 'Ничего нет')
    else:
        for out in output:
            output_print += '{} {} было {} {}\n'.format(out.input_amount,
                                                      out.currency_from,
                                                      out.output_amount,
                                                      out.currency_to)
        bot.send_message(message.chat.id, output_print)

    bot.send_message(message.chat.id, 'Что ещё угодно?')


def convert(message):
    update_rate()
    if message.text is None:
        bot.send_message(message.chat.id, 'Я все вижу и читаю)\nТекст, '
                                          'пожалуйста')
        bot.register_next_step_handler(message, get_rate)

    message_input = message.text.split(' ')
    value = 0.0
    flag = True  #в рубли
    if len(message_input) != 2:
        if message_input[0] == '/codes':
            handle_codes(message)
            bot.register_next_step_handler(message, convert)
            return
        else:
            bot.send_message(message.chat.id, 'Ты промахнулся с '
                                              'вводом\nИспользуй формат выше')
            bot.register_next_step_handler(message, convert)
            return
    try:
        buffer = message_input[0].split(',')
        value_txt = '.'.join(buffer)
        value = locale.atof(value_txt)
    except (TypeError, ValueError):
        try:
            buffer = message_input[1].split(',')
            value_txt = '.'.join(buffer)
            value = locale.atof(value_txt)
            flag = False
            message_input = message_input[::-1]
        except (TypeError, ValueError):
            bot.send_message(message.chat.id, 'Ты промахнулся с '
                                              'вводом\nИспользуй формат выше')
            bot.register_next_step_handler(message, convert)

    cur_rate = Currency.select().where(Currency.cur_code == message_input[
        1].upper())
    if not cur_rate.exists():
        bot.send_message(message.chat.id, 'Не знаю такую валюту\nПопробуй ещё')
        bot.register_next_step_handler(message, convert)
    else:
        if flag:
            result_value = value * cur_rate[0].rate
            result_value = round(result_value, 4)
            bot.send_message(message.chat.id, '{} RUB'.format(result_value))
            result = Transaction.create(id=message.chat.id,
                                        currency_from=cur_rate[0].cur_code,
                                        currency_to='RUB', input_amount=value,
                                        output_amount=result_value,
                                        transaction_data=datetime.datetime.now(
                                            ).date())
            result.save()
        else:
            result_value = value / cur_rate[0].rate
            result_value = round(result_value, 4)
            bot.send_message(message.chat.id, '{} {}'.format(result_value,
                                                             'RUB'))
            result = Transaction.create(id=message.chat.id,
                                        currency_from='RUB',
                                        currency_to=cur_rate[0].cur_code,
                                        input_amount=value,
                                        output_amount=result_value,
                                        transaction_data=datetime.datetime.now(
                                        ).date())
        bot.send_message(message.chat.id, 'Что ещё угодно?')


def get_rate(message):
    update_rate()
    if message.text is None:
        bot.send_message(message.chat.id, 'Я все вижу )\nТекст, пожалуйста')
        bot.register_next_step_handler(message, get_rate)
    elif len(message.text) == 3:
        result = Currency.select().where(Currency.cur_code ==
                                         message.text.upper())
        if result.exists():
            output = 'Сегодня {} {} руб'.format(result[0].name, result[0].rate)
            bot.send_message(message.chat.id, output)
            bot.send_message(message.chat.id, 'Что ещё угодно?')
        else:
            bot.send_message(message.chat.id, 'Я не знаю такую '
                                              'валюту\nПопробуй ещё')
            bot.register_next_step_handler(message, get_rate)
    elif len(message.text) >= 3:
        if message.text == '/codes':
            handle_codes(message)
            bot.register_next_step_handler(message, get_rate)
            return
        result = Currency.select().where(Currency.name ==
                                         message.text)
        if result.exists():
            output = 'Сегодня {} {} руб'.format(result[0].name, result[0].rate)
            bot.send_message(message.chat.id, output)
            bot.send_message(message.chat.id, 'Что ещё угодно?')
        else:
            bot.send_message(message.chat.id, 'Я не знаю такую '
                                              'валюту (названия пиши '
                                              'грамотно, иначе ничего не '
                                              'скажу)'
                                              '\nПопробуй ещё')
            bot.register_next_step_handler(message, get_rate)
    else:
        bot.send_message(message.chat.id, 'Поприкалываться сюда '
                                          'пришёл?\nМеня не '
                                          'обманешь\nПопробуй ещё')
        bot.register_next_step_handler(message, get_rate)


def update_rate():
    current_date = datetime.datetime.now()
    is_valid = Currency.select().where(Currency.day == current_date.date())
    if is_valid.exists():
        return True
    try:
        # Выполняем запрос к API.
        get_xml = requests.get(
            'http://www.cbr.ru/scripts/XML_daily.asp?date_req={}'.format(
                current_date.strftime('%d/%m/%Y')))
        content = get_xml.content
        # Парсинг XML используя ElementTree
        currency_list = ET.fromstring(content)

        for currency in currency_list.getiterator('Valute'):
            code = currency.find('CharCode').text
            name = currency.find('Name').text
            value_txt = currency.find('Value').text
            buffer = value_txt.split(',')
            value_txt = '.'.join(buffer)
            value = locale.atof(value_txt)
            old_val = Currency.select().where(Currency.cur_code == code)
            if old_val.exists():
                old_val = old_val.get()
                old_val.delete_instance()
            val = Currency.create(cur_code=code, name=name, rate=value,
                                  day=current_date.date())
            val.save()
        return True
    except:
        return False


def get_name(message):
    person_select = People.select().where(People.id == message.chat.id)
    if person_select.exists():
        for person in person_select:
            person.delete_instance()
    if message.text is not None:
        you_name = str(message.text)
        you = People.create(id=message.chat.id, name=you_name, surname='',
                            age=0)
        you.save()
        bot.send_message(message.chat.id, 'Какая у тебя фамилия?')
        bot.register_next_step_handler(message, get_surname)
    else:
        bot.send_message(message.chat.id, 'Ты хочешь, чтобы меня '
                                          'кокнуло?\nЯ жду текст')
        bot.register_next_step_handler(message, get_name)


def get_surname(message):
    you = People.get(People.id == message.chat.id)
    if message.text is not None:
        you.surname = str(message.text)
        you.save()
        bot.send_message(message.chat.id, 'Сколько тебе лет?')
        bot.register_next_step_handler(message, get_age)
    else:
        bot.send_message(message.chat.id, 'Несмешная шутка\nТекст, пожалуйста')
        bot.register_next_step_handler(message, get_surname)


def get_age(message):
    you = People.get(People.id == message.chat.id)
    try:
        age = int(message.text)  # проверяем, что возраст введен корректно
        if age < 0 or age > 150:
            bot.send_message(message.chat.id, 'Шутки шутишь\nПопробуем ещё')
            bot.register_next_step_handler(message, get_age)
            return
        you.age = age
        you.save()
    except (TypeError, ValueError):
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(message, get_age)
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()  # наша клавиатура
        # кнопка «Да»
        key_yes = telebot.types.InlineKeyboardButton( text='Да',
                                                      callback_data='yes')
        keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
        key_no = telebot.types.InlineKeyboardButton(text='Нет',
                                                    callback_data='no')
        keyboard.add(key_no)
        you = People.select().where(People.id == message.chat.id).get()
        question = 'Тебе {age} лет, тебя зовут {name} {surname}?'.format(
            age=you.age, name=you.name, surname=you.surname)
        bot.send_message(message.chat.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  # call.data это callback_data,
        # которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'Запомню : )\nНапиши /help, '
                                               'чтобы узнать все мои '
                                               'возможности')
    elif call.data == "no":
        acc = People.select().where(People.id == call.message.chat.id)
        if acc.exists():
            acc = acc.get()
            acc.delete_instance()
        bot.send_message(call.message.chat.id, "Попробуем начать сначала.  "
                                               "Как тебя зовут?")
        bot.register_next_step_handler(call.message, get_name)
