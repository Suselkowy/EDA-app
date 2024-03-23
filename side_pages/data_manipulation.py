import streamlit as st


def generate_empty(df, selected_variable):
    empty_values_count = df[selected_variable].isnull().sum()
    return empty_values_count


REPLACE_EMPTY_STRATEGIES = {
    "object": ["Most Frequent", "Custom Value"],
    "datetime64[ns]": ["Custom Value"],
    "numeric": ["Mean", "Median", "Most Frequent", "Zero", "Forward Fill", "Backward Fill", "Interpolation", "Custom Value"]
}


def replace_empty_values(df, selected_variable, method):
    if df[selected_variable].dtype == 'object':
        if method == "Most Frequent":
            most_frequent_value = df[selected_variable].mode()[0]
            df[selected_variable].fillna(most_frequent_value, inplace=True)
        elif method == "Custom Value":
            df[selected_variable].fillna(st.session_state['custom_value'], inplace=True)
    elif df[selected_variable].dtype == 'datetime64[ns]':
        if method == "Custom Value":
            df[selected_variable].fillna(st.session_state['custom_date_value'], inplace=True)
    else:
        if method == "Mean":
            df[selected_variable].fillna(df[selected_variable].mean(), inplace=True)
        elif method == "Median":
            df[selected_variable].fillna(df[selected_variable].median(), inplace=True)
        elif method == "Most Frequent":
            most_frequent_value = df[selected_variable].mode()[0]
            df[selected_variable].fillna(most_frequent_value, inplace=True)
        elif method == "Zero":
            df[selected_variable].fillna(0, inplace=True)
        elif method == "Forward Fill":
            df[selected_variable].fillna(method='ffill', inplace=True)
        elif method == "Backward Fill":
            df[selected_variable].fillna(method='bfill', inplace=True)
        elif method == "Interpolation":
            df[selected_variable].interpolate(inplace=True)
        elif method == "Custom Value":
            df[selected_variable].fillna(st.session_state['custom_value'], inplace=True)
    return df


def data_wrangling():
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
        print("primary changed")
        st.session_state['primary_df'] = df

    def delete_session_variable(session_variable):
        del st.session_state[session_variable]

    st.write("# Data Manipulation")
    if not st.session_state['edited']:
        print("df changed to primary")
        df = st.session_state['primary_df']
        all_variables = df.columns.tolist()
    else:
        print("df changed to edited")
        df = st.session_state['edited_df']
        all_variables = df.columns.tolist()

    def replace_values(df, selected_variable, method):
        new_df = df.copy()
        new_df = replace_empty_values(new_df, selected_variable, method)
        st.session_state['edited_df'] = new_df
        st.session_state['edited'] = True
        del st.session_state['empty_selected']
        st.session_state['empty_selected'] = None

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
            st.session_state['edited_df'] = df_editable
            st.rerun()

    st.write(f"### Replace empty values of variable")
    selected_variable_fill = st.selectbox(f"Select variable to replace empty", options=all_variables,
                                          index=None, placeholder="Select variable", key="empty_selected")

    if selected_variable_fill is not None:
        empty_values_count = generate_empty(df, selected_variable_fill)
        st.write(f"Number of empty values for {selected_variable_fill}: {empty_values_count}")
        if df[selected_variable_fill].dtype == 'object':
            method = st.selectbox("Select method to replace empty values:",
                                  REPLACE_EMPTY_STRATEGIES.get('object'), index=None,
                                  placeholder="Select method")
        elif df[selected_variable_fill].dtype == 'datetime64[ns]':
            method = st.selectbox("Select method to replace empty values:",
                                  REPLACE_EMPTY_STRATEGIES.get('datetime64[ns]'), index=None,
                                  placeholder="Select method")
        else:
            method = st.selectbox("Select method to replace empty values:",
                                  REPLACE_EMPTY_STRATEGIES.get('numeric'), index=None,
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

        df.to_csv(filename, index=False)

        with open(filename, 'rb') as f:
            file_contents = f.read()
        st.download_button(label='Click to download CSV file', data=file_contents, file_name=filename, mime='text/csv')

    st.write(f"### Reset dataset to initial values")
    if not st.session_state['reset_confirmation']:
        st.button("Reset", on_click=change_reset_state, args=[True])
    else:
        st.error("Are you sure, that you want to reset dataset to initial values?")
        st.button("Proceed", on_click=reset_edited_state)
        st.button("Cancel", on_click=change_reset_state, args=[False])
