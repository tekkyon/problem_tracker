import sqlite3

import pandas as pd
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bitrix24_funcs import init_1c_orders
from config import db
from db import add_bitrix_to_sql

def refresh_db(db=db):
    orders = init_1c_orders()

    with sqlite3.connect(db) as db:
        query = """
        DELETE FROM bitrix_buffer"""
    db.execute(query)
    db.commit()

    for key, value in orders.items():
        order_number = key
        order_id = value['ID Заказа']
        status = value['Статус заказа']
        dims = value['Габариты']
        add_bitrix_to_sql(order_id, order_number, status, dims)
    return True


def create_orders_kb(width: int,
                     **kwargs: str):
    kb_builder = InlineKeyboardMarkup()
    buttons = []

    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()

def init_keyboard_dct(db, limit=5):
    result_dct = {}
    with sqlite3.connect(db) as con:
        sql_query = pd.read_sql(f'SELECT * FROM bitrix_buffer', con)

        df = pd.DataFrame(sql_query, columns=['order_id', 'order_number_1c'])

    counter = 0
    for index, value in df.iterrows():
        if counter < limit:
            new_key = f'{str(value["order_id"])}_{value["order_number_1c"]}'
            result_dct[new_key] = value['order_number_1c']
            counter += 1
        else:
            break

    return result_dct
