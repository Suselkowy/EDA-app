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


def generate_2d_plots(df, selected_variables, graph_type):
    x_var, y_var = selected_variables

    if graph_type == 'Heatmap':
        fig = px.density_heatmap(df, x=x_var, y=y_var, title=f"Heatmap of {x_var} vs {y_var}")
        st.plotly_chart(fig)
    # for var in selected_variables:
    #     if df[var].dtype == 'object':
    #         if graph_type == 'bar chart':
    #             filtered_df = df
    #             fig = px.bar(filtered_df[var].value_counts(), x=filtered_df[var].value_counts().index,
    #                          y=filtered_df[var].value_counts().values,
    #                          labels={'x': var, 'y': 'frequency'}, title=f"{var} bar chart")
    #             st.plotly_chart(fig)
    #         elif graph_type == 'pie chart':
    #             fig = px.pie(df[var].value_counts(), values=df[var].value_counts().values,
    #                          names=df[var].value_counts().index,
    #                          title=f"{var} pie chart")
    #             st.plotly_chart(fig)
    #         elif graph_type == 'tree map':
    #             value_counts = df[var].value_counts().reset_index()
    #             value_counts.columns = ['value', 'count']
    #             fig = px.treemap(value_counts, path=['value'], values='count')
    #             fig.update_layout(title='treemap of unique values counts in column')
    #             st.plotly_chart(fig)
    #
    #     if graph_type == 'Histogram':
    #         if df[var].dtype == 'int64' or df[var].dtype == 'float64':
    #             fig = px.histogram(df, x=var, title=f"{var} Histogram")
    #             st.plotly_chart(fig)
    #         elif df[var].dtype == 'datetime64[ns]':
    #             fig = px.histogram(df, x=var, title=f"{var} Histogram")
    #             st.plotly_chart(fig)
    #     elif graph_type == 'Box Plot':
    #         if df[var].dtype == 'int64' or df[var].dtype == 'float64':
    #             fig = px.box(df, y=var, title=f"{var} Box Plot")
    #             st.plotly_chart(fig)


def statistics2d_page():
    if not st.session_state['edited']:
        df = st.session_state['primary_df']
    else:
        df = st.session_state['edited_df']
    all_variables = df.columns.tolist()

    st.write("### 2D plots")
    selected_variable_plot_a = st.selectbox(f"Select first variable to plot", options=all_variables,
                                          index=None, placeholder='Select first variable', key="a")
    selected_variable_plot_b = st.selectbox(f"Select first variable to plot", options=all_variables,
                                          index=None, placeholder='Select second variable', key="b")

    if selected_variable_plot_a and selected_variable_plot_b:
        a_type = "categorical" if df[selected_variable_plot_a].dtype == "object" else "numerical"
        b_type = "categorical" if df[selected_variable_plot_b].dtype == "object" else "numerical"
        if a_type == "categorical" and b_type == "categorical":
            graph_type = st.selectbox("Select graph type", ["Clustered Bar Chart", "Stacked Bar Chart", "Heatmap"])
        elif a_type == "numerical" and b_type == "numerical":
            graph_type = st.selectbox("Select graph type", ["Scatter Plot", "Line Graph", "Bubble Chart"])
        else:
            graph_type = st.selectbox("Select graph type", ["Grouped Bar Graph", "Stacked Bar Graph", "Boxplot"])

        if graph_type:
            generate_2d_plots(df, [selected_variable_plot_a, selected_variable_plot_b], graph_type)

    # all_categorical_variables = df.select_dtypes(include=['object']).columns.tolist()
    # all_datetime_variables = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
    # all_numerical_variables = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    # st.write("### 2D Statistics")
    # col1, col2, col3, col4 = st.columns([0.15, 0.25, 0.25, 0.25])
    # with col1:
    #     select_all = st.button("Select All")
    # with col2:
    #     select_all_numerical = st.button("Select All Numerical")
    # with col3:
    #     select_all_categorical = st.button("Select All Categorical")
    # with col4:
    #     select_all_date = st.button("Select All Date")
    #
    # selected_variables = st.multiselect("Select variables", all_variables, key="selected_variables")
    #
    # def overwrite_selected_variables(new_variables):
    #     del st.session_state['selected_variables']
    #     st.session_state['selected_variables'] = new_variables
    #     st.rerun()
    #
    # if select_all:
    #     overwrite_selected_variables(all_variables)
    # elif select_all_numerical:
    #     overwrite_selected_variables(all_numerical_variables)
    # elif select_all_categorical:
    #     overwrite_selected_variables(all_categorical_variables)
    # elif select_all_date:
    #     overwrite_selected_variables(all_datetime_variables)
    #
    # if selected_variables:
    #     stats_df = generate_statistics(df, selected_variables)
    #
    #     st.write("Variable Statistics")
    #     st.write(stats_df)
    #
    #     if st.button("Save Statistics to CSV"):
    #         filename = st.text_input('Enter a filename for the CSV file:', 'data.csv')
    #         csv = convert_df_to_csv(df)
    #         st.download_button(label='Click to download CSV file',
    #                            data=csv, file_name=filename, mime='text/csv')
