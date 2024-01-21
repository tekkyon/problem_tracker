import streamlit as st
import datetime
import time

from cookie_test import cookie_manager


def create_session_state():
    if 'stats_selector' not in st.session_state:
        st.session_state['stats_selector'] = None

    if 'filter_selector' not in st.session_state:
        st.session_state['filter_selector'] = None

    if 'day_selector' not in st.session_state:
        st.session_state['day_selector'] = None

    if 'result_df' not in st.session_state:
        st.session_state['result_df'] = None

    if 'period_selector' not in st.session_state:
        st.session_state['period_selector'] = None

    if 'day_1' not in st.session_state:
        st.session_state['day_1'] = datetime.date(2022, 12, 13)

    if 'day_2' not in st.session_state:
        st.session_state['day_2'] = datetime.date.today()

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

    # if 'cookie_manager' not in st.session_state:
    #     cookies = cookie_manager.get_all()
    #     time.sleep(0.5)
    #     st.session_state['cookie_manager'] = True
    #
    # value = cookie_manager.get(cookie='authed')
    # if value is None:
    #     if 'authed' not in st.session_state:
    #         st.session_state['authed'] = False
    # else:
    #     st.session_state['authed'] = True

    if 'authed' not in st.session_state:
        st.session_state['authed'] = False

    if 'sku_radio_selector' not in st.session_state:
        st.session_state['sku_radio_selector'] = 'По типу проблемы'

    if 'graph_scale_slider' not in st.session_state:
        st.session_state['graph_scale_slider'] = 450

    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
