import pandas as pd
import streamlit as st

import lexicon
from config import db
from dashboard_functions import render_default_dataframe
import altair as alt

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
                                                      options=['Test', 'По типу проблемы',
                                                               'Cтатистика по маркетплейсам',
                                                               'Смешанный'])

    st.session_state['graph_period_selector'] = st.selectbox(label='Периодичность',
                                                             options=['По дням',
                                                                      'По неделям',
                                                                      'По месяцам'])

    if st.session_state['graph_selector'] != 'Смешанный':
        st.session_state['graph_radio_abs_selector'] = st.radio(label='Метод отображения',
                                                                options=['Относительные значения',
                                                                         'Абсолютные значения'],
                                                                horizontal=True)

    if st.session_state['graph_period_selector'] == 'По месяцам':
        frequency_graph = 'M'
    elif st.session_state['graph_period_selector'] == 'По дням':
        frequency_graph = 'D'
    elif st.session_state['graph_period_selector'] == 'По неделям':
        frequency_graph = 'W'

    # if st.session_state['graph_selector'] == 'Test':
    #     df = df.groupby(by=[pd.Grouper(key='Дата', freq=frequency_graph), 'Тип проблемы']).agg(
    #         {'Артикул': 'count'}).reset_index()
    #     df.rename(columns={'Артикул': 'Число проблем'}, inplace=True)
    #
    #     nearest = alt.selection_point(nearest=True, on='mouseover',
    #                                   fields=['Дата'], empty=False)
    #
    #     line = alt.Chart(df).mark_line(interpolate='basis').encode(
    #         x='Дата',
    #         y='Число проблем',
    #         color=alt.Color('Тип проблемы', legend=alt.Legend(orient='bottom'))
    #     )
    #
    #     selectors = alt.Chart(df).mark_point().encode(
    #         x='Дата',
    #         opacity=alt.value(0),
    #     ).add_params(
    #         nearest
    #     )
    #
    #     points = line.mark_point().encode(
    #         opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    #     )
    #
    #     text = line.mark_text(align='left', dx=5, dy=-5).encode(
    #         text=alt.condition(nearest, 'Число проблем', alt.value(' '))
    #     )
    #
    #     rules = alt.Chart(df).mark_rule(color='gray').encode(
    #         x='Дата',
    #     ).transform_filter(
    #         nearest
    #     )
    #
    #
    #     result = alt.layer(
    #         line, selectors, points, rules, text
    #     ).properties(
    #         height=450
    #     )
    #
    #     st.altair_chart(result, use_container_width=True, theme=None)

    if st.session_state['graph_selector'] == 'По типу проблемы':
        df = df.groupby(by=[pd.Grouper(key='Дата', freq=frequency_graph), 'Тип проблемы']).agg(
            {'Артикул': 'count'}).reset_index()
        df.rename(columns={'Артикул': 'Число проблем'}, inplace=True)

        if st.session_state['graph_radio_abs_selector'] == 'Относительные значения':
            circle = render_circle_graph(df,
                                         'Дата',
                                         'Число проблем',
                                         'Тип проблемы',
                                         st.session_state['graph_scale_slider'])

            line = render_line_graph(df,
                                     'Дата',
                                     'Число проблем',
                                     'Тип проблемы',
                                     st.session_state['graph_scale_slider'])

            result = circle + line

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
            circle = render_circle_graph(df,
                                         'Дата',
                                         'Число проблем',
                                         'Маркетплейс',
                                         st.session_state['graph_scale_slider'])

            line = render_line_graph(df,
                                     'Дата',
                                     'Число проблем',
                                     'Маркетплейс',
                                     st.session_state['graph_scale_slider'])

            result = circle + line

        if st.session_state['graph_radio_abs_selector'] == 'Абсолютные значения':
            result = abs_line_graph(df,
                                    'Дата',
                                    'Число проблем',
                                    'Маркетплейс',
                                    st.session_state['graph_scale_slider'])

        st.altair_chart(result, use_container_width=True, theme=None)

    if st.session_state['graph_selector'] == 'Смешанный':
        df_1 = df.groupby(by=[pd.Grouper(key='Дата', freq=frequency_graph), 'Тип проблемы']).agg(
            {'Артикул': 'count'}).reset_index()
        df_1.rename(columns={'Артикул': 'Число проблем'}, inplace=True)

        df_2 = df.groupby(by=[pd.Grouper(key='Дата', freq=frequency_graph), 'Маркетплейс']).agg(
            {'Артикул': 'count'}).reset_index()
        df_2.rename(columns={'Артикул': 'Число проблем'}, inplace=True)

        interval = alt.selection_interval()

        line_altair_chart = alt.Chart(df_1).mark_line().encode(
            x=alt.X('Дата:T'),
            y='Число проблем:Q',
            color=alt.Color('Тип проблемы:N', legend=alt.Legend(orient='bottom'))
        ).properties(
            width=1100
        ).add_selection(
            interval
        )

        circle_altair_chart = alt.Chart(df_1).mark_circle().encode(
            x=alt.X('Дата:T'),
            y='Число проблем:Q',
            color='Тип проблемы:N'
        ).properties(
            width=1100
        ).add_selection(
            interval
        )

        add_altair_chart = alt.Chart(df_2).mark_bar().encode(
            x='Число проблем:Q',
            y='Маркетплейс:N',
            color='Маркетплейс'
        ).properties(
            width=1100,
            height=80
        ).transform_filter(
            interval
        )
        first_graph = line_altair_chart + circle_altair_chart
        result = first_graph & add_altair_chart

        st.altair_chart(result, use_container_width=True, theme=None)
