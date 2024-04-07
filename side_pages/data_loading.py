import streamlit as st
import pandas as pd

options = ['int64', 'float64', 'object', 'datetime64[ns]', 'Delete']


def main():
    st.title("CSV File Viewer")
    st.session_state['edited'] = False
    selected_separator = st.selectbox("Select separator:", [',',';'],
                                     index=0, placeholder="Select separator",
                                     key='selected_separator')

    selected_decimal = st.selectbox("Select decimal:", ['.',','],
                                     index=0, placeholder="Select decimal",
                                     key='selected_decimal')

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'main'

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep=selected_separator, decimal=selected_decimal)

        st.write("### Raw Data")
        st.write(df)

        new_df = df.copy()

        for col in df.columns:
            new_dtype = st.selectbox(f"Select data type for column '{col}'", options=options,
                                     index=options.index(f'{df.dtypes[col]}'))
            if new_dtype != df.dtypes[col]:
                if new_dtype != 'Delete':
                    new_df[col] = df[col].astype(new_dtype)
                else:
                    new_df = new_df.drop([col], axis=1)

        def click():
            st.session_state['primary_df'] = new_df
            st.session_state['edited'] = False
            st.session_state['page'] = 'data_manipulation'

        st.button("Go to Data Analysis", on_click=click)
