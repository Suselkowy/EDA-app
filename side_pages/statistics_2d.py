import streamlit as st
import plotly.express as px
from utils import scroll_to_top
import pandas as pd
from scipy.stats import chi2_contingency, kruskal


def generate_statistics(df, selected_variables):
    if len(selected_variables) == 0: return
    sel_categorical = []
    sel_numerical = []
    for var in selected_variables:
        if df[var].dtype == 'object':
            sel_categorical.append(var)
        elif df[var].dtype in ['int64', 'float64']:
            sel_numerical.append(var)

    if len(sel_numerical) > 1:
        corr = df.loc[:, sel_numerical].corr()
        fig = px.imshow(corr,
                        text_auto=True,
                        aspect="auto",
                        color_continuous_scale='RdBu_r',
                        labels=dict(color="Correlation"),
                        )
        fig.update_layout(coloraxis_colorbar=dict(title="Correlation", tickvals=[-1, -0.5, 0, 0.5, 1]),
                          title_text='Correlation Matrix')
        st.plotly_chart(fig, theme="streamlit")

    if len(sel_categorical) > 1:
        results = []
        for i, var1 in enumerate(sel_categorical):
            for var2 in sel_categorical[i + 1:]:
                contingency_table = pd.crosstab(df[var1], df[var2])
                chi2, p, dof, _ = chi2_contingency(contingency_table)
                results.append({
                    'Variable 1': var1,
                    'Variable 2': var2,
                    'Chi-Square Statistic': chi2,
                    'p-value': p,
                    'Degrees of Freedom': dof
                })
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True, hide_index=True)

    if len(sel_categorical) > 1 and len(sel_numerical) > 0:
        results = []
        for numerical in sel_numerical:
            for categorical in sel_categorical:
                groups = df.groupby(categorical)[numerical].apply(list)
                stat, p_value = kruskal(*groups)
                results.append({
                    'Variable 1': numerical,
                    'Variable 2': categorical,
                    'Test Type': 'Kruskal-Wallis',
                    'Statistic': stat,
                    'p-value': p_value,
                    'Degrees of Freedom': len(groups) - 1
                })

        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True, hide_index=True)
    return


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
    all_categorical_variables = df.select_dtypes(include=['object']).columns.tolist()
    all_datetime_variables = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
    all_numerical_variables = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    st.write("### 2D Statistics")
    col1, col2, col3, col4 = st.columns([0.15, 0.25, 0.25, 0.25])
    with col1:
        select_all = st.button("Select All")
    with col2:
        select_all_numerical = st.button("Select All Numerical")
    with col3:
        select_all_categorical = st.button("Select All Categorical")
    with col4:
        select_all_date = st.button("Select All Date")

    selected_variables = st.multiselect("Select variables", all_variables, key="selected_variables")

    def overwrite_selected_variables(new_variables):
        del st.session_state['selected_variables']
        st.session_state['selected_variables'] = new_variables
        st.rerun()

    if select_all:
        overwrite_selected_variables(all_variables)
    elif select_all_numerical:
        overwrite_selected_variables(all_numerical_variables)
    elif select_all_categorical:
        overwrite_selected_variables(all_categorical_variables)
    elif select_all_date:
        overwrite_selected_variables(all_datetime_variables)

    if selected_variables:
        generate_statistics(df, selected_variables)

    st.write("### 2D plots")
    selected_variable_plot_a = st.selectbox(f"Select first variable to plot", options=all_variables,
                                            index=None, key="a")
    selected_variable_plot_b = st.selectbox(f"Select second variable to plot", options=all_variables,
                                            index=None, key="b")

    if selected_variable_plot_a and selected_variable_plot_b:
        generate_2d_plots(df, [selected_variable_plot_a, selected_variable_plot_b])

    if st.session_state['new_page']:
        scroll_to_top()
