import pandas as pd
import streamlit as st

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
    if method == "Most Frequent":
        most_frequent_value = df[selected_variable].mode()[0]
        return df[selected_variable].fillna(most_frequent_value)
    if method == "Custom Value":
        return df[selected_variable].fillna(st.session_state['custom_value'])
    if method == "Mean":
        return df[selected_variable].fillna(df[selected_variable].mean())
    if method == "Median":
        return df[selected_variable].fillna(df[selected_variable].median())
    if method == "Most Frequent":
        most_frequent_value = df[selected_variable].mode()[0]
        return df[selected_variable].fillna(most_frequent_value)
    if method == "Zero":
        return df[selected_variable].fillna(0)
    if method == "Forward Fill":
        return df[selected_variable].fillna(method='ffill')
    if method == "Backward Fill":
        return df[selected_variable].fillna(method='bfill')
    if method == "Interpolation":
        return df[selected_variable].interpolate()
    if method == "Drop Rows":
        return df.dropna(subset=[selected_variable])
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
    if st.button('Save DataFrame to CSV'):
        filename = st.text_input('Enter a filename for the CSV file:', 'data.csv')
        csv = convert_df_to_csv(df)
        st.download_button(label='Click to download CSV file',
                           data=csv, file_name=filename, mime='text/csv')

    st.write(f"### Reset dataset to initial values")
    if not st.session_state['reset_confirmation']:
        st.button("Reset", on_click=change_reset_state, args=[True])
    else:
        st.error("Are you sure, that you want to reset dataset to initial values?")
        st.button("Proceed", on_click=reset_edited_state)
        st.button("Cancel", on_click=change_reset_state, args=[False])
