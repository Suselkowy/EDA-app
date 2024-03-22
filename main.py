import streamlit as st
from side_pages.data_loading import main
from side_pages.data_manipulation import data_wrangling
from side_pages.statistics import statistics
from st_pages import show_pages, hide_pages, Page

if "page" not in st.session_state:
    st.session_state['page'] = "loading"

show_pages(
    [
        Page("main.py", "Loading"),
    ]
)


def switch_page(page: str):
    st.session_state['page'] = page


if st.session_state['page'] == "loading":
    main()
elif st.session_state['page'] == "data_manipulation":
    side_bar = st.sidebar
    side_bar.button("Data Manipulation", on_click=switch_page, args=["data_manipulation"])
    side_bar.button("Statistics", on_click=switch_page, args=["statistics"])
    data_wrangling()
elif st.session_state['page'] == "statistics":
    side_bar = st.sidebar
    side_bar.button("Data Manipulation", on_click=switch_page, args=["data_manipulation"])
    side_bar.button("Statistics", on_click=switch_page, args=["statistics"])
    statistics()
