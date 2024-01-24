import asyncio

import pandas as pd
import sqlite3

import streamlit

import lexicon
from config import db
from lexicon import lexicon_dict


def render_default_dataframe(db, main, columns_list):
    with sqlite3.connect(db) as con:
        sql_query = pd.read_sql(f'SELECT * FROM {main}', con, parse_dates=['date'])

        df = pd.DataFrame(sql_query, columns=columns_list)

        return df


def render_users(db, table, columns_list, list_mode=True, users='all'):
    with sqlite3.connect(db) as con:
        sql_query = pd.read_sql(f'SELECT * FROM {table}', con, parse_dates=['date'])

        df = pd.DataFrame(sql_query, columns=columns_list)

        if list_mode:
            if users == 'all':
                return list(df['user_id'])
            elif users == 'authed':
                return list(df.query('role != "pending"')['user_id'])
            elif users == 'pending':
                return list(df.query('role == "pending"')['user_id'])
        else:
            if users == 'all':
                return df['user_id']
            elif users == 'authed':
                return df.query('role != "pending"')
            elif users == 'pending':
                return df.query('role == "pending"')

        return df

def simple_render_user(db, table, columns_list, list_mode=True, users='all'):
    with sqlite3.connect(db) as con:
        sql_query = pd.read_sql(f'SELECT * FROM {table}', con, parse_dates=['date'])

        df = pd.DataFrame(sql_query, columns=columns_list)
        return df


async def add_pending_user(db, username, user_id, table='users', role='pending', location='Офис'):
    with sqlite3.connect(db) as con:
        cursor = con.cursor()
        cursor.execute(f'INSERT INTO {table} VALUES ("{username}", "{user_id}", "{role}", "{location}")')
        cursor.fetchall()
        asyncio.sleep(0.1)


def change_role(user_id, role, db='greenea_issues.db'):
    with sqlite3.connect(db) as con:
        cursor = con.cursor()
        cursor.execute(f'UPDATE users SET role = "{role}" WHERE user_id = {user_id}')
        return

def change_loc(user_id, location, db='greenea_issues.db'):
    with sqlite3.connect(db) as con:
        cursor = con.cursor()
        cursor.execute(f'UPDATE users SET location = "{location}" WHERE user_id = {user_id}')
        return

def render_sku_table(df: pd.DataFrame, group: list):
    list_of_markets = set(df['marketplace'])
    result = pd.DataFrame()
    for market in list_of_markets:
        temp = df.query('sku_number == @group & marketplace == @market')
        temp = temp.groupby(by=['sku_number']).agg({'marketplace': 'size'}).reset_index()
        temp = temp.rename(columns={'marketplace': market})
        if len(result) == 0:
            result = temp
        else:
            result = result.merge(temp, on='sku_number', how='outer')

    result = result.rename(columns=lambda x: lexicon_dict[x])
    result = result.fillna(0).set_index('Артикул')
    return result

def color_marketplace(value):
    if value == 'Wildberries':
        color = 'rgba(138, 43, 226,.2)'
    elif value == 'Озон':
        color = 'rgba(0, 0, 255,.2)'
    elif value == 'Яндекс.Маркет':
        color = 'rgba(255, 255, 0,.2)'
    return f'background-color: {color}; opacity: 0.1'

def get_monthes(year):
    df = render_default_dataframe(db, 'main', lexicon.columns_list)
    month_df = df[df['date'].dt.year == year]
    min_month = month_df['date'].min().month
    max_month = month_df['date'].max().month
    return list(range(min_month, max_month+1))

