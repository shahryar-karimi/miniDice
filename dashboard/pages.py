import sys
import os

# Add the parent directory to Python path to allow imports from miniDice
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import streamlit.components.v1 as components
from helper_functions import fetch_analyzed_data_grouped_by_date, fetch_winners_grouped_by_date, fetch_data_for_date, plot_graphs, plot_histograms, extract_wallet_information, extract_player_information, success_story, assets_section, player_giveaway, referrer_giveaway, plot_frequent_graphs, fetch_hours_histogram, fetch_top_players, fetch_wallet_based_points
from tgstat_helper_functions import plot_tgstat_channel_info, plot_tgstat_channel_stats, plot_tgstat_subscribers_growth, get_channel_posts_with_dates, compare_stats_between_posts
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pandas as pd
import string
from sqlalchemy import func, case, text, distinct
from models import Player

# Page Functions
def data_sheets_page(session, session_dashboard, DEBUG):
    st.title("📄 Data Sheets")
    df_analyzed_data = fetch_analyzed_data_grouped_by_date(session, session_dashboard, DEBUG)
    df_winners_grouped = fetch_winners_grouped_by_date(session)
    
    tab1, tab2 = st.tabs([
        "📋 Analyzed Data",
        "🏆 Winners Data"
    ])
    
    with tab1:
        st.write("📋 Analyzed Data")
        st.dataframe(df_analyzed_data.iloc[::-1])
    
    with tab2:
        st.write("🏆 Winners Data")
        st.dataframe(df_winners_grouped)

def giveaways_page(session):
    st.title("🎁 Giveaways")
    default_date = datetime.today().date() - timedelta(days=1)
    selected_date = st.date_input("Select a date", value=default_date, max_value=datetime.today().date())
    
    tab1, tab2 = st.tabs(["🎮 Player Giveaway", "🤝 Referrer Giveaway"])
    
    with tab1:
        st.write("🎰 **20$ Prize**")
        players, _ = fetch_data_for_date(selected_date, session)
        player_giveaway(players, selected_date)
    
    with tab2:
        st.write("🎁 **30$ Prize**")
        _, referrals = fetch_data_for_date(selected_date, session)
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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Search Players",
        "📝 Check Wallet List",
        "🔄 Map Wallets to Unique IDs",
        "📊 Wallet Address Analysis",
        "💰 Wallet-Based Points"
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
                
                # Use Streamlit's native clipboard solution
                st.text_area(
                    "Copy these IDs",
                    value=telegram_ids_text,
                    height=100,
                    key="copy_telegram_ids"
                )
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

    with tab5:
        st.write("💰 Wallet-Based Points Analysis")
        st.write("This tab shows the maximum points assigned to each unique wallet based on the highest points among connected players.")
        
        # Fetch wallet-based points data
        df_wallet_points = fetch_wallet_based_points(session)
        
        # Add metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Unique Wallets", len(df_wallet_points))
        with col2:
            st.metric("Total Assigned Points", df_wallet_points['assigned_points'].sum())
        with col3:
            st.metric("Average Points per Wallet", round(df_wallet_points['assigned_points'].mean(), 2))
        
        # Display the dataframe
        st.write("📊 Wallet Points Data")
        st.dataframe(df_wallet_points)
        
        # Create a histogram of points distribution
        fig = go.Figure(data=[
            go.Histogram(
                x=df_wallet_points['assigned_points'],
                nbinsx=50,
                marker_color='#1f77b4',
                opacity=0.75
            )
        ])
        
        fig.update_layout(
            title="Distribution of Wallet Points",
            xaxis_title="Points",
            yaxis_title="Number of Wallets",
            template="plotly_dark"
        )
        
        st.plotly_chart(fig)

