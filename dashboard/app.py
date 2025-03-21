import streamlit as st
from load_items import load_items
DEBUG, STREAMLIT_PASSWORD, TGSTAT_APIKEY, session, session_dashboard, llm = load_items()
from pages import (
    data_sheets_page,
    giveaways_page,
    graphs_page,
    histograms_page,
    wallet_info_page,
    player_info_page,
    success_story_page,
    assets_page,
    frequent_graphs_page,
    top_players_page,
    tgstat_analytics_page
)
from .tgstat_client import TGStatClient


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

        # Initialize TGStat client
        tgstat_client = TGStatClient(TGSTAT_APIKEY)

        # Sidebar navigation
        if 'page' not in st.session_state:
            st.session_state.page = "Frequent Graphs"

        page_options = {
            "Frequent Graphs": lambda: frequent_graphs_page(session, session_dashboard, DEBUG),
            "Data Sheets": lambda: data_sheets_page(session, session_dashboard, DEBUG),
            "Giveaways": lambda: giveaways_page(session),
            "Graphs": lambda: graphs_page(session, session_dashboard, DEBUG),
            "Histograms": lambda: histograms_page(session, session_dashboard, DEBUG),
            "Wallet Information": lambda: wallet_info_page(session),
            "Player Information": lambda: player_info_page(session),
            "Success Story": lambda: success_story_page(session, llm),
            "Assets": lambda: assets_page(session),
            "Top Players": lambda: top_players_page(session),
            "TGStat Analytics": lambda: tgstat_analytics_page(tgstat_client),
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