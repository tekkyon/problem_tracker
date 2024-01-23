import altair as alt
import pandas as pd
import streamlit as st


def render_circle_graph(dataframe: pd.DataFrame,
                        x: str,
                        y: str,
                        color: str,
                        height: st.session_state,
                        legend_pos: str = 'bottom'):
    point_altair_chart = alt.Chart(dataframe).mark_circle().encode(
        x=alt.X(x),
        y=alt.Y(y),
        color=alt.Color(color, legend=alt.Legend(orient=legend_pos)).scale(scheme="set1")
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
                      legend_pos: str = 'bottom',
                      marketplace=False):
    range_ = ['#9932CC', '#0000FF', '#FFD700']

    if marketplace:
        line_altair_chart = alt.Chart(dataframe).mark_line(interpolate='monotone', point=True).encode(
            x=alt.X(x),
            y=alt.Y(y),
            color=alt.Color(color, legend=alt.Legend(orient=legend_pos)).scale(range=range_)
        ).properties(
            width='container',
            height=height
        )
        return line_altair_chart
    else:
        line_altair_chart = alt.Chart(dataframe).mark_line(interpolate='monotone', point=True).encode(
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
                   legend_pos: str = 'bottom',
                   marketplace=False):

    range_ = ['#9932CC', '#0000FF', '#FFD700']

    if marketplace:

        line_altair_chart = alt.Chart(dataframe).mark_area(opacity=0.6, interpolate='basis').encode(
            x=x,
            y=alt.Y(y).stack("normalize"),
            color=alt.Color(color, legend=alt.Legend(orient=legend_pos)).scale(range=range_)
        ).properties(
            height=height,
            width='container'
        )
        return line_altair_chart

    else:
        line_altair_chart = alt.Chart(dataframe).mark_area(opacity=0.6, interpolate='basis').encode(
            x=x,
            y=alt.Y(y).stack("normalize"),
            color=alt.Color(color, legend=alt.Legend(orient=legend_pos))
        ).properties(
            height=height,
            width='container'
        )
        return line_altair_chart