def tgstat_analytics_page(client, channel="dicemaniacs"):
    st.title("📊 TGStat Channel Analytics")
    
    # Allow custom channel input
    custom_channel = st.text_input("Enter channel username (without @)", value=channel)
    
    if custom_channel:
        channel = custom_channel.strip().replace("@", "")
        
        # Create tabs for different analytics views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Channel Overview",
            "🔍 Channel Subcribers",
            "🔍 Post Analysis",
            "📊 Posts Comparison"
        ])
        
        with tab1:
            st.subheader("Channel Overview")
            plot_tgstat_channel_info(client, channel)
            plot_tgstat_channel_stats(client, channel)
            
        with tab2:
            st.subheader("Channel Subscribers")
            plot_tgstat_subscribers_growth(client, channel)
            
        with tab3:
            st.subheader("Post Analysis")
            
            # Get recent posts for selection
            posts = get_channel_posts_with_dates(client, channel, limit=50)
            
            if posts:
                # Format post options for dropdown
                post_options = [f"{post['date']} - {post['summary']}" for post in posts]
                
                # Display post selection dropdown
                selected_post_idx = st.selectbox(
                    "Select a post to analyze",
                    options=range(len(post_options)),
                    format_func=lambda i: post_options[i]
                )
                
                selected_post = posts[selected_post_idx]
                
                # Display selected post details
                st.write("### Selected Post Details")
                st.write(f"**Date:** {selected_post['date']}")
                st.write(f"**ID:** {selected_post['id']}")
                
                # Display post content
                if 'text' in selected_post['full_post']:
                    st.write("**Content:**")
                    st.markdown(selected_post['full_post']['text'], unsafe_allow_html=True)
                
                # Display post stats
                if 'views' in selected_post['full_post']:
                    st.metric("Views", selected_post['full_post']['views'])
                
                try:
                    # Get post statistics
                    post_stats = client.get_post_stats(selected_post['id'])
                    
                    if 'status' in post_stats and post_stats['status'] == 'ok' and 'response' in post_stats:
                        stats = post_stats['response']
                        
                        # Display stats metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if 'forwards_count' in stats:
                                st.metric("Forwards", stats['forwards_count'])
                        
                        with col2:
                            if 'mentions_count' in stats:
                                st.metric("Mentions", stats['mentions_count'])
                                
                        with col3:
                            if 'views_per_subscriber' in stats:
                                st.metric("Views per Subscriber", f"{stats['views_per_subscriber']:.2f}")
                                
                        with col4:
                            if 'reach_per_post' in stats:
                                st.metric("Reach per Post", stats['reach_per_post'])
                except Exception as e:
                    st.error(f"Error fetching post stats: {str(e)}")
            else:
                st.warning("No posts found for this channel")
        
        with tab4:
            pass
            
    #         st.subheader("Compare Statistics Between Posts")
            
    #         # Get recent posts for selection
    #         posts = get_channel_posts_with_dates(client, channel, limit=50)
            
    #         if posts:
    #             # Format post options for dropdown
    #             post_options = [f"{post['date']} - {post['summary']}" for post in posts]
                
    #             # Create two columns for post selection
    #             col1, col2 = st.columns(2)
                
    #             with col1:
    #                 st.write("### Select Starting Post")
    #                 start_post_idx = st.selectbox(
    #                     "Choose first post",
    #                     options=range(len(post_options)),
    #                     format_func=lambda i: post_options[i],
    #                     key="start_post"
    #                 )
                
    #             with col2:
    #                 st.write("### Select Ending Post")
    #                 # Default to a post that's a week later than the start post if possible
    #                 default_end_idx = min(start_post_idx + 7, len(posts) - 1)
    #                 end_post_idx = st.selectbox(
    #                     "Choose second post",
    #                     options=range(len(post_options)),
    #                     index=default_end_idx,
    #                     format_func=lambda i: post_options[i],
    #                     key="end_post"
    #                 )
                
    #             start_post = posts[start_post_idx]
    #             end_post = posts[end_post_idx]
                
    #             if st.button("📊 Compare Statistics"):
    #                 compare_stats_between_posts(client, channel, start_post['id'], end_post['id'])
    #         else:
    #             st.warning("No posts found for this channel")
    # else:
    #     st.warning("Please enter a valid channel username to analyze")

    