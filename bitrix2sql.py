import asyncio
import sqlite3

import pandas as pd
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import add_bitrix_to_sql
from fastbitrix_funcs import get_deals


def refresh_db():
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


