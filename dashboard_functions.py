import asyncio

import streamlit as st
import pandas as pd
import sqlite3


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


async def add_pending_user(db, username, user_id, table='users', role='pending'):
    with sqlite3.connect(db) as con:
        cursor = con.cursor()
        cursor.execute(f'INSERT INTO {table} VALUES ("{username}", "{user_id}", "{role}")')
        cursor.fetchall()
        asyncio.sleep(0.1)


def change_role(user_id, role, db='greenea_issues.db'):
    with sqlite3.connect(db) as con:
        cursor = con.cursor()
        cursor.execute(f'UPDATE users SET role = "{role}" WHERE user_id = {user_id}')
        return
