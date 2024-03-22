import streamlit as st
import plotly as px
import pandas as pd

def generate_statistics(df, selected_variables):
    statistics = {}

    for var in selected_variables:
        if df[var].dtype == 'int64' or df[var].dtype == 'float64':
            statistics[var] = {
                'Mean': df[var].mean(),
                'Median': df[var].median(),
                'Std Dev': df[var].std(),
                'Min': df[var].min(),
                'Max': df[var].max(),
            }
        elif df[var].dtype == 'object':
            statistics[var] = {
                'Unique Values': df[var].nunique(),
                'Most Common Value': df[var].mode()[0],
                'Frequency': df[var].value_counts().max(),
            }
        elif df[var].dtype == 'datetime64[ns]':
            statistics[var] = {
                'Earliest Date': df[var].min(),
                'Latest Date': df[var].max(),
            }

    return pd.DataFrame(statistics).transpose()


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
        print("df changed to primary")
        df = st.session_state['primary_df']
        all_variables = df.columns.tolist()
    else:
        print("df changed to edited")
        df = st.session_state['edited_df']
        all_variables = df.columns.tolist()


    st.write("### 1D Statistics")
    select_all = st.button("Select All")

    if select_all:
        selected_variables = st.multiselect("Select variables", all_variables, default=all_variables)
    else:
        selected_variables = st.multiselect("Select variables", all_variables)

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