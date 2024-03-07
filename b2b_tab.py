import streamlit as st

import lexicon
from config import db
from dashboard_functions import render_default_dataframe, change_worker, change_date
import pandas as pd
import altair as alt

b2b_column_list = ['type',
                   'bitrix_id',
                   'sku',
                   'sku_number',
                   'date',
                   'worker',
                   'comment',
                   ]


def render_b2b_tab():
    df = render_default_dataframe(db, 'main', b2b_column_list, b2b=True)

    df['type'] = df['type'].apply(lambda x: lexicon.lexicon_dict[x])
    df['sku'] = df['sku'].apply(lambda x: lexicon.lexicon_dict[x])
    df['sku_number'] = df['sku_number'].apply(lambda x: str(x))

    df['Артикул'] = df['sku'] + df['sku_number']
    df = df.drop(['sku', 'sku_number'], axis=1)

    df = df.rename(columns={'type': 'Тип проблемы',
                            'bitrix_id': 'Номер заказа',
                            'date': 'Дата',
                            'worker': 'Ответственный',
                            'comment': 'Комментарий'})

    # df['Дата'] = pd.to_datetime(df['Дата']).dt.date

    b2b_editor_cfg = {
        'Тип проблемы': st.column_config.SelectboxColumn(
            'Тип проблемы',
            width='medium',
            options=['Проблема со сборкой',
                     'Проблема с товаром',
                     'Проблема с доставкой'],
            required=True,
        ),
        'Дата': st.column_config.DateColumn(
            'Дата'
        ),
        'Ответственный': st.column_config.SelectboxColumn(
            'Ответственный',
            width='medium',
            options=['Сборщик 1',
                     'Сборщик 2',
                     'Нет'],
            required=True
        ),
        'Номер заказа': st.column_config.TextColumn(
            'Номер заказа',
            width='small'
        )
    }

    with st.form('save b2b table'):
        b2b_editor = st.data_editor(df,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config=b2b_editor_cfg,
                                    column_order=['Тип проблемы',
                                                  'Номер заказа',
                                                  'Дата',
                                                  'Артикул',
                                                  'Ответственный',
                                                  'Комментарий'],
                                    disabled=['Тип проблемы',
                                              'Номер заказа',
                                              'Артикул',
                                              'Комментарий'],
                                    key='b2b_editor'
                                    )

        save_b2b_table_btn = st.form_submit_button('Сохранить изменения',
                                                   use_container_width=True)
        if save_b2b_table_btn:
            edit_b2b_dict = st.session_state["b2b_editor"]['edited_rows']
            for key, value in edit_b2b_dict.items():
                order_id = df['Номер заказа'].iloc[key]
                worker = b2b_editor['Ответственный'].iloc[key]
                date = b2b_editor['Дата'].iloc[key]
                change_worker(order_id, worker)
                change_date(order_id, date)
            st.toast('Данные обновлены')




