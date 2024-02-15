import asyncio
import sqlite3

import pandas as pd
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import db, task_db
from db import add_bitrix_to_sql
from fastbitrix_funcs import get_deals


def refresh_db(db=task_db):
    update_dict = {}
    orders = asyncio.run(get_deals())

    for key, value in orders.items():
        order_number = key
        order_id = value['ID Заказа']
        status = value['Статус заказа']
        dims = value['Габариты']
        present_id = add_bitrix_to_sql(order_id, order_number, status, dims)
        if present_id:
            update_dict[present_id[0]] = present_id[1]

    return update_dict




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
