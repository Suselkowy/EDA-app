from unicodedata import numeric
import streamlit as st
import plotly.express as px
import pandas as pd

from side_pages.data_manipulation import convert_df_to_csv


def generate_statistics(df, selected_variables):
    statistics = {}
    num = 1
    for var in selected_variables:
        if df[var].dtype == 'int64' or df[var].dtype == 'float64':
            statistics[num] = {
                'Variable': var,
                'Mean': df[var].mean(),
                'Median': df[var].median(),
                'Std Dev': df[var].std(),
                'Min': df[var].min(),
                'Max': df[var].max(),
            }
            num += 1
        elif df[var].dtype == 'object':
            unique_values = df[var].value_counts()
            total_count = len(df[var])
            for value, count in unique_values.items():
                stats = {
                    'Variable': var,
                    'Value': value,
                    'Count': count,
                    'Count Percentage': (count / total_count) * 100
                }
                statistics[num] = stats
                num += 1
        elif df[var].dtype == 'datetime64[ns]':
            statistics[num] = {
                'Variable': var,
                'Earliest Date': df[var].min(),
                'Latest Date': df[var].max(),
            }
            num += 1

    statistics_df = pd.DataFrame(statistics).transpose()
    return statistics_df

def plot_categorical_categorical(df, xs, ys):
    if xs == ys: return
    grouped_df = df.groupby([xs, ys]).size().reset_index(name='count')

    fig = px.bar(grouped_df, x=xs, y='count', color=ys, title=f'Stacked Bar Chart of {xs} by {ys}', barmode='stack')
    st.plotly_chart(fig, use_container_width=True)

    fig = px.density_heatmap(grouped_df, x=xs, y=ys, z='count', title=f"Heatmap of {xs} by {ys}")
    st.plotly_chart(fig, use_container_width=True)

def plot_numerical_numerical(df, xs, ys):
    fig = px.scatter(df, x=xs, y=ys, title=f"Scatter plot of {xs} vs {ys}")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.density_heatmap(df, x=xs, y=ys, title=f"Heatmap of {xs} vs {ys}")
    st.plotly_chart(fig, use_container_width=True)

def plot_categorical_numerical(df, categorical, numerical):
    fig = px.strip(df, x=categorical, y=numerical, title=f"Strip plot of {categorical} vs {numerical}")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.box(df, x=categorical, y=numerical, title=f"Box plot of {categorical} vs {numerical}")
    st.plotly_chart(fig, use_container_width=True)

def generate_2d_plots(df, selected_variables):
    xs, ys = selected_variables

    x_type = "categorical" if df[xs].dtype == "object" else "numerical"
    y_type = "categorical" if df[ys].dtype == "object" else "numerical"
    
    if x_type == "categorical" and y_type == "categorical":
        plot_categorical_categorical(df, xs, ys)
    elif x_type == "numerical" and y_type == "numerical":
        plot_numerical_numerical(df, xs, ys)
    elif x_type == "numerical" and y_type == "categorical":
        plot_categorical_numerical(df, categorical=xs, numerical=ys)
    else:
        plot_categorical_numerical(df, categorical=ys, numerical=xs)

def statistics_2d_page():
    if not st.session_state['edited']:
        df = st.session_state['primary_df']
    else:
        df = st.session_state['edited_df']
    all_variables = df.columns.tolist()

    st.write("### 2D plots")
    selected_variable_plot_a = st.selectbox(f"Select first variable to plot", options=all_variables,
                                          index=None, key="a")
    selected_variable_plot_b = st.selectbox(f"Select second variable to plot", options=all_variables,
                                          index=None, key="b")

    if selected_variable_plot_a and selected_variable_plot_b:
        generate_2d_plots(df, [selected_variable_plot_a, selected_variable_plot_b])
