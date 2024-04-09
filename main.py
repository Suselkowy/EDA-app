import streamlit as st
from side_pages.data_loading import main
from side_pages.data_manipulation import data_manipulation_page
from side_pages.statistics_1d import statistics_1d_page
from side_pages.statistics_2d import statistics_2d_page
from st_pages import show_pages, Page

if "page" not in st.session_state:
    st.session_state['page'] = "loading"

st.set_page_config(layout="wide")

show_pages(
    [
        Page("main.py", "Loading"),
    ]
)


def show_side_panel():
    side_bar = st.sidebar
    side_bar.button("Data Manipulation", on_click=switch_page, args=("data_manipulation",))
    side_bar.button("Statistics 1d", on_click=switch_page, args=("statistics_1d",))
    side_bar.button("Statistics 2d", on_click=switch_page, args=("statistics_2d",))


def switch_page(page: str):
    st.session_state['page'] = page
    st.session_state['new_page'] = True


if st.session_state['page'] == "loading":
    main()
elif st.session_state['page'] == "data_manipulation":
    show_side_panel()
    data_manipulation_page()
elif st.session_state['page'] == "statistics_1d":
    show_side_panel()
    statistics_1d_page()
elif st.session_state['page'] == "statistics_2d":
    show_side_panel()
    statistics_2d_page()
