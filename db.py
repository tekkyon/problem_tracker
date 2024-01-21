import sqlite3
import pandas as pd
from datetime import date

from config import db

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


def add_lexicon(db, key, value):
    with sqlite3.connect(db) as db:
        query = f"""
        INSERT INTO lexicon
        VALUES
        ('{key}', '{value}')
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

