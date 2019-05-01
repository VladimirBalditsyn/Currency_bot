# -*- coding: utf-8 -*-
import telebot
from peewee import IntegerField, FloatField, CharField, PostgresqlDatabase, \
    MySQLDatabase, Model, DateField, PrimaryKeyField

# db = PostgresqlDatabase(
#     'currency_transactions',
#     user='postgres',
#     password='postgres',
#     host='localhost')


# db = MySQLDatabase(
#     'name_of_your_db',
#     user='your_user_name',
#     password='your_password',
#     host='localhost'
# )


class People(Model):
    id = IntegerField()
    name = CharField()
    surname = CharField()
    age = IntegerField()

    class Meta:
        database = db


class Currency(Model):
    cur_code = CharField(primary_key=True)
    name = CharField()
    rate = FloatField()
    day = DateField()

    class Meta:
        database = db


class Transaction(Model):
    pk = PrimaryKeyField()
    id = IntegerField()
    currency_from = CharField()
    currency_to = CharField()
    input_amount = FloatField()
    output_amount = FloatField()
    transaction_data = DateField()

    class Meta:
        database = db


bot = None


People.create_table()
Currency.create_table()
Transaction.create_table()


def init_bot(token):
    global bot
    # telebot.apihelper.proxy = {'https': 'http://104.248.108.33:8080'}
    bot = telebot.TeleBot(token)

    from app import handlers
