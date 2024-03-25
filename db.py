import asyncio
import sqlite3
import pandas as pd
from datetime import date, datetime
import streamlit as st

from config import db, task_db
from fastbitrix_funcs import get_current_status

from st_supabase_connection import SupabaseConnection

st_supabase_client = st.connection(
    name="LOLKEK",
    type=SupabaseConnection,
    ttl=None,
    url="https://tplqoibzznwgucyvkqes.supabase.co",
    key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwbHFvaWJ6em53Z3VjeXZrcWVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxMDE2MzgxMywiZXhwIjoyMDI1NzM5ODEzfQ.EdJS3-lQByc9yt6RykEJTHKhKBldqJZmR9DlkU8u1vM"
)


# def insert_db(db, sku, sku_number, marketplace, date_str, type_of_problem, comment, type_of_mp,
#               manager_id, worker, bitrix_id=''):
#     with sqlite3.connect(db) as db:
#         date_str = date_str.split('/')
#         today = date.today()
#
#         new_date = f'{date_str[0]}-{date_str[1]}-{date_str[2]}'
#         query = f"""
#         INSERT INTO main
#         VALUES
#         ('{sku}',
#          '{sku_number}',
#           '{marketplace}',
#            '{new_date}',
#             '{type_of_problem}',
#              '{comment}',
#               '{type_of_mp}',
#               '{today}',
#               '{manager_id}',
#               '{worker}',
#               '{bitrix_id}')
#         """
#
#         db.execute(query)
#         db.commit()

def insert_db(sku, sku_number, marketplace, date_str, type_of_problem, comment, type_of_mp,
              manager_id, worker, bitrix_id=''):
    date_str = date_str.split('/')
    today = date.today()

    new_date = f'{date_str[0]}-{date_str[1]}-{date_str[2]}'

    st_supabase_client.table("main").insert(
        [{'sku': str(sku),
          'sku_number': str(sku_number),
          'marketplace': str(marketplace),
          'date': str(new_date),
          'type': str(type_of_problem),
          'comment': str(comment),
          'marketplace_type': str(type_of_mp),
          'creation_date': str(today),
          'manager': str(manager_id),
          'worker': str(worker),
          'bitrix_id': str(bitrix_id)}],
        count="None"
    ).execute()


# def add_user(db, username, user_id, role='manager', table='users', loc='not_defined'):
#     with sqlite3.connect(db) as db:
#         query = f"""
#         INSERT INTO {table}
#         VALUES
#         ('{username}', '{user_id}', '{role}', '{loc}')
#         """
#
#     db.execute(query)
#     db.commit()

# def add_user(username, user_id, role='manager', loc='not_defined'):
#     st_supabase_client.table("users").insert(
#         [{'username': username,
#           'user_id': user_id,
#           'role': role,
#           'location': loc, }],
#         count="None"
#     ).execute()


# def read_users(db, table='users'):
#     response = st_supabase_client.query("*", table="main", ttl=0).execute().data
#     with sqlite3.connect(db) as db:
#         query = f"""
#         SELECT * FROM {table}
#         """
#     df = pd.read_sql_query(query, db)
#     return df


def get_name_by_id(db, tel_id):
    with sqlite3.connect(db) as db:
        query = f"""
        SELECT * FROM users
        WHERE user_id = '{tel_id}'
        """
    df = pd.read_sql_query(query, db)
    return df


# def add_lexicon(db, key, value):
#     with sqlite3.connect(db) as db:
#         query = f"""
#         INSERT INTO lexicon
#         VALUES
#         ('{key}', '{value}')
#         """
#
#     db.execute(query)
#     db.commit()

# def check_uniq_id(order_id, task_db=task_db):
#     with sqlite3.connect(task_db) as con:
#         query = f"""
#         SELECT *
#         FROM orders
#         WHERE order_id = '{order_id}'
#         """
#         cursor = con.cursor()
#         cursor.execute(query)
#         if len(cursor.fetchall()) > 0:
#             return False
#         else:
#             return True

