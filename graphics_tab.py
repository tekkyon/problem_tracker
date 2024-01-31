import datetime

import streamlit as st

import lexicon
from dashboard_functions import get_years, get_months
from graph_render import draw_problems, draw_markets


def render_graphics_tab():
    g_col1, g_col2 = st.columns([1, 1])
    with g_col1:
        st.session_state['graph_selector'] = st.selectbox('Какой график построить?',
                                                          options=['По типу проблемы',
                                                                   'По маркетплейсам'])

    with g_col2:
        st.session_state['graph_period_selector'] = st.selectbox('Периодичность',
                                                                 options=['По дням месяца',
                                                                          'По неделям',
                                                                          'По месяцам'])
    match st.session_state['graph_period_selector']:

        case 'По дням месяца':
            period = 'day'
            day_selector = True
            g_period_col1, g_period_col2 = st.columns([1, 1])
            with g_period_col1:
                list_of_years = get_years()
                list_of_years.sort(reverse=True)
                st.session_state['graph_year_selector'] = st.selectbox('Год', options=list_of_years, key='ahz')
            with g_period_col2:
                list_of_month = get_months(st.session_state['graph_year_selector'], day_selector=day_selector)
                list_of_month.sort(reverse=True)

                list_of_month = list(map(lambda x: lexicon.numerical_month_dict[x], list_of_month))

                st.session_state['graph_month_selector'] = st.selectbox('Месяц', options=list_of_month, key='smrndm')
                st.session_state['graph_month_selector'] = [i for i in lexicon.numerical_month_dict if
                                                            lexicon.numerical_month_dict[i] == st.session_state[
                                                                'graph_month_selector']][0]

            match st.session_state['graph_month_selector']:
                case 12:
                    st.session_state['graph_start'] = str(datetime.date(st.session_state['graph_year_selector'],
                                                                        st.session_state['graph_month_selector'],
                                                                        1))
                    st.session_state['graph_end'] = str(datetime.date(st.session_state['graph_year_selector'] + 1,
                                                                      1,
                                                                      1))
                case _:
                    st.session_state['graph_start'] = str(datetime.date(st.session_state['graph_year_selector'],
                                                                        st.session_state['graph_month_selector'],
                                                                        1))
                    st.session_state['graph_end'] = str(datetime.date(st.session_state['graph_year_selector'],
                                                                      st.session_state['graph_month_selector'] + 1,
                                                                      1))

        case 'По неделям':
            period = 'week'
            # g_period_col1, g_period_col2, g_period_col3, g_period_col4 = st.columns([1, 1, 1, 1])
            # with g_period_col1:
            #     list_of_years = get_years()
            #     list_of_years.sort(reverse=True)
            #     default = list_of_years.index(2022)
            #     st.session_state['graph_year_selector'] = st.selectbox('Год',
            #                                                            options=list_of_years,
            #                                                            index=default)
            # with g_period_col2:
            #     list_of_month = get_months(st.session_state['graph_year_selector'])
            #     list_of_month.sort(reverse=True)
            #     st.session_state['graph_month_selector'] = st.selectbox('Месяц',
            #                                                             options=list_of_month)
            #
            #     match st.session_state['graph_month_selector']:
            #         case 12:
            #             list_of_years = get_years(initial_year=st.session_state['graph_year_selector'] + 1)
            #         case _:
            #             list_of_years = get_years(initial_year=st.session_state['graph_year_selector'])
            # with g_period_col3:
            #     list_of_years.sort(reverse=True)
            #     st.session_state['graph_year_selector_end'] = st.selectbox('Год',
            #                                                                options=list_of_years,
            #                                                                key='year_end')
            # with g_period_col4:
            #     list_of_month = get_months(st.session_state['graph_year_selector_end'])
            #     st.session_state['graph_month_selector_end'] = st.selectbox('Месяц',
            #                                                                options=list_of_month,
            #                                                                key='month_end')
            #
            # st.session_state['graph_start'] = str(datetime.date(st.session_state['graph_year_selector'],
            #                                                     st.session_state['graph_month_selector'],
            #                                                     1))
            #
            # st.session_state['graph_end'] = str(datetime.date(st.session_state['graph_year_selector_end'],
            #                                                   st.session_state['graph_month_selector_end'],
            #                                                   1))
            st.session_state['graph_start'] = '2022-12-13'
            st.session_state['graph_end'] = str(datetime.date.today())

        case 'По месяцам':
            period = 'month'
            # g_period_col1, g_period_col2, g_period_col3, g_period_col4 = st.columns([1, 1, 1, 1])
            # with g_period_col1:
            #     list_of_years = get_years()
            #     list_of_years.sort(reverse=True)
            #     default = list_of_years.index(2022)
            #     st.session_state['graph_year_selector'] = st.selectbox('Год',
            #                                                            options=list_of_years,
            #                                                            index=default)
            # with g_period_col2:
            #     list_of_month = get_months(st.session_state['graph_year_selector'])
            #     list_of_month.sort(reverse=True)
            #     st.session_state['graph_month_selector'] = st.selectbox('Месяц',
            #                                                             options=list_of_month)
            #
            #     match st.session_state['graph_month_selector']:
            #         case 12:
            #             list_of_years = get_years(initial_year=st.session_state['graph_year_selector'] + 1)
            #         case _:
            #             list_of_years = get_years(initial_year=st.session_state['graph_year_selector'])
            # with g_period_col3:
            #     list_of_years.sort(reverse=True)
            #     st.session_state['graph_year_selector_end'] = st.selectbox('Год',
            #                                                                options=list_of_years,
            #                                                                key='year_end')
            # with g_period_col4:
            #     list_of_month = get_months(st.session_state['graph_year_selector_end'])
            #     st.session_state['graph_year_selector_end'] = st.selectbox('Месяц',
            #                                                                options=list_of_month,
            #                                                                key='month_end')
            #
            # st.session_state['graph_start'] = str(datetime.date(st.session_state['graph_year_selector'],
            #                                                     st.session_state['graph_month_selector'],
            #                                                     1))
            # #
            # # st.session_state['graph_end'] = str(datetime.date(st.session_state['graph_year_selector_end'],
            # #                                                   st.session_state['graph_month_selector_end'],
            # #                                                   1))
            st.session_state['graph_start'] = '2022-12-13'
            st.session_state['graph_end'] = str(datetime.date.today())

    match st.session_state['graph_selector']:

        case 'По типу проблемы':
            st.session_state['result_graph'] = draw_problems(start=st.session_state['graph_start'],
                                                             end=st.session_state['graph_end'],
                                                             period=period)

        case 'По маркетплейсам':
            st.session_state['result_graph'] = draw_markets(start=st.session_state['graph_start'],
                                                            end=st.session_state['graph_end'],
                                                            period=period)

    if st.session_state['result_graph'] is not None:
        st.altair_chart(st.session_state['result_graph'],
                        use_container_width=True,
                        theme=None)
