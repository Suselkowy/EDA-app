import streamlit as st
import pandas as pd
import plotly.express as px

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
    def change_edited_state(state: bool):
        st.session_state['edited'] = state

    def change_primary_df(df):
        print("primary changed")
        st.session_state['primary_df'] = df

    st.write("Data Wrangling")
    if not st.session_state['edited']:
        print("df changed to primary")
        df = st.session_state['primary_df']
        all_variables = df.columns.tolist()
    else:
        print("df changed to edited")
        df = st.session_state['edited_df']
        all_variables = df.columns.tolist()

    def set_edit(data):
        st.session_state['edited_df'] = data
        df = replace_empty_values(data, selected_variable_fill, method)
        st.session_state['edited'] = True

    def replace_values(df, selected_variable, method):
        df = replace_empty_values(df, selected_variable, method)
        set_edit(df)
        del st.session_state['empty_selected']

    st.data_editor(df)

    st.write(st.session_state['edited'])

    selected_variable = st.selectbox("Select variable to change:", df.columns,
                                     index=None, placeholder="Select variable to change it name",
                                     key='selected_variable')

    if selected_variable:
        changed_value = st.text_input(f"Rename '{selected_variable}' to:", value=selected_variable)
        if changed_value != selected_variable:
            df_editable = df.rename(columns={selected_variable: changed_value})
            change_primary_df(df_editable)
            st.session_state['edited_df'] = df_editable
            st.experimental_rerun()

    selected_variable_fill = st.selectbox(f"Select variable to replace empty", options=all_variables,
                                          index=None, placeholder="Select variable", key="empty_selected")

    if selected_variable_fill is not None:
        empty_values_count = generate_empty(df, selected_variable_fill)
        st.write(f"Number of empty values for {selected_variable_fill}: {empty_values_count}")
        method = st.selectbox("Select method to replace empty values:",
                              ["Mean", "Median", "Most Frequent", "Zero", "Custom Value"], index=None,
                              placeholder="Select method")

        st.button("Replace Empty Values", on_click=replace_values, args=[df, selected_variable_fill, method])

        st.button("Reset", on_click=change_edited_state, args=[False])


