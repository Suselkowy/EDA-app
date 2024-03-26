import streamlit as st
import plotly.express as px
import pandas as pd


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


def generate_1d_plots(df, selected_variables, graph_type):
    for var in selected_variables:
        st.write(f"### {var} Distribution")
        if graph_type == 'Histogram':
            if df[var].dtype == 'int64' or df[var].dtype == 'float64':
                fig = px.histogram(df, x=var, title=f"{var} Histogram")
                st.plotly_chart(fig)
            elif df[var].dtype == 'datetime64[ns]':
                fig = px.histogram(df, x=var, title=f"{var} Histogram")
                st.plotly_chart(fig)
        elif graph_type == 'Bar Chart':
            if df[var].dtype == 'object':
                fig = px.bar(df[var].value_counts(), x=df[var].value_counts().index, y=df[var].value_counts().values,
                             labels={'x': var, 'y': 'Frequency'}, title=f"{var} Bar Chart")
                st.plotly_chart(fig)
        elif graph_type == 'Box Plot':
            if df[var].dtype == 'int64' or df[var].dtype == 'float64':
                fig = px.box(df, y=var, title=f"{var} Box Plot")
                st.plotly_chart(fig)
        elif graph_type == 'Pie Chart':
            if df[var].dtype == 'object':
                fig = px.pie(df[var].value_counts(), values=df[var].value_counts().values,
                             names=df[var].value_counts().index,
                             title=f"{var} Pie Chart")
                st.plotly_chart(fig)


def statistics():
    if not st.session_state['edited']:
        df = st.session_state['primary_df']
    else:
        print("df changed to edited")
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

    if select_all:
        del st.session_state['selected_variables']
        st.session_state['selected_variables'] = all_variables
        st.rerun()
    elif select_all_numerical:
        del st.session_state['selected_variables']
        st.session_state['selected_variables'] = all_numerical_variables
        st.rerun()
    elif select_all_categorical:
        del st.session_state['selected_variables']
        st.session_state['selected_variables'] = all_categorical_variables
        st.rerun()
    elif select_all_date:
        del st.session_state['selected_variables']
        st.session_state['selected_variables'] = all_datetime_variables
        st.rerun()

    if selected_variables:
        # Generate statistics
        stats_df = generate_statistics(df, selected_variables)

        # Display statistics
        st.write("Variable Statistics")
        st.write(stats_df)

        if st.button("Save Statistics to CSV"):
            with st.spinner("Saving statistics to CSV..."):
                stats_df.to_csv("statistics.csv", index=True)
            st.success("Statistics saved successfully!")

    st.write("### 1D plots")

    selected_variable_plot = st.selectbox(f"Select variable which plot you want to generate", options=all_variables,
                                          index=None, placeholder='Select plot')

    if selected_variable_plot:
        graph_type = st.selectbox("Select graph type", ["Histogram", "Bar Chart", "Box Plot", "Pie Chart"])
        generate_1d_plots(df, [selected_variable_plot], graph_type)
