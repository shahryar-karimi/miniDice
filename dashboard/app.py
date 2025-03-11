import streamlit as st

from load_items import load_items
DEBUG, STREAMLIT_PASSWORD, session, session_dashboard, llm = load_items()
from pages import data_sheets_page, giveaways_page, graphs_page, histograms_page, wallet_info_page, player_info_page, success_story_page, assets_page


def main():
    if 'auth' not in st.session_state:
        if DEBUG:
            st.session_state.auth = True
            st.rerun()
        else:
            st.session_state.auth = False
            st.rerun()

    if not st.session_state.auth:
        st.title("🔒 Authentication")
        password = st.text_input("🔑 Enter the password", type="password")
        if password == STREAMLIT_PASSWORD:
            st.session_state.auth = True
            st.rerun()
    else:
        st.title("📊 Analytics Dashboard")

        # Sidebar navigation
        if 'page' not in st.session_state:
            st.session_state.page = "Data Sheets"

        page_options = {
            "Data Sheets": lambda: data_sheets_page(session, session_dashboard, DEBUG),
            "Giveaways": lambda: giveaways_page(session),
            "Graphs": lambda: graphs_page(session, session_dashboard, DEBUG),
            "Histograms": lambda: histograms_page(session, session_dashboard, DEBUG),
            "Wallet Information": lambda: wallet_info_page(session),
            "Player Information": lambda: player_info_page(session),
            "Success Story": lambda: success_story_page(session, llm),
            "Assets": lambda: assets_page(session)
        }

        selected_page = st.sidebar.selectbox(
            "Select a Page",
            options=list(page_options.keys()),
            index=list(page_options.keys()).index(st.session_state.page)
        )

        # Update session state and call the selected page function
        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()

        # Call the function for the selected page
        page_options[selected_page]()

if __name__ == "__main__":
    main()