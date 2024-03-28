import streamlit as st

def init_session_states():
    if 'initial_wb' not in st.session_state:
        st.session_state['initial_wb'] = None

    if 'initial_ozon' not in st.session_state:
        st.session_state['initial_ozon'] = None

    if 'cost_wb' not in st.session_state:
        st.session_state['cost_wb'] = None

    if 'cost_ozon' not in st.session_state:
        st.session_state['cost_ozon'] = None

    if 'counted_wb' not in st.session_state:
        st.session_state['counted_wb'] = None

    if 'counted_ozon' not in st.session_state:
        st.session_state['counter_ozon'] = None

    if 'first_load' not in st.session_state:
        st.session_state['first_load'] = True