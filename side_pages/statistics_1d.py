import streamlit as st
import plotly.express as px
import pandas as pd
from utils import scroll_to_top
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


def generate_1d_plots(df, selected_variables):
    for var in selected_variables:
        st.title(var)
        if df[var].dtype == 'object':
            unique_value = df[var].unique()
            if len(unique_value) > 50:
                show_all = st.checkbox("Variable have more than 40 unique values, are you sure, that you want to "
                                       "generate plots ? It can slow the app significantly.", value=False, key=f"checkbox_{var}")
            else:
                show_all = True

            if show_all:
                filtered_df = df
                bar = px.bar(filtered_df[var].value_counts(), x=filtered_df[var].value_counts().index,
                             y=filtered_df[var].value_counts().values,
                             labels={'x': var, 'y': 'Frequency'}, title=f"{var} Bar Chart")
                pie = px.pie(df[var].value_counts(), values=df[var].value_counts().values,
                             names=df[var].value_counts().index,
                             title=f"{var} Pie Chart")
                value_counts = df[var].value_counts().reset_index()
                value_counts.columns = ['value', 'count']
                tree = px.treemap(value_counts, path=['value'], values='count')
                tree.update_layout(title='Treemap of Unique Values Counts in Column')

                col1_1, col2_1 = st.columns(2)
                col1_2, col2_2 = st.columns(2)

                col1_1.plotly_chart(bar, use_container_width=True)
                col2_1.plotly_chart(pie, use_container_width=True)
                col1_2.plotly_chart(tree, use_container_width=True)

        elif df[var].dtype == 'int64' or df[var].dtype == 'float':

            hist = px.histogram(df, x=var, title=f"{var} Histogram")
            box = px.box(df, y=var, title=f"{var} Box Plot")

            col1, col2 = st.columns(2)

            col1.plotly_chart(hist, use_container_width=True)
            col2.plotly_chart(box, use_container_width=True)

        else:
            fig = px.histogram(df, x=var, title=f"{var} Histogram")
            st.plotly_chart(fig)


def statistics_1d_page():
    if not st.session_state['edited']:
        df = st.session_state['primary_df']
    else:
        df = st.session_state['edited_df']
    all_variables = df.columns.tolist()
    all_categorical_variables = df.select_dtypes(include=['object']).columns.tolist()
    all_datetime_variables = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
    all_numerical_variables = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    st.write("### 1D Statistics")
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
        stats_df = generate_statistics(df, selected_variables)

        st.write("Variable Statistics")
        st.write(stats_df)

        if st.button("Save Statistics to CSV"):
            filename = st.text_input('Enter a filename for the CSV file:', 'data.csv')
            csv = convert_df_to_csv(df)
            st.download_button(label='Click to download CSV file',
                               data=csv, file_name=filename, mime='text/csv')

        generate_1d_plots(df, selected_variables)

    if st.session_state['new_page']:
        scroll_to_top()