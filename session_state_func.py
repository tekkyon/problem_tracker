import streamlit as st
import datetime


def create_session_state():
    if 'first_load' not in st.session_state:
        st.session_state['first_load'] = True

    if 'stats_selector' not in st.session_state:
        st.session_state['stats_selector'] = None

    if 'filter_selector' not in st.session_state:
        st.session_state['filter_selector'] = None

    if 'day_selector' not in st.session_state:
        st.session_state['day_selector'] = None

    if 'common_tab_selector' not in st.session_state:
        st.session_state['common_tab_selector'] = None

    if 'result_df' not in st.session_state:
        st.session_state['result_df'] = None

    if 'result_graph' not in st.session_state:
        st.session_state['result_graph'] = None

    if 'period_selector' not in st.session_state:
        st.session_state['period_selector'] = None

    if 'day_1' not in st.session_state:
        st.session_state['day_1'] = datetime.date(2022, 12, 13)

    if 'day_2' not in st.session_state:
        st.session_state['day_2'] = datetime.date.today()

    if 'year_1' not in st.session_state:
        st.session_state['year_1'] = 2022

    if 'month_1' not in st.session_state:
        st.session_state['month_1'] = 12

    if 'metric_state' not in st.session_state:
        st.session_state['metric_state'] = None

    if 'total_problems' not in st.session_state:
        st.session_state['total_problems'] = None

    if 'period_problems' not in st.session_state:
        st.session_state['period_problems'] = None

    if 'defect_month_before' not in st.session_state:
        st.session_state['defect_month_before'] = None

    if 'package_month_before' not in st.session_state:
        st.session_state['package_month_before'] = None

    if 'total_month_before' not in st.session_state:
        st.session_state['total_month_before'] = None

    if 'delta_option' not in st.session_state:
        st.session_state['delta_option'] = None

    if 'graph_selector' not in st.session_state:
        st.session_state['graph_selector'] = None

    if 'graph_period_selector' not in st.session_state:
        st.session_state['graph_period_selector'] = None

    if 'graph_radio_abs_selector' not in st.session_state:
        st.session_state['graph_radio_abs_selector'] = 'Относительные значения'

    if 'sku_radio_selector' not in st.session_state:
        st.session_state['sku_radio_selector'] = 'По типу проблемы'

    if 'graph_scale_slider' not in st.session_state:
        st.session_state['graph_scale_slider'] = 450

    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None

    if 'graph_month_selector' not in st.session_state:
        st.session_state['graph_month_selector'] = None

    if 'graph_year_selector' not in st.session_state:
        st.session_state['graph_year_selector'] = None

    if 'graph_start' not in st.session_state:
        st.session_state['graph_start'] = None

    if 'graph_end' not in st.session_state:
        st.session_state['graph_end'] = None

    if 'graph_month_selector_end' not in st.session_state:
        st.session_state['graph_month_selector_end'] = None

    if 'graph_year_selector_end' not in st.session_state:
        st.session_state['graph_year_selector_end'] = None

    if 'table_year_selector' not in st.session_state:
        st.session_state['table_year_selector'] = None

    if 'table_month_selector' not in st.session_state:
        st.session_state['table_month_selector'] = None

    if 'show_month' not in st.session_state:
        st.session_state['show_month'] = False

    if 'result_table' not in st.session_state:
        st.session_state['result_table'] = None

    if 'admin_mode' not in st.session_state:
        st.session_state['admin_mode'] = False