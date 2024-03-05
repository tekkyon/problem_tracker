import streamlit as st

import lexicon
from config import db
from dashboard_functions import render_default_dataframe
import pandas as pd

b2b_column_list = ['type',
                   'bitrix_id',
                   'sku',
                   'sku_number',
                   'date',
                   'worker',
                   'comment',
                   ]


def render_b2b_tab():
    b2b_col1, b2b_col2 = st.columns([1, 4])

    with b2b_col2:
        df = render_default_dataframe(db, 'main', b2b_column_list, b2b=True)

        df['type'] = df['type'].apply(lambda x: lexicon.lexicon_dict[x])
        df['sku'] = df['sku'].apply(lambda x: lexicon.lexicon_dict[x])


        df = df.rename(columns={'type': 'Тип проблемы',
                                'bitrix_id': 'Номер заказа',
                                'sku': 'Группа артикула',
                                'sku_number': 'Номер артикула',
                                'date': 'Дата',
                                'worker': 'Ответственный',
                                'comment': 'Комментарий'})
        df['Дата'] = pd.to_datetime(df['Дата']).dt.date

        st.dataframe(df,
                     use_container_width=True,
                     hide_index=True)
