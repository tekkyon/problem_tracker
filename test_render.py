import streamlit as st
import pandas as pd

import lexicon
from config import db
from dashboard_functions import render_default_dataframe
from graph_render import draw_barchart


def render_test():
    # st.altair_chart(draw_barchart(), use_container_width=True, theme=None)
    pass