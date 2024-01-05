import streamlit as st

if 'stats_selector' not in st.session_state:
    st.session_state['stats_selector'] = None

if 'filter_selector' not in st.session_state:
    st.session_state['filter_selector'] = None

if 'day_selector' not in st.session_state:
    st.session_state['day_selector'] = None

if 'result_df' not in st.session_state:
    st.session_state['result_df'] = None