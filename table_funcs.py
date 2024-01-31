import streamlit as st
import pandas as pd

import lexicon
from config import db
from dashboard_functions import render_default_dataframe, render_sku_table


def render_common_table():
    df = render_default_dataframe(db, 'main', lexicon.columns_list)
    df['type'] = df['type'].apply(lambda x: lexicon.lexicon_dict[x])
    df['marketplace'] = df['marketplace'].apply(lambda x: lexicon.lexicon_dict[x])
    df.rename(columns={'type': 'Тип проблемы',
                       'date': 'Дата',
                       'marketplace': 'Маркетплейс',
                       'sku_number': 'Артикул',
                       'comment': 'Комментарий'}, inplace=True)
    df['Дата'] = pd.to_datetime(df['Дата']).dt.date
    st.session_state['total_problems'] = df.shape[0]
    df = df.loc[
        (df['Дата'] >= st.session_state['day_1']) & (df['Дата'] <= st.session_state['day_2'])]
    st.session_state['period_problems'] = df.shape[0]
    return df

def render_sku_groups_table(sku_group_dict: dict, df: pd.DataFrame):
    for key, value in sku_group_dict.items():
        st.subheader(key)
        st.dataframe(render_sku_table(df, value), use_container_width=True)
