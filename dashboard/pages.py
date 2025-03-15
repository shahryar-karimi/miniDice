import sys
import os

# Add the parent directory to Python path to allow imports from miniDice
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import streamlit.components.v1 as components
from helper_functions import fetch_analyzed_data_grouped_by_date, fetch_winners_grouped_by_date, fetch_data_for_date, plot_graphs, plot_histograms, extract_wallet_information, extract_player_information, success_story, assets_section, player_giveaway, referrer_giveaway, plot_frequent_graphs, fetch_hours_histogram, fetch_top_players
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pandas as pd
import string
from sqlalchemy import func, case, text, distinct
from models import Player
import pyperclip

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
    
    
def top_players_page(session):
    st.title("🏆 Top Players")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Search Players",
        "📝 Check Wallet List",
        "🔄 Map Wallets to Unique IDs",
        "📊 Wallet Address Analysis"
    ])
    
    with tab1:
        # Search interface
        col1, col2 = st.columns(2)
        with col1:
            search_type = st.selectbox(
                "Search by",
                options=["None", "Username", "Wallet Address"],
                key="search_type"
            )
        
        with col2:
            search_term = st.text_input(
                "Search term",
                key="search_term",
                disabled=(search_type == "None")
            )
        
        # Convert search type to query parameter
        search_type_param = None
        if search_type == "Username":
            search_type_param = "username"
        elif search_type == "Wallet Address":
            search_type_param = "wallet"
        
        # Fetch data with search parameters
        df_top_players = fetch_top_players(
            session,
            search_term=search_term if search_type != "None" else None,
            search_type=search_type_param
        )
        
        if df_top_players.empty:
            st.warning("No players found matching your search criteria.")
            return
        
        st.write(f"📊 {'Top 100 ' if search_type == 'None' else 'Found '}Players by Points")
        
        # Add metrics for total stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Players", len(df_top_players))
        with col2:
            st.metric("Total Wins", df_top_players['wins'].sum())
        with col3:
            st.metric("Total Predictions", df_top_players['predictions'].sum())
        with col4:
            st.metric("Total Referrals", df_top_players['referrals'].sum())
        
        # Display the dataframe
        st.dataframe(df_top_players)
        
        # Only show chart if we have data
        if not df_top_players.empty:
            # Create a bar chart for the top 20 players
            df_top_20 = df_top_players.head(20)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=df_top_20['telegram_username'].fillna(df_top_20['telegram_id'].astype(str)),
                    y=df_top_20['points'],
                    text=df_top_20['points'],
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title=f"{'Top 20' if len(df_top_20) == 20 else 'Found'} Players by Points",
                xaxis_title="Player",
                yaxis_title="Points",
                template="plotly_dark"
            )
            
            st.plotly_chart(fig)
    
    with tab2:
        st.write("📝 Check Wallet Addresses Against Top 100 Players")
        wallet_list = st.text_area(
            "Enter wallet addresses (one per line)",
            height=200,
            help="Enter each wallet address on a new line. All punctuation and whitespace will be removed.",
            key="check_top_100_wallet_list"
        )
        
        if wallet_list:
            # Process and clean the wallet list
            wallet_addresses = []
            for addr in wallet_list.split('\n'):
                # Remove all punctuation and whitespace
                cleaned_addr = addr.translate(str.maketrans('', '', string.punctuation)).replace(' ', '').strip()
                if cleaned_addr:  # Only add non-empty addresses
                    wallet_addresses.append(cleaned_addr)
            
            # Get top 100 players and clean their wallet addresses
            df_top_100 = fetch_top_players(session)
            # Clean the wallet addresses in df_top_100
            df_top_100['clean_wallet'] = df_top_100['wallet_address'].fillna('').apply(
                lambda x: x.translate(str.maketrans('', '', string.punctuation)).replace(' ', '').lower()
            )
            top_100_wallets = set(df_top_100['clean_wallet'].dropna())
            
            # Check matches
            matches = []
            for addr in wallet_addresses:
                if addr.lower() in top_100_wallets:
                    player_data = df_top_100[df_top_100['clean_wallet'] == addr.lower()].iloc[0]
                    matches.append({
                        'wallet_address': player_data['wallet_address'],  # Show original wallet address
                        'input_wallet': addr,  # Show user's input
                        'rank': df_top_100[df_top_100['clean_wallet'] == addr.lower()].index[0] + 1,
                        'points': player_data['points'],
                        'username': player_data['telegram_username'] or str(player_data['telegram_id'])
                    })
            
            # Display results
            total_valid_addresses = len(wallet_addresses)
            st.write(f"Found {len(matches)} matches out of {total_valid_addresses} valid addresses")
            
            if matches:
                matches_df = pd.DataFrame(matches)
                st.dataframe(matches_df.sort_values('rank'))
                
                # Create pie chart showing ratio
                fig = go.Figure(data=[go.Pie(
                    labels=['In Top 100', 'Not in Top 100'],
                    values=[len(matches), total_valid_addresses - len(matches)],
                    hole=.3
                )])
                
                fig.update_layout(
                    title="Ratio of Addresses in Top 100",
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig)
    
    with tab3:
        st.write("🔄 Map Wallet Addresses to Telegram IDs")
        st.write("This tool will find all Telegram IDs associated with the input wallet addresses.")
        
        wallet_list = st.text_area(
            "Enter wallet addresses (one per line)",
            height=200,
            help="Enter each wallet address on a new line. All punctuation and whitespace will be removed.",
            key="map_wallet_list"
        )
        
        if wallet_list:
            # Process and clean the wallet list
            wallet_addresses = []
            for addr in wallet_list.split('\n'):
                # Remove all punctuation and whitespace
                cleaned_addr = addr.translate(str.maketrans('', '', string.punctuation)).replace(' ', '').strip()
                if cleaned_addr:  # Only add non-empty addresses
                    wallet_addresses.append(cleaned_addr)
            
            if not wallet_addresses:
                st.warning("No valid wallet addresses provided.")
                return
            
            # Query all players with these wallet addresses
            telegram_ids = []
            
            for wallet in wallet_addresses:
                # Query all players with this wallet address
                players = session.query(Player).filter(
                    func.lower(Player.wallet_address).contains(wallet.lower())
                ).all()
                
                if players:
                    for player in players:
                        telegram_ids.append({
                            'telegram_id': player.telegram_id,
                            'telegram_username': player.telegram_username,
                            'first_name': player.first_name,
                            'wallet_address': player.wallet_address,
                            'input_wallet': wallet
                        })
            
            if telegram_ids:
                # Create DataFrame
                df_results = pd.DataFrame(telegram_ids)
                
                # Add metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Input Wallets", len(wallet_addresses))
                with col2:
                    st.metric("Total Telegram IDs Found", len(df_results))
                
                # Show results
                st.write("📊 All Telegram IDs Found")
                st.dataframe(df_results)
                
                # Create a text string with just the Telegram IDs
                unique_ids = sorted(list(set(df_results['telegram_id'].tolist())))
                telegram_ids_text = '\n'.join(map(str, unique_ids))
                
                st.write("📋 List of Unique Telegram IDs")
                st.code(telegram_ids_text, language='text')
                
                # Add copy button for Telegram IDs
                if st.button("Copy Telegram IDs"):
                    pyperclip.copy(telegram_ids_text)
                    st.toast("Telegram IDs copied to clipboard!")
            else:
                st.warning("No matches found for any of the provided wallet addresses.")
    
    with tab4:
        st.write("📊 Analyze Wallet Address Frequencies")
        st.write("This tool will count how many times each wallet address appears in your input list.")
        
        wallet_list = st.text_area(
            "Enter wallet addresses (one per line)",
            height=200,
            help="Enter each wallet address on a new line. All punctuation and whitespace will be removed.",
            key="analyze_wallet_list"
        )
        
        if wallet_list:
            # Process and clean the wallet list
            wallet_addresses = []
            for addr in wallet_list.split('\n'):
                # Remove all punctuation and whitespace
                cleaned_addr = addr.translate(str.maketrans('', '', string.punctuation)).replace(' ', '').strip()
                if cleaned_addr:  # Only add non-empty addresses
                    wallet_addresses.append(cleaned_addr.lower())  # Convert to lowercase for consistent counting
            
            if not wallet_addresses:
                st.warning("No valid wallet addresses provided.")
                return
            
            # Create frequency DataFrame
            frequency_dict = {}
            for addr in wallet_addresses:
                frequency_dict[addr] = frequency_dict.get(addr, 0) + 1
            
            # Convert to DataFrame
            df_frequency = pd.DataFrame({
                'wallet_address': list(frequency_dict.keys()),
                'occurrences': list(frequency_dict.values())
            }).sort_values('occurrences', ascending=False)
            
            # Add metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Entries", len(wallet_addresses))
            with col2:
                st.metric("Unique Addresses", len(df_frequency))
            with col3:
                st.metric("Duplicate Rate", f"{(1 - len(df_frequency)/len(wallet_addresses))*100:.1f}%")
            
            # Show results
            st.write("📊 Frequency Analysis")
            st.dataframe(df_frequency)
            
            # Create a histogram of frequencies
            fig = go.Figure(data=[
                go.Bar(
                    x=df_frequency['occurrences'].value_counts().index,
                    y=df_frequency['occurrences'].value_counts().values,
                    text=df_frequency['occurrences'].value_counts().values,
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title="Distribution of Wallet Address Frequencies",
                xaxis_title="Number of Occurrences",
                yaxis_title="Count of Wallet Addresses",
                template="plotly_dark"
            )
            
            st.plotly_chart(fig)
            
            # Show addresses that appear multiple times
            multiple_occurrences = df_frequency[df_frequency['occurrences'] > 1]
            if not multiple_occurrences.empty:
                st.write("⚠️ Addresses that appear multiple times:")
                st.dataframe(multiple_occurrences)

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
    
    