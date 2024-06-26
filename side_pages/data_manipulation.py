import pandas as pd
import streamlit as st
from utils import scroll_to_top

REPLACE_EMPTY_STRATEGIES = {
    "object": ["Most Frequent", "Custom Value", "Drop Rows"],
    "datetime64[ns]": ["Custom Value", "Drop Rows"],
    "float64": ["Mean", "Median", "Most Frequent", "Zero", "Forward Fill", "Backward Fill", "Interpolation",
                "Custom Value", "Drop Rows"],
    "int64": ["Mean", "Median", "Most Frequent", "Zero", "Forward Fill", "Backward Fill", "Interpolation",
              "Custom Value", "Drop Rows"]
}


def generate_empty(df, selected_variable):
    empty_values_count = df[selected_variable].isnull().sum()
    return empty_values_count


def replace_empty_values(df, selected_variable, method):
    df = df.copy()
    if method == "Most Frequent":
        most_frequent_value = df[selected_variable].mode()[0]
        df[selected_variable].fillna(most_frequent_value,inplace=True)
    if method == "Custom Value":
        df[selected_variable].fillna(st.session_state['custom_value'],inplace=True)
    if method == "Mean":
        df[selected_variable].fillna(df[selected_variable].mean(),inplace=True)
    if method == "Median":
        df[selected_variable].fillna(df[selected_variable].median(),inplace=True)
    if method == "Zero":
        df[selected_variable].fillna(0,inplace=True)
    if method == "Forward Fill":
        df[selected_variable].fillna(method='ffill',inplace=True)
    if method == "Backward Fill":
        df[selected_variable].fillna(method='bfill',inplace=True)
    if method == "Interpolation":
        df[selected_variable].interpolate(inplace=True)
    if method == "Drop Rows":
        df.dropna(subset=[selected_variable],inplace=True)
    return df


def get_missing_values(df):
    missing_values_count = df.isnull().sum()
    missing_values_df = missing_values_count[missing_values_count > 0]
    result_df = pd.DataFrame({'Column Name': missing_values_df.index, 'Missing Values Count': missing_values_df.values})
    return result_df


@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


def data_manipulation_page():
    if "reset_confirmation" not in st.session_state:
        st.session_state['reset_confirmation'] = False

    def change_reset_state(state: bool):
        st.session_state['reset_confirmation'] = state

    def reset_edited_state():
        st.session_state['edited'] = False
        st.session_state['edited_df'] = st.session_state['primary_df']
        change_reset_state(False)
        st.toast("Dataset set to initial values")

    def change_primary_df(df):
        st.session_state['primary_df'] = df

    def change_edited_df(df):
        st.session_state['edited_df'] = df

    def replace_values(df, selected_variable, method):
        edited_df = replace_empty_values(df, selected_variable, method)
        st.session_state['edited_df'] = edited_df
        st.session_state['edited'] = True
        del st.session_state['empty_selected']
        st.session_state['empty_selected'] = None

    st.write("# Data Manipulation")
    if not st.session_state['edited']:
        df = st.session_state['primary_df']
    else:
        df = st.session_state['edited_df']

    all_variables = df.columns.tolist()
    all_variables_with_empty_values = df.columns[df.isnull().any()].tolist()

    st.write(f"### Data preview")
    st.write(df)

    st.write(f"### Change variable name")
    selected_variable = st.selectbox("Select variable to change:", df.columns,
                                     index=None, placeholder="Select variable to change it name",
                                     key='selected_variable')

    if selected_variable:
        changed_value = st.text_input(f"Rename '{selected_variable}' to:", value=selected_variable)
        if changed_value != selected_variable:
            df_editable = df.rename(columns={selected_variable: changed_value})
            change_primary_df(df_editable)
            change_edited_df(df_editable)
            st.rerun()

    st.write(f"### Replace missing data")

    if len(all_variables_with_empty_values) == 0:
        st.write("No columns with missing data")
    else:
        st.write(get_missing_values(df))
        selected_variable_fill = st.selectbox(f"Select variable to replace empty values",
                                              options=all_variables_with_empty_values,
                                              index=None, placeholder="Select variable", key="empty_selected")

        if selected_variable_fill is not None:
            empty_values_count = generate_empty(df, selected_variable_fill)
            st.write(f"Number of empty values for {selected_variable_fill}: {empty_values_count}")

            method = st.selectbox("Select method to replace empty values:",
                                  REPLACE_EMPTY_STRATEGIES[f"{df[selected_variable_fill].dtype}"], index=None,
                                  placeholder="Select method")

            if method != "Custom Value":
                st.button("Replace Empty Values", on_click=replace_values, args=[df, selected_variable_fill, method])
            else:
                custom_value = st.text_input("Enter custom value", key="custom_value")
                if custom_value:
                    replace_values(df, selected_variable_fill, method)
                    st.rerun()

    st.write(f"### Save dataset")
    if st.button('Save DataFrame to CSV' , key="save_all"):
        filename = st.text_input('Enter a filename for the CSV file:', 'data.csv')
        csv = convert_df_to_csv(df)
        st.download_button(label='Click to download CSV file',
                           data=csv, file_name=filename, mime='text/csv', key="download_all")

    st.write(f"### Save dataset with selected columns")
    all_variables = df.columns.tolist()
    all_categorical_variables = df.select_dtypes(include=['object']).columns.tolist()
    all_datetime_variables = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
    all_numerical_variables = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
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

    if st.button('Save DataFrame to CSV', key="save_selected"):
        new_df = df.loc[:, selected_variables]
        filename = st.text_input('Enter a filename for the CSV file:', 'data.csv')
        csv = convert_df_to_csv(new_df)
        st.download_button(label='Click to download CSV file',
                           data=csv, file_name=filename, mime='text/csv', key="download_selected")

    st.write(f"### Reset dataset to initial values")
    if not st.session_state['reset_confirmation']:
        st.button("Reset", on_click=change_reset_state, args=[True])
    else:
        st.error("Are you sure, that you want to reset dataset to initial values?")
        st.button("Proceed", on_click=reset_edited_state)
        st.button("Cancel", on_click=change_reset_state, args=[False])

    if st.session_state['new_page']:
        scroll_to_top()
