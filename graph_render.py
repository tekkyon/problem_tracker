import altair as alt
import pandas as pd
import streamlit as st

from dashboard_functions import render_period_pivot


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


def draw_problems(start='2022-12-01', end='2024-01-27', period='day'):
    source = render_period_pivot(start=start, end=end, period=period)

    source['Дата'] = source['Дата'].dt.date

    domain = ['Проблема с товаром', 'Проблема со сборкой']
    range_ = ['#0000FF', 'firebrick']

    highlight = alt.selection_point()

    base = alt.Chart(source).transform_fold(
        ['Проблема с товаром',
         'Проблема со сборкой']
    ).mark_circle(opacity=0.75
                  ).encode(
        x=alt.X('Дата', title='Дата'),
        y=alt.Y('value:Q', title='Количество проблем'),
        color=alt.Color('key:N').legend(orient='bottom', title=None).scale(domain=domain, range=range_)
    )

    lines = base.mark_line(opacity=0.5,
                           interpolate='monotone',
                           point=True).encode()

    result = base + lines

    return result


def draw_markets(start='2022-12-01',
                 end='2024-01-27',
                 period='day'):
    source = render_period_pivot(start=start, end=end, period=period)

    source['Дата'] = source['Дата'].dt.date
    source = source.rename(columns={'Яндекс.Маркет': 'ЯндексМаркет'})

    domain = ['Wildberries', 'Озон', 'ЯндексМаркет']
    range_ = ['#5f23d3', '#1e4de5', '#f8c62c']

    result = alt.Chart(source).transform_fold(
        ['Wildberries',
         'Озон',
         'ЯндексМаркет']
    ).mark_line(opacity=0.75,
                interpolate='monotone',
                point=True).encode(
        x=alt.X('Дата', title='Дата'),
        y=alt.Y('value:Q', title='Количество проблем'),
        color=alt.Color('key:N').legend(orient='bottom', title=None).scale(domain=domain, range=range_)
    )

    return result


def draw_barchart(start='2024-01-01',
                  end='2024-01-31',
                  period='day'):
    source = render_period_pivot(start=start, end=end, period=period)
    source['Дата'] = source['Дата'].dt.date

    domain = ['Проблема с товаром', 'Проблема со сборкой']
    range_ = ['#0000FF', 'firebrick']

    highlight = alt.selection_point()

    base = alt.Chart(source).mark_bar(
    ).encode(
        x='Дата',
        y='К'
    )

    return base


def draw_b2b(start='2022-12-01',
             end='2024-01-27',
             period='day',
             b2b=True,
             by_problem=True):
    source = render_period_pivot(start=start,
                                 end=end,
                                 period=period,
                                 b2b=b2b)

    source['Дата'] = source['Дата'].dt.date

    domain = ['Проблема с товаром', 'Проблема со сборкой', 'Проблема с доставкой']
    range_ = ['#0000FF', 'firebrick', 'teal']

    base = alt.Chart(source).transform_fold(
        ['Проблема с товаром',
         'Проблема со сборкой',
         'Проблема с доставкой']
    ).mark_circle(opacity=0.75
                  ).encode(
        x=alt.X('Дата', title='Дата'),
        y=alt.Y('value:Q', title='Количество проблем'),
        color=alt.Color('key:N').legend(orient='bottom', title=None).scale(domain=domain, range=range_)
    )

    lines = base.mark_line(opacity=0.5,
                           interpolate='monotone',
                           point=True).encode()

    result = base + lines

    return result