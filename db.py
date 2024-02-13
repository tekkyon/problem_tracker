import sqlite3
import pandas as pd
from datetime import date, datetime

from config import db, task_db


def init_tables(db):
    with sqlite3.connect(db) as db:
        query = """
        CREATE TABLE IF NOT EXISTS main(
        sku TEXT,
        sku_number INTEGER,
        marketplace TEXT,
        date TEXT,
        type TEXT,
        comment TEXT)
        """

        db.execute(query)

        db.commit()


def init_bitrix_buffer(db):
    with sqlite3.connect(db) as db:
        query = """
        CREATE TABLE IF NOT EXISTS bitrix_buffer(
        order_id INTEGER UNIQUE,
        order_number_1c TEXT,
        status TEXT)
        """

        db.execute(query)

        db.commit()


def init_lexicon_table(db):
    with sqlite3.connect(db) as db:
        query = """
        CREATE TABLE IF NOT EXISTS lexicon(
        key TEXT,
        value TEXT)
        """

        db.execute(query)

        db.commit()


def init_users_tables(db):
    with sqlite3.connect(db) as db:
        query = """
        CREATE TABLE IF NOT EXISTS users(
        username TEXT,
        user_id INTEGER,
        role TEXT)
        """

        db.execute(query)

        db.commit()


def insert_db(db, sku, sku_number, marketplace, date_str, type_of_problem, comment, type_of_mp, manager_id):
    with sqlite3.connect(db) as db:
        date_str = date_str.split('/')
        today = date.today()

        new_date = f'{date_str[0]}-{date_str[1]}-{date_str[2]}'
        query = f"""
        INSERT INTO main
        VALUES
        ('{sku}',
         '{sku_number}',
          '{marketplace}',
           '{new_date}',
            '{type_of_problem}',
             '{comment}',
              '{type_of_mp}',
              '{today}',
              '{manager_id}')
        """

        db.execute(query)
        db.commit()


def add_column_to_db(db, column_name, table='main'):
    with sqlite3.connect(db) as db:
        query = f"""
        ALTER TABLE {table} ADD COLUMN {column_name} char(255)
        """

    db.execute(query)
    db.commit()


def add_user(db, username, user_id, role='manager', table='users', loc='not_defined'):
    with sqlite3.connect(db) as db:
        query = f"""
        INSERT INTO {table}
        VALUES
        ('{username}', '{user_id}', '{role}', '{loc}')
        """

    db.execute(query)
    db.commit()


def read_users(db, table='users'):
    with sqlite3.connect(db) as db:
        query = f"""
        SELECT * FROM {table}
        """
    df = pd.read_sql_query(query, db)
    return df


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

def check_uniq_id(order_id, task_db=task_db):
    with sqlite3.connect(task_db) as con:
        query = f"""
        SELECT *
        FROM orders
        WHERE order_id = '{order_id}' 
        """
        cursor = con.cursor()
        cursor.execute(query)
        if len(cursor.fetchall()) > 0:
            return False
        else:
            return True


def add_bitrix_to_sql(order_id, order_number, status, dims, executor='default', task_db=task_db):
    if check_uniq_id(order_id):
        default_date = ''
        with sqlite3.connect(task_db) as db:
            query = f"""
            INSERT INTO orders
            VALUES
            ('{order_id}',
             '{order_number}',
              '{status}',
               '{dims}',
                '{executor}',
                 '{default_date}',
                  '{default_date}')
            """

        db.execute(query)
        db.commit()
    else:
        pass


def update_sql_dim(order_id, dims, executor, task_db=task_db):
    now = datetime.now()
    with sqlite3.connect(task_db) as db:
        query = f"""
        UPDATE orders
        SET dims='{dims}', executor='{executor}', datetime_finish='{now}', status='Готов к отгрузке(собран)'
        WHERE order_id='{order_id}'
        """

    db.execute(query)
    db.commit()


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


def add_new_worker(worker_id: int, firstname: str, lastname: str, position:str, db=task_db):
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