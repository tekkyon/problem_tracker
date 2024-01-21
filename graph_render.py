import altair as alt
import pandas as pd
import streamlit as st

alt.renderers.set_embed_options(format_locale="ru-RU", time_format_locale="ru-RU")

def render_circle_graph(dataframe: pd.DataFrame,
                        x: str,
                        y: str,
                        color: str,
                        height: st.session_state,
                        legend_pos: str = 'bottom'):


    point_altair_chart = alt.Chart(dataframe).mark_circle().encode(
        x=alt.X(x),
        y=alt.Y(y),
        color=alt.Color(color, legend=alt.Legend(orient=legend_pos))
    ).properties(
        height=height,
        width='container'
    )
    return point_altair_chart


def render_line_graph(dataframe: pd.DataFrame,
                      x: str,
                      y: str,
                      color: str,
                      height: st.session_state,
                      legend_pos: str = 'bottom'):
    line_altair_chart = alt.Chart(dataframe).mark_line().encode(
        x=alt.X(x),
        y=alt.Y(y),
        color=alt.Color(color, legend=alt.Legend(orient=legend_pos))
    ).properties(
        width='container',
        height=height
    )
    return line_altair_chart

def abs_line_graph(dataframe: pd.DataFrame,
                      x: str,
                      y: str,
                      color: str,
                      height: st.session_state,
                      legend_pos: str = 'bottom'):
    line_altair_chart = alt.Chart(dataframe).mark_area().encode(
        x=x,
        y=alt.Y(y).stack("normalize"),
        color=alt.Color(color, legend=alt.Legend(orient=legend_pos))
    ).properties(
        height=height,
        width='container'
    )
    return line_altair_chart