def check_uniq_id(order_id):
    response = st_supabase_client.query("*", table="orders", ttl=0).eq('order_id', order_id).execute().data
    return len(response)


# def add_bitrix_to_sql(order_id, order_number, status, dims, executor='default', task_db=task_db):
#
#     if check_uniq_id(order_id):
#         default_date = ''
#         with sqlite3.connect(task_db) as db:
#             query = f"""
#             INSERT INTO orders
#             VALUES
#             ('{order_id}',
#              '{order_number}',
#               '{status}',
#                '{dims}',
#                 '{executor}',
#                  '{default_date}',
#                   '{default_date}')
#             """
#
#         db.execute(query)
#         db.commit()
#     else:
#         with sqlite3.connect(task_db) as db:
#             query = f"""
#             UPDATE orders
#             SET dims = '{dims}', status = '{status}'
#             WHERE order_id = '{order_id}'
#             """
#         return [order_id, status]


def add_bitrix_to_sql(order_id, order_number, status, dims, executor='default', task_db=task_db):
    if check_uniq_id(order_id):
        st_supabase_client.table("orders").insert(
            [{'order_id': order_id,
              'order_number_1c': order_number,
              'status': status,
              'dims': dims,
              'executor': executor,
              'datetime_start': '',
              'datetime_finish': '',}],
            count="None"
        ).execute()
    else:
        st_supabase_client.table("orders").update(
            [{'dims': dims,
              'status': status}]
        ).eq('order_id', order_id).execute()

        return [order_id, status]


# def update_sql_dim(order_id, dims, executor, task_db=task_db):
#     now = datetime.now()
#     with sqlite3.connect(task_db) as db:
#         query = f"""
#         UPDATE orders
#         SET dims='{dims}', executor='{executor}', datetime_finish='{now}', status='Готов к отгрузке(собран)'
#         WHERE order_id='{order_id}'
#         """
#
#     db.execute(query)
#     db.commit()

def update_sql_dim(order_id, dims, executor):
    now = datetime.now()
    st_supabase_client.table("orders").update(
        [{'dims': dims,
          'executor': executor,
          'datetime_finish': now,
          'status': 'Готов к отгрузке(собран)'}]
    ).eq('order_id', order_id).execute()


def read_lexicon(db=db):
    with sqlite3.connect(db) as db:
        query = f"""
        SELECT * FROM lexicon
        """
        df = pd.read_sql_query(query, db)
        return df



def update_lexicon(old_value, new_value, color, db=db):
    with sqlite3.connect(db) as db:
        query = f"""
        UPDATE lexicon
        SET value='{new_value}', color='{color}'
        WHERE value='{old_value}'
        """

    db.execute(query)
    db.commit()


def add_lexicon(new_value, color, db=db, pos=6, purpose='marketplace'):
    with sqlite3.connect(db) as db:
        query = f"""
        INSERT INTO lexicon
        VALUES ('btn_6', '{new_value}', '{purpose}', '{color}');
        """
    db.execute(query)
    db.commit()


def add_new_worker(worker_id: int, firstname: str, lastname: str, position: str, db=task_db):
    with sqlite3.connect(db) as db:
        query = f"""
        INSERT INTO workers
        VALUES ('{worker_id}', '{firstname}', '{lastname}', '{position}');
        """
    db.execute(query)
    db.commit()


def get_list_of_workers(db=task_db):
    with sqlite3.connect(db) as db:
        query = f"""
        SELECT lastname, firstname, worker_id
        FROM workers
        """
    df = pd.read_sql_query(query, db)
    return df


def update_status(new_status_dict: dict) -> None:
    for key, value in new_status_dict.items():
        with sqlite3.connect('task.db') as db:
            query = f"""
            UPDATE orders
            SET status='{value}'
            WHERE order_id='{key}'
            """
        db.execute(query)
        db.commit()


def read_user(login: str, password: str):
    with sqlite3.connect('users.db') as db:
        try:
            query = f"""
            SELECT *
            FROM users_credentials
            WHERE login == '{login}'
            """
            df = pd.read_sql_query(query, 'users.db')
            return df
        except Exception as error:
            return error
