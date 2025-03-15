import sys
import os

# Add the parent directory to Python path to allow imports from miniDice
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import streamlit.components.v1 as components
from helper_functions import fetch_analyzed_data_grouped_by_date, fetch_winners_grouped_by_date, fetch_data_for_date, plot_graphs, plot_histograms, extract_wallet_information, extract_player_information, success_story, assets_section, player_giveaway, referrer_giveaway, plot_frequent_graphs, fetch_hours_histogram
from datetime import datetime, timedelta

# Page Functions
def data_sheets_page(session, session_dashboard, DEBUG):
    st.title("📄 Data Sheets")
    df_analyzed_data = fetch_analyzed_data_grouped_by_date(session, session_dashboard, DEBUG)
    df_winners_grouped = fetch_winners_grouped_by_date(session)
    st.markdown('---')
    st.write("📋 Analyzed Data")
    st.dataframe(df_analyzed_data.iloc[::-1])
    st.markdown('---')
    st.write("🏆 Winners Data")
    st.dataframe(df_winners_grouped)

def giveaways_page(session):
    st.title("🎁 Giveaways")
    default_date = datetime.today().date() - timedelta(days=1)
    selected_date = st.date_input("Select a date", value=default_date, max_value=datetime.today().date())
    players, referrals = fetch_data_for_date(selected_date, session)
    st.header("Player Giveaway")
    player_giveaway(players, selected_date)
    st.header("Referrer Giveaway")
    referrer_giveaway(referrals, selected_date)

def graphs_page(session, session_dashboard, DEBUG):
    st.title("📈 Graphs")
    df_analyzed_data = fetch_analyzed_data_grouped_by_date(session, session_dashboard, DEBUG)
    plot_graphs(df_analyzed_data)


def histograms_page(session, session_dashboard, DEBUG):
    st.title("📊 Histograms")
    df_analyzed_data = fetch_analyzed_data_grouped_by_date(session, session_dashboard, DEBUG)
    df_hours = fetch_hours_histogram(session)
    plot_histograms(df_analyzed_data, df_hours, session)
    

def wallet_info_page(session):
    st.title("💸 Wallet Information")
    extract_wallet_information(session)

        
        
def player_info_page(session):
    st.title("👨🏻‍💼 Player Information")
    extract_player_information(session)


def success_story_page(session, llm):
    st.title("🎉 Generate a Player Success Story")
    success_story(session, llm)


def assets_page(session):
    st.title("🪙 Assets")
    assets_section(session)
    
    
def frequent_graphs_page(session, session_dashboard, DEBUG):
    st.title("📈 Frequent Graphs")
    df_analyzed_data = fetch_analyzed_data_grouped_by_date(session, session_dashboard, DEBUG)
    plot_frequent_graphs(df_analyzed_data)
    
    
# def test_page():
#     st.title("Test Page")
#     st.image("https://tgstat.ru/channel/@dicemaniacs/stat-widget.png")

# def tgstat_analytics_page(session, TGSTAT_APIKEY):
#     st.title("🔍 TGStat Analytics")
#     client = TGStatClient(TGSTAT_APIKEY)
#     plot_tgstat_channel_info(client, "dicemaniacs")
#     plot_tgstat_channel_stats(client, "dicemaniacs")
#     plot_tgstat_subscribers_growth(client, "dicemaniacs")
#     plot_tgstat_views_by_hours(client, "dicemaniacs")
#     plot_tgstat_audience_geography(client, "dicemaniacs")
    
    