import asyncio

import pandas as pd
import sqlite3

import streamlit

import lexicon
from config import db
from lexicon import lexicon_dict


def render_default_dataframe(db, main, columns_list, b2b=False):
    with sqlite3.connect(db) as con:
        if not b2b:
            sql_query = pd.read_sql(f'SELECT * FROM {main} where marketplace != "b2b"',
                                    con,
                                    parse_dates=['date'])
        elif b2b:
            sql_query = pd.read_sql(f'SELECT * FROM {main} where marketplace == "b2b"',
                                    con,
                                    parse_dates=['date'])

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
            elif users == 'office':
                return list(df.query('role != "pending" & location == "Офис"')['user_id'])
            elif users == 'pending':
                return list(df.query('role == "pending"')['user_id'])
            elif users == 'warehouse':
                return list(df.query('role != "pending" & location == "Склад"')['user_id'])

        else:
            if users == 'all':
                return df['user_id']
            elif users == 'office':
                return df.query('role != "pending" & location == "Офис"')['user_id']
            elif users == 'pending':
                return df.query('role == "pending"')
            elif users == 'warehouse':
                return df.query('role != "pending" & location == "Склад"')['user_id']

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

def change_worker(order_id, worker):
    try:
        with sqlite3.connect('greenea_issues.db') as con:
            cursor = con.cursor()
            cursor.execute(f'UPDATE main SET worker = "{worker}" WHERE bitrix_id = {order_id}')
            return
    except Exception as error:
        print(error)

def change_date(order_id, date):
    try:
        date = str(date)[0:-9]
        with sqlite3.connect('greenea_issues.db') as con:
            cursor = con.cursor()
            cursor.execute(f'UPDATE main SET date = "{date}" WHERE bitrix_id = {order_id}')
            return
    except:
        print(date[0:-9])


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


def get_years(initial_year=2022, reverse=False):
    df = render_default_dataframe(db, 'main', lexicon.columns_list)
    min = initial_year
    max = df['date'].max().year

    result = list(range(min, max + 1))
    result.sort(reverse=reverse)

    return result


def get_months(year, initial_month=1, day_selector=False, shift=True):
    df = render_default_dataframe(db, 'main', lexicon.columns_list)
    month_df = df[df['date'].dt.year == year]
    min_month = initial_month
    max_month = month_df['date'].max().month

    if year == 2022:
        return [12]

    if day_selector:
        return list(range(min_month, max_month + 1))

    else:
        if min_month == max_month:
            return list(range(min_month, max_month + 1 + shift))
        else:
            return list(range(min_month, max_month + 1))


def get_quar(year):
    df = render_default_dataframe(db, 'main', lexicon.columns_list)
    month_df = df[df['date'].dt.year == year]
    month_df['month'] = month_df['date'].dt.month

    min_month = month_df['month'].min()
    max_month = month_df['month'].max()

    quarters = []
    for month in range(min_month, max_month+1):
        quarter = (month - 1) // 3 + 1
        if quarter not in quarters:
            quarters.append(quarter)

    return (quarters)


def render_period_pivot(start='2023-04-01', end='2023-05-01', period='day', b2b=False):
    df = render_default_dataframe(db, 'main', lexicon.columns_list, b2b=b2b)
    df['type'] = df['type'].apply(lambda x: lexicon.lexicon_dict[x])
    df['marketplace'] = df['marketplace'].apply(lambda x: lexicon.lexicon_dict[x])
    df.rename(columns={'type': 'Тип проблемы',
                       'date': 'Дата',
                       'marketplace': 'Маркетплейс',
                       'sku_number': 'Артикул',
                       'comment': 'Комментарий'}, inplace=True)

    problems = df['Тип проблемы'].unique()
    markets = df['Маркетплейс'].unique()

    mask = (df['Дата'] >= start) & (df['Дата'] < end)

    df = df.loc[mask]

    match period:

        case 'day':
            frequency = 'D'
        case 'week':
            frequency = 'W'
        case 'month':
            frequency = 'M'

    period = pd.DataFrame(pd.date_range(start=start, end=end, freq=frequency))
    period = period.rename(columns={0: 'Дата'})

    for problem in problems:
        defect_df = df[df['Тип проблемы'] == problem]
        defect_df = defect_df.groupby(pd.Grouper(key='Дата', freq=frequency)).agg({'Артикул': 'size'})
        defect_df = defect_df.rename(columns={'Артикул': problem})

        period = period.merge(defect_df, on='Дата', how='outer')

    for market in markets:
        market_df = df[df['Маркетплейс'] == market]
        market_df = market_df.groupby(pd.Grouper(key='Дата', freq=frequency)).agg({'Артикул': 'size'})
        market_df = market_df.rename(columns={'Артикул': market})

        period = period.merge(market_df, on='Дата', how='outer')
        period = period.fillna(0)

    return period
