import datetime

import pandas as pd
import streamlit as st

import lexicon
from config import db
from dashboard_functions import render_default_dataframe
import altair as alt
from pandas.tseries.offsets import DateOffset

from graph_render import render_circle_graph, render_line_graph, abs_line_graph


def render_graphics_tab():
    df = render_default_dataframe(db, 'main', lexicon.columns_list)
    df['type'] = df['type'].apply(lambda x: lexicon.lexicon_dict[x])
    df['marketplace'] = df['marketplace'].apply(lambda x: lexicon.lexicon_dict[x])
    df.rename(columns={'type': 'Тип проблемы',
                       'date': 'Дата',
                       'marketplace': 'Маркетплейс',
                       'sku_number': 'Артикул',
                       'comment': 'Комментарий'}, inplace=True)

    df = df.drop(columns=['Комментарий']).sort_values(by='Дата')

    st.session_state['graph_selector'] = st.selectbox(label='Какой график построить?',
                                                      options=['По типу проблемы',
                                                               'Cтатистика по маркетплейсам'])

    st.session_state['graph_period_selector'] = st.selectbox(label='Периодичность',
                                                             options=['По дням',
                                                                      'По неделям',
                                                                      'По месяцам'])

    if st.session_state['graph_selector'] != 'Смешанный':
        st.session_state['graph_radio_abs_selector'] = st.radio(label='Метод отображения',
                                                                options=['Относительные значения',
                                                                         'Абсолютные значения'],
                                                                horizontal=True,
                                                                label_visibility='collapsed')

    if st.session_state['graph_period_selector'] == 'По месяцам':
        frequency_graph = 'M'
    elif st.session_state['graph_period_selector'] == 'По дням':
        frequency_graph = 'D'
    elif st.session_state['graph_period_selector'] == 'По неделям':
        frequency_graph = 'W'

    if st.session_state['graph_selector'] == 'По типу проблемы':
        df = df.groupby(by=[pd.Grouper(key='Дата', freq=frequency_graph), 'Тип проблемы']).agg(
            {'Артикул': 'count'}).reset_index()
        df.rename(columns={'Артикул': 'Число проблем'}, inplace=True)

        if st.session_state['graph_radio_abs_selector'] == 'Относительные значения':

            line = render_line_graph(df,
                                     'Дата',
                                     'Число проблем',
                                     'Тип проблемы',
                                     st.session_state['graph_scale_slider'])

            result = line

        if st.session_state['graph_radio_abs_selector'] == 'Абсолютные значения':
            result = abs_line_graph(df,
                                    'Дата',
                                    'Число проблем',
                                    'Тип проблемы',
                                    st.session_state['graph_scale_slider'])

        st.altair_chart(result, use_container_width=True, theme=None)

    if st.session_state['graph_selector'] == 'Cтатистика по маркетплейсам':
        df = df.groupby(by=[pd.Grouper(key='Дата', freq=frequency_graph), 'Маркетплейс']).agg(
            {'Артикул': 'count'}).reset_index()
        df.rename(columns={'Артикул': 'Число проблем'}, inplace=True)

        if st.session_state['graph_radio_abs_selector'] == 'Относительные значения':

            line = render_line_graph(df,
                                     'Дата',
                                     'Число проблем',
                                     'Маркетплейс',
                                     st.session_state['graph_scale_slider'],
                                     marketplace=True)

            result = line

        if st.session_state['graph_radio_abs_selector'] == 'Абсолютные значения':
            result = abs_line_graph(df,
                                    'Дата',
                                    'Число проблем',
                                    'Маркетплейс',
                                    st.session_state['graph_scale_slider'],
                                    marketplace=True)

        st.altair_chart(result, use_container_width=True, theme=None)


