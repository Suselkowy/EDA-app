import streamlit as st
import pandas as pd
import plotly.express as px

options = ['int64', 'float64', 'object', 'datetime64[ns]']

def main():
    st.title("CSV File Viewer")
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
            st.session_state['primary_df'] = new_df
            st.session_state['edited'] = False
            st.session_state['page'] = 'data_manipulation'

        st.button("Go to Data Analysis", on_click=click)

