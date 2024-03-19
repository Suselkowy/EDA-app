import streamlit as st
import pandas as pd
import plotly.express as px


def main():
    st.title("CSV File Viewer")
    options = ['int64', 'float64', 'object', 'datetime64[ns]']
    st.session_state['edited'] = False
    # Upload CSV file
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'main'

    if uploaded_file is not None:
        # Load CSV data into a DataFrame
        df = pd.read_csv(uploaded_file)

        # Display DataFrame
        st.write("### Raw Data")
        st.write(df)

        new_df = df

        for col in df.columns:
            new_dtype = st.selectbox(f"Select data type for column '{col}'", options=options,
                                     index=options.index(f'{df.dtypes[col]}'))
            if new_dtype != df.dtypes[col]:
                new_df[col] = df[col].astype(new_dtype)

        def click():
            st.session_state['current_page'] = 'data_wrangling'
            st.session_state['current_df'] = new_df

        st.button("Go to Data Analysis", on_click=click)



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


def generate_empty(df, selected_variable):
    empty_values_count = df[selected_variable].isnull().sum()
    return empty_values_count


def replace_empty_values(df, selected_variable, method):
    if method == "Mean":
        df[selected_variable].fillna(df[selected_variable].mean(), inplace=True)
    elif method == "Median":
        df[selected_variable].fillna(df[selected_variable].median(), inplace=True)
    elif method == "Most Frequent":
        most_frequent_value = df[selected_variable].mode()[0]
        df[selected_variable].fillna(most_frequent_value, inplace=True)
    elif method == "Zero":
        df[selected_variable].fillna(0, inplace=True)
    elif method == "Custom Value":
        custom_value = st.text_input("Enter custom value:")
        if st.button("Replace with Custom Value"):
            df[selected_variable].fillna(custom_value, inplace=True)
    return df


def data_wrangling():
    st.write("Data Wrangling")
    if not st.session_state['edited']:
        df = st.session_state['current_df']
    else:
        df = st.session_state['edited_df']

    all_variables = df.columns.tolist()

    selected_variable = st.selectbox("Select variable to change:", df.columns,
                                     index=None, placeholder="Select variable to change it name")

    if selected_variable:
        changed_value = st.text_input(f"Rename '{selected_variable}' to:", value=selected_variable)
        if changed_value != selected_variable:
            df_editable = df.rename(columns={selected_variable: changed_value})
            st.session_state['edited'] = True
            st.session_state['edited_df'] = df_editable
            df = df_editable
            all_variables = df.columns.tolist()


    selected_variable_fill = st.selectbox(f"Select variable to replace empty", options=all_variables,
                                          index=None, placeholder="Select variable")

    if selected_variable_fill is not None:
        # Display number of empty values for selected variable
        empty_values_count = generate_empty(df, selected_variable_fill)
        st.write(f"Number of empty values for {selected_variable_fill}: {empty_values_count}")
        method = st.selectbox("Select method to replace empty values:",
                              ["Mean", "Median", "Most Frequent", "Zero", "Custom Value"], index=None,
                              placeholder="Select method")

        if method != "Custom Value":
            if st.button("Replace Empty Values"):
                df = replace_empty_values(df, selected_variable_fill, method)
                st.write("### Data after replacing empty values")
                st.write(df.head())

        else:
            df = replace_empty_values(df, selected_variable_fill, method)

            # Save updated DataFrame
        if st.button("Save Updated Data"):
            with st.spinner("Saving updated data to CSV..."):
                df.to_csv("updated_data.csv", index=False)
            st.success("Updated data saved successfully!")

            # Reset button to reset all variables to primary values
        if st.button("Reset"):
            df = st.session_state['edited_df']

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


if __name__ == "__main__":
    if 'current_page' not in st.session_state or st.session_state['current_page'] != 'data_wrangling':
        main()
    else:
        data_wrangling()
