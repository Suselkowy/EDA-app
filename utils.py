import streamlit as st


def scroll_to_top():
    js = '''
    <div style="display: none">
    <script>
        var body = window.parent.document.querySelector(".main");
        body.scrollTop = 0;
    </script>
    </div>
    '''
    st.components.v1.html(js, height=0)
    st.session_state['new_page'] = False
