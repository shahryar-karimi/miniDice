import pandas as pd
import numpy as np
from models import Player, Prediction, Report, UserReferral, Asset
from sqlalchemy import distinct, case, desc, func
import streamlit as st
import sympy as sp
import random
import plotly.graph_objects as go


# Helper function to fetch data from the database
def fetch_data(query, session):
    return pd.read_sql(query.statement, session.bind)


def update_report_table(df_analyzed_data, session_dashboard):
    for index, row in df_analyzed_data.iterrows():
        if row['insert_d'] == 'Total':
            continue

        # Calculate averages and convert NumPy types to native Python types
        average_joined_players = float(df_analyzed_data['joined_players_count'].mean()) if not np.isnan(df_analyzed_data['joined_players_count'].mean()) else None
        average_connected_wallets = float(df_analyzed_data['count_wallets'].mean()) if not np.isnan(df_analyzed_data['count_wallets'].mean()) else None

        # Convert row values to native Python types and handle NaN
        joined_players = int(row['joined_players_count']) if pd.notna(row['joined_players_count']) else None
        connected_wallets = int(row['count_wallets']) if pd.notna(row['count_wallets']) else None
        referrals = int(row['count_referrals']) if pd.notna(row['count_referrals']) else None
        winners = int(row['winners_count']) if pd.notna(row['winners_count']) else None
        unique_players = int(row['unique_players_count']) if pd.notna(row['unique_players_count']) else None
        players_noref_wallet_connected = int(row['count_joined_player_noref_wallet']) if pd.notna(row['count_joined_player_noref_wallet']) else None
        unique_wallets_predictions = int(row['unique_wallets_predictions_count']) if pd.notna(row['unique_wallets_predictions_count']) else None
        players_joined_without_referral = int(row['joined_without_referral']) if pd.notna(row['joined_without_referral']) else None
        new_wallets_count = int(row['new_wallets_count']) if pd.notna(row['new_wallets_count']) else None

        # Use no_autoflush to prevent premature flushing
        with session_dashboard.no_autoflush:
            report_entry = session_dashboard.query(Report).filter(Report.date == row['insert_d']).first()
            if report_entry:
                report_entry.joined_players = joined_players
                report_entry.average_joined_players = average_joined_players
                report_entry.connected_wallets = connected_wallets
                report_entry.average_connected_wallets = average_connected_wallets
                report_entry.referrals = referrals
                report_entry.winners = winners
                report_entry.unique_players = unique_players
                report_entry.players_noref_wallet_connected = players_noref_wallet_connected
                report_entry.unique_wallets_predictions = unique_wallets_predictions
                report_entry.players_joined_without_referral = players_joined_without_referral
                report_entry.new_wallets_count = new_wallets_count
            else:
                new_report_entry = Report(
                    date=row['insert_d'],
                    joined_players=joined_players,
                    average_joined_players=average_joined_players,
                    connected_wallets=connected_wallets,
                    average_connected_wallets=average_connected_wallets,
                    referrals=referrals,
                    winners=winners,
                    unique_players=unique_players,
                    players_noref_wallet_connected=players_noref_wallet_connected,
                    unique_wallets_predictions=unique_wallets_predictions,
                    players_joined_without_referral=players_joined_without_referral,
                    new_wallets_count=new_wallets_count
                )
                session_dashboard.add(new_report_entry)

    session_dashboard.commit()
    
# Fetch analyzed data grouped by date
def fetch_analyzed_data_grouped_by_date(session, session_dashboard, DEBUG):
    
    # Query for players joined grouped by date
    players_joined_query = session.query(
        func.date(Player.insert_dt).label('insert_d'),
        func.count(Player.telegram_id).label('joined_players_count')
    ).group_by(func.date(Player.insert_dt)).subquery()

    # Query for players with wallet addresses grouped by date
    players_wallet_query = session.query(
        func.date(Player.wallet_insert_dt).label('insert_d'),
        func.count(Player.telegram_id).label('count_wallets')
    ).filter(Player.wallet_address.isnot(None)) \
     .group_by(func.date(Player.wallet_insert_dt)).subquery()

    # Query for referrals grouped by date
    referrals_query = session.query(
        func.date(UserReferral.insert_dt).label('insert_d'),
        func.count(UserReferral.id).label('count_referrals')
    ).group_by(func.date(UserReferral.insert_dt)).subquery()

    # Query for predictions grouped by date
    predictions_query = session.query(
        func.date(Prediction.insert_dt).label('insert_d'),
        func.sum(case((Prediction.is_win == True, 1), else_=0)).label('winners_count'),
        func.count(func.distinct(Prediction.player_id)).label('unique_players_count'),
        func.count(Prediction.id).label('predictions_count')
    ).group_by(func.date(Prediction.insert_dt)).subquery()

    # Query for players who joined without referrals and connected wallet
    players_noref_wallet_query = session.query(
        func.date(Player.wallet_insert_dt).label('insert_d'),
        func.count(Player.telegram_id).label('count_joined_player_noref_wallet')
    ).filter(
        Player.wallet_address.isnot(None),
        ~Player.telegram_id.in_(
            session.query(UserReferral.referee_id).distinct()
        )
    ).group_by(func.date(Player.wallet_insert_dt)).subquery()

    
    unique_wallet_predicion_query = session.query(
    func.date(Prediction.insert_dt).label('insert_d'),
    func.count(func.distinct(Player.wallet_address)).label('unique_wallets_predictions_count')
    ).join(Player, Prediction.player_id == Player.telegram_id) \
    .filter(Player.wallet_address.isnot(None)) \
    .group_by(func.date(Prediction.insert_dt)).subquery()
        
    
    # Combine all queries into a single result
    result_query = session.query(
    players_joined_query.c.insert_d,
    players_joined_query.c.joined_players_count,
    players_wallet_query.c.count_wallets,
    referrals_query.c.count_referrals,
    predictions_query.c.winners_count,
    predictions_query.c.unique_players_count,
    predictions_query.c.predictions_count,
    players_noref_wallet_query.c.count_joined_player_noref_wallet,
    unique_wallet_predicion_query.c.unique_wallets_predictions_count  
    ).outerjoin(players_wallet_query, players_joined_query.c.insert_d == players_wallet_query.c.insert_d) \
    .outerjoin(referrals_query, players_joined_query.c.insert_d == referrals_query.c.insert_d) \
    .outerjoin(predictions_query, players_joined_query.c.insert_d == predictions_query.c.insert_d) \
    .outerjoin(players_noref_wallet_query, players_joined_query.c.insert_d == players_noref_wallet_query.c.insert_d) \
    .outerjoin(unique_wallet_predicion_query, players_joined_query.c.insert_d == unique_wallet_predicion_query.c.insert_d) 
     
    # Fetch the result as a DataFrame
    df_analyzed_data = fetch_data(result_query, session)
    df_analyzed_data['unique_wallets_predictions_count'] = df_analyzed_data['unique_wallets_predictions_count'].fillna(0)   

    # Fill NaN values with 0
    df_analyzed_data['count_referrals'] = df_analyzed_data['count_referrals'].fillna(0)
    df_analyzed_data['count_joined_player_noref_wallet'] = df_analyzed_data['count_joined_player_noref_wallet'].fillna(0)

    # Calculate joined without referral
    df_analyzed_data['joined_without_referral'] = df_analyzed_data['joined_players_count'] - df_analyzed_data['count_referrals']
    df_analyzed_data = df_analyzed_data.sort_values(by='insert_d').reset_index(drop=True)
    
    
    
    wallet_first_occurrence_subquery = session.query(
        Player.telegram_id,
        Player.wallet_address,
        func.date(Player.wallet_insert_dt).label('insert_d'),
        case(
            (func.row_number().over(
                partition_by=Player.wallet_address,
                order_by=desc(Player.wallet_insert_dt),
            ) == 1, 1),
            else_=0
        ).label('is_first_occurrence')
    ).filter(Player.wallet_address.isnot(None)).subquery()
    
    # Main query to group by date and count new wallets
    new_wallets_per_day_query = session.query(
        wallet_first_occurrence_subquery.c.insert_d,
        func.sum(wallet_first_occurrence_subquery.c.is_first_occurrence).label('new_wallets_count')
    ).group_by(
        wallet_first_occurrence_subquery.c.insert_d
    ).order_by(
        wallet_first_occurrence_subquery.c.insert_d
    )

    new_wallets_per_day = new_wallets_per_day_query.all()
    new_wallets_df = pd.DataFrame(new_wallets_per_day, columns=['insert_d', 'new_wallets_count'])
    df_analyzed_data = pd.merge(df_analyzed_data, new_wallets_df, how='left', left_on='insert_d', right_on='insert_d')
    df_analyzed_data['new_wallets_count'] = df_analyzed_data['new_wallets_count'].fillna(0)
    
    
    if not DEBUG:
        update_report_table(df_analyzed_data, session_dashboard)
    # Add a total row
    def add_total_row(df):
        total_row = {'insert_d': 'Total'}
        for column in df.columns:
            if column == 'insert_d':
                continue
            try:
                total_row[column] = df[column].sum()
            except:
                total_row[column] = '-'
        df.loc[len(df)] = total_row
        return df

    df_analyzed_data = add_total_row(df_analyzed_data)
    return df_analyzed_data


# Fetch winners grouped by date
def fetch_winners_grouped_by_date(session):
    query = session.query(
        func.date(Prediction.insert_dt).label('insert_dt'),
        func.count(distinct(Prediction.player_id)).label('number_of_winners'),
        func.array_agg(distinct(Player.wallet_address)).label('winners_wallet_addresses'),
        func.array_agg(distinct(Player.telegram_id)).label('winners_telegram_ids'),
        func.array_agg(distinct(Player.telegram_username)).label('winners_telegram_usernames')
    ).join(Player, Prediction.player_id == Player.telegram_id) \
     .filter(Prediction.is_win == True) \
     .group_by(func.date(Prediction.insert_dt))
    
    df = fetch_data(query, session)
    df['amount_per_winner'] = 100.0 / df['number_of_winners']
    return df
# Fetch data for a specific date

def fetch_data_for_date(selected_date, session):
    players = session.query(Player).join(Prediction).filter(func.date(Prediction.insert_dt) == selected_date).all()
    referrals = session.query(UserReferral).filter(func.date(UserReferral.insert_dt) == selected_date).all()
    
    return players, referrals

# Player giveaway function
def player_giveaway(players, selected_date):
    if players:
        key = f'selected_player_{str(selected_date)}'
        st.write("🎰 **20$ Prize**")
        if st.button("🎲 Select a Random Player from Selected Date's Predictions"):
            random_player = random.choice(players)
            st.session_state[key] = random_player

        if key in st.session_state:
            player = st.session_state[key]
            st.write(f"🆔 Telegram ID: `{player.telegram_id}`")
            st.write(f"👤 Username: `{player.telegram_username}`")
            st.write(f"📛 First Name: `{player.first_name}`")
            st.write(f"💳 Wallet Address: `{player.wallet_address}`")
    else:
        st.write("😢 No players made predictions on the selected date.")

# Referrer giveaway function
def referrer_giveaway(referrals, selected_date):
    if referrals:
        key = f'selected_referrer_{str(selected_date)}'
        st.write("🎁 **30$ Prize**")
        if st.button("🎲 Select a Random Referrer from Selected Date's Referrals"):
            random_referrer = random.choice(referrals)
            st.session_state[key] = random_referrer

        if key in st.session_state:
            referrer = st.session_state[key]
            st.write(f"🆔 Telegram ID: `{referrer.referrer_id}`")
            st.write(f"👤 Username: `{referrer.referrer_ref.telegram_username}`")
            st.write(f"📛 First Name: `{referrer.referrer_ref.first_name}`")
            st.write(f"💳 Wallet Address: `{referrer.referrer_ref.wallet_address}`")
    else:
        st.write("😢 No referrers made referrals on the selected date.")

def create_math_function(expression, variables):
    sym_vars = {var: sp.symbols(var) for var in variables}
    for var in variables:
        expression = expression.replace(f'${var}$', str(sym_vars[var]))
    sym_expr = sp.sympify(expression)
    func = sp.lambdify(list(sym_vars.values()), sym_expr, 'numpy')
    return func


def fetch_random_eligible_player(min_predictions, min_wins, min_referrals, session):
    # Subquery for total predictions and wins
    predictions_subquery = session.query(
        Prediction.player_id,
        func.count(Prediction.id).label('total_predictions'),
        func.sum(case((Prediction.is_win == True, 1), else_=0)).label('total_wins')
    ).filter(Prediction.is_active == True) \
        .group_by(Prediction.player_id).subquery()

    # Subquery for total referrals
    referrals_subquery = session.query(
        UserReferral.referrer_id,
        func.count(UserReferral.id).label('total_referrals'),
    ).group_by(UserReferral.referrer_id).subquery()

    # Main query with filtering conditions
    query = session.query(
        Player.telegram_id,
        Player.telegram_username,
        Player.first_name,
        Player.wallet_address,
        func.coalesce(predictions_subquery.c.total_predictions, 0).label('total_predictions'),
        func.coalesce(predictions_subquery.c.total_wins, 0).label('total_wins'),
        func.coalesce(referrals_subquery.c.total_referrals, 0).label('total_referrals')
    ).outerjoin(predictions_subquery, Player.telegram_id == predictions_subquery.c.player_id) \
        .outerjoin(referrals_subquery, Player.telegram_id == referrals_subquery.c.referrer_id) \
        .filter(
            func.coalesce(predictions_subquery.c.total_predictions, 0) >= min_predictions,
            func.coalesce(predictions_subquery.c.total_wins, 0) >= min_wins,
            func.coalesce(referrals_subquery.c.total_referrals, 0) >= min_referrals
        ) \
        .order_by(func.random()) \
        .limit(1)

    result = query.first()

    if result:
        return {
            "telegram_id": result.telegram_id,
            "telegram_username": result.telegram_username,
            "first_name": result.first_name,
            "wallet_address": result.wallet_address,
            "total_predictions": result.total_predictions,
            "total_wins": result.total_wins,
            "total_referrals": result.total_referrals
        }
    return None  # Return None if no eligible player is found
    

# Function to generate success story using LangChain
def generate_success_story(player, game_description, instruction, llm):
    prompt = f"""
    Write an engaging success story about a player in the game '{game_description}'.

    Player details:
    - Username: {player['telegram_username']}
    - First Name: {player['first_name']}
    - Total Predictions: {player['total_predictions']}
    - Total Wins: {player['total_wins']}
    - Total Referrals: {player['total_referrals']}

    Make the story motivational and inspiring for other players.
    """

    history = [
        {"role": "system", "content": instruction}
    ]
    history.append({"role": "user", "content": prompt})
    response = llm.invoke(history)
    return response.content

def success_story(session, llm):
    st.markdown("Use this tool to create a motivational success story for a player!")

    # Input fields for filtering criteria
    min_predictions = st.number_input("Minimum Active Predictions", min_value=0, value=5)
    min_wins = st.number_input("Minimum Wins", min_value=0, value=1)
    min_referrals = st.number_input("Minimum Referrals", min_value=0, value=1)

    # Input field for game explanation to ChatGPT
    game_description = st.text_area("Describe Your Game for ChatGPT", "A thrilling dice prediction game with exciting rewards!")

    instruction = st.text_area("Insert Your Instructions for ChatGPT", """I want you to act as a game copywriter for Dice Maniacs. Your role is to craft electrifying, high-converting, and community-driven content that keeps players engaged, excited, and coming back for more. Your writing should be sharp, persuasive, and action-packed, using a mix of FOMO (Fear of Missing Out), psychological triggers, and strategic formatting to drive engagement.
    Your responsibilities include:
    • FOMO-Driven Announcements – Hype up upcoming dice rolls, limited-time events, and last-chance opportunities with bold, high-energy messaging.
    • Winner Updates – Celebrate winners with dynamic posts that showcase their success while motivating others to participate.
    • Referral Promotions – Encourage players to bring in friends by making the referral rewards irresistible and easy to understand.
    • Daily Dice Roll Reminders – Use urgency and excitement to remind players to place their predictions before time runs out.
    • Interactive Polls – Craft engaging poll questions that spark curiosity and discussion in the community.
    • Compelling CTAs – Drive action with short, punchy, and impactful calls to action that make players feel like they must participate now.

    Your tone should be conversational, energetic, and immersive—like a game host keeping the crowd on their toes. Keep your language concise, bold, and full of momentum. Use emojis strategically to enhance readability, and make every post feel like an event.

    """)
    
    # Submit button
    if st.button("🎲 Generate Success Story"):
        selected_player = fetch_random_eligible_player(min_predictions, min_wins, min_referrals, session)
        if not selected_player:
            st.warning("No players meet the selected criteria. Try adjusting the values.")
        else:
            # Generate a success story
            success_story = generate_success_story(selected_player, game_description, instruction, llm)

            # Display the generated story
            st.subheader("✨ Success Story")
            st.write(success_story)


        
def extract_wallet_information(session):
    wallet_address = st.text_input("🔑 Enter the wallet address")

    if wallet_address:
        # Fetch players with the specified wallet address
        players_with_wallet = session.query(Player).filter(Player.wallet_address == wallet_address).all()

        if not players_with_wallet:
            st.write("😢 No players found with this wallet address.")
        else:
            # Static Data: Calculate total wins and amount won
            wins_all = 0
            amount_won = 0

            # Fetch winners grouped by date
            winners_grouped = fetch_winners_grouped_by_date(session)
            for _, row in winners_grouped.iterrows():
                if wallet_address in row['winners_wallet_addresses']:
                    wins = row['winners_wallet_addresses'].count(wallet_address)
                    wins_all += wins
                    amount_won += wins * row['amount_per_winner']

            st.write("📊 **Static Data**")
            st.write(f"🏆 Winning predictions count: {wins_all}")
            st.write(f"💰 Amount won: {round(amount_won, 2)}")

            # Players connected to this wallet address
            st.markdown('---')
            st.write("👥 **Players Connected to this Wallet**")
            players_df = pd.DataFrame([{
                'Telegram ID': player.telegram_id,
                'Username': player.telegram_username,
                'First Name': player.first_name,
                'Wallet Address': player.wallet_address
            } for player in players_with_wallet])
            st.dataframe(players_df)

            # Predictions for each player associated with the wallet
            st.markdown('---')
            st.write("🎲 **Predictions**")
            for player in players_with_wallet:
                predictions = session.query(Prediction).filter(Prediction.player_id == player.telegram_id).all()
                if predictions:
                    st.write(f"📅 Predictions for Telegram ID: {player.telegram_id}")
                    predictions_df = pd.DataFrame([{
                        'Prediction ID': pred.id,
                        'Insert Date': pred.insert_dt,
                        'Dice 1': pred.dice_number1,
                        'Dice 2': pred.dice_number2,
                        'Slot': pred.slot,
                        'Is Win': pred.is_win,
                        'Is Active': pred.is_active
                    } for pred in predictions])
                    st.dataframe(predictions_df)
                else:
                    st.write(f"😢 No predictions for Telegram ID: {player.telegram_id}")

            # Referrals for each player
            st.markdown('---')
            st.write("🤝 **Referrals**")
            for player in players_with_wallet:
                referrals = session.query(UserReferral).filter(UserReferral.referrer_id == player.telegram_id).all()
                if referrals:
                    st.write(f"📅 Referrals for Telegram ID: {player.telegram_id}")
                    referrals_df = pd.DataFrame([{
                        'Referral ID': ref.id,
                        'Referee ID': ref.referee_id,
                        'Insert Date': ref.insert_dt
                    } for ref in referrals])
                    st.dataframe(referrals_df)
                else:
                    st.write(f"😢 No referrals for Telegram ID: {player.telegram_id}")



def extract_player_information(session):
    telegram_id_extract_player = st.text_input("🔍 Enter the player Telegram ID")

    if telegram_id_extract_player:
        try:
            telegram_id_extract_player = int(telegram_id_extract_player)

            # Fetch player data based on Telegram ID
            player = session.query(Player).filter(Player.telegram_id == telegram_id_extract_player).first()

            if not player:
                st.write("😢 Player not found!")
            else:
                # Static Data: Calculate total wins and amount won
                wins_all = 0
                amount_won = 0

                # Fetch winners grouped by date
                winners_grouped = fetch_winners_grouped_by_date(session)
                for _, row in winners_grouped.iterrows():
                    if telegram_id_extract_player in row['winners_telegram_ids']:
                        wins = row['winners_telegram_ids'].count(telegram_id_extract_player)
                        wins_all += wins
                        amount_won += wins * row['amount_per_winner']

                st.write("📊 **Static Data**")
                st.write(f"🏆 Winning predictions count: {wins_all}")
                st.write(f"💰 Amount won: {round(amount_won, 2)}")

                # Player Information
                st.markdown('---')
                st.write("👤 **Player Information**")
                player_df = pd.DataFrame([{
                    'Telegram ID': player.telegram_id,
                    'Username': player.telegram_username,
                    'First Name': player.first_name,
                    'Wallet Address': player.wallet_address
                }])
                st.dataframe(player_df)

                # Player Predictions
                st.markdown('---')
                st.write("🎲 **Predictions**")
                predictions = session.query(Prediction).filter(Prediction.player_id == telegram_id_extract_player).all()
                if predictions:
                    predictions_df = pd.DataFrame([{
                        'Prediction ID': pred.id,
                        'Insert Date': pred.insert_dt,
                        'Dice 1': pred.dice_number1,
                        'Dice 2': pred.dice_number2,
                        'Slot': pred.slot,
                        'Is Win': pred.is_win,
                        'Is Active': pred.is_active
                    } for pred in predictions])
                    st.dataframe(predictions_df)
                else:
                    st.write("😢 No predictions found for this player.")

                # Player Referrals
                st.markdown('---')
                st.write("🤝 **Referrals**")
                referrals = session.query(UserReferral).filter(UserReferral.referrer_id == telegram_id_extract_player).all()
                if referrals:
                    referrals_df = pd.DataFrame([{
                        'Referral ID': ref.id,
                        'Referee ID': ref.referee_id,
                        'Insert Date': ref.insert_dt
                    } for ref in referrals])
                    st.dataframe(referrals_df)
                else:
                    st.write("😢 No referrals found for this player.")
                
                
                def extract_wallet():
                    assets = session.query(Asset).filter(Asset.player_id == telegram_id_extract_player).all()
                    if assets:
                        assets_df = pd.DataFrame([{
                            'Asset ID': asset.id,
                            'Player ID': asset.player_id,
                            'Symbol': asset.symbol,
                            'Balance': asset.balance,
                            'Decimal': asset.decimal
                        } for asset in assets])
                        st.dataframe(assets_df)
                    else:
                        st.write("😢 No money found for this player.")
                
                st.markdown('---')
                st.write("🤑 **Assets**")
                extract_wallet()
                
        except ValueError:
            st.write("❌ ID must be a number.")
                      


def assets_section(session):
    
    query = session.query(
        Asset.symbol,
        func.count(Asset.id).label('total_repeats'),
        func.avg(Asset.price).label('average_price')
    ).group_by(Asset.symbol).order_by(desc('total_repeats'))
    
    st.write("💰 **Table of All Assets**")
    result_df = fetch_data(query, session)
    st.dataframe(result_df)
    
    
    st.markdown('---')
    st.write('💵 **Active Wallets Data**')
    all_wallets = session.query(Player).filter(Player.wallet_address.isnot(None)).count()
    active_wallets = result_df.iloc[0]['total_repeats']
    inactive_wallets = all_wallets - active_wallets
    ratio_active_wallets = active_wallets / all_wallets
    ratio_inactive_wallets = inactive_wallets / all_wallets
    
    st.write(f'All wallets: {all_wallets}')
    st.write(f'Active wallets: {active_wallets}')
    st.write(f'Inactive wallets: {inactive_wallets}')
    st.write(f'Active wallets ratio: {100 * round(ratio_active_wallets, 4)} \%')
    st.write(f'Inactive wallets ratio: {100 * round(ratio_inactive_wallets, 4)} \%')

    
    st.markdown('---')
    st.write("💵 **USD Value of Each Player - Sorted**")
    
    
    player_assets_query = session.query(
        Player.telegram_id,
        Player.telegram_username,
        Player.first_name,
        func.sum(Asset.usd_value).label('total_usd_value'),
        Player.wallet_address
    ).join(Asset, Player.telegram_id == Asset.player_id) \
        .group_by(Player.telegram_id) \
        .order_by(desc('total_usd_value'))
    
    player_assets_df = fetch_data(player_assets_query, session)
    st.dataframe(player_assets_df)
    
    
    st.markdown('---')
    st.write("📊 **Histogram of Wallets**")
    total_usd_values = player_assets_df['total_usd_value']
    
    # histogram
    interval = st.number_input("Select interval size for histogram", min_value=0.1, value=0.2, step=0.1)
    maximum = st.number_input("Select maximum value for histogram", min_value=0, value=100, step=1)
    filtered_usd_values = total_usd_values[total_usd_values <= maximum]
    total_discarded_values = len(total_usd_values) - len(filtered_usd_values)
    st.write(f'Max is {total_usd_values.max()}')
    st.write(f'{total_discarded_values} values are discarded')
    fig_usd_histogram = go.Figure()

    fig_usd_histogram.add_trace(go.Histogram(
        x=filtered_usd_values,
        xbins=dict(
            start=0,
            end=maximum,
            size=interval  # 5 USD intervals
        ),
        marker_color='#1f77b4',
        opacity=0.75
    ))

    fig_usd_histogram.update_layout(
        title="Histogram of USD Value of Each Player",
        xaxis_title="Total USD Value",
        yaxis_title="Frequency",
        template="plotly_dark",
        showlegend=False
    )

    st.plotly_chart(fig_usd_histogram)



def plot_graphs(df_analyzed_data):
    # Ensure 'insert_d' is a datetime object for filtering
    df_analyzed_data['insert_d'] = pd.to_datetime(df_analyzed_data['insert_d'], errors='coerce')

    # Ensure valid min and max dates for slider
    min_date = df_analyzed_data['insert_d'].min()
    max_date = df_analyzed_data['insert_d'].max()

    if pd.isnull(min_date) or pd.isnull(max_date):
        st.error("No valid dates available for plotting.")
        return

    min_date = min_date.to_pydatetime()
    max_date = max_date.to_pydatetime()

    # Create date range slider
    start_date, end_date = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )

    # Filter data within selected date range
    filtered_data = df_analyzed_data[
        (df_analyzed_data['insert_d'] >= pd.to_datetime(start_date)) &
        (df_analyzed_data['insert_d'] <= pd.to_datetime(end_date))
    ]
    
    filtered_data['insert_d'] = filtered_data['insert_d'].dt.date  # Convert to date-only format

    # Expression Builder UI
    st.header("Expression Builder")

    columns = [col for col in df_analyzed_data.columns if col != 'insert_d']
    operations = ['+', '-', '*', '/']

    if 'expr' not in st.session_state:
        st.session_state.expr = ''
    if 'isVar' not in st.session_state:
        st.session_state.isVar = True
    if 'canSave' not in st.session_state:
        st.session_state.canSave = False

    expr = st.session_state.expr
    st.code(f"Your Expression: {expr}", language="markdown")

    if st.session_state.isVar:
        for column in columns:
            display = column.replace('_', '\,')
            if st.button(f"${display}$", key=f'add_{column}'):
                st.session_state.expr += f'${column}$'
                st.session_state.isVar = False
                st.session_state.canSave = True
                st.rerun()
    else:
        for opr in operations:
            if st.button(f"${opr}$", key=f'add_{opr}'):
                st.session_state.expr += f'{opr}'
                st.session_state.isVar = True
                st.session_state.canSave = False
                st.rerun()

    # Save expressions in session state
    if 'expressions' not in st.session_state:
        st.session_state.expressions = []

    def reset():
        st.session_state.expr = ''
        st.session_state.isVar = True
        st.session_state.canSave = False
        st.rerun()

    if st.session_state.expr != '':
        if st.button('Clear Expression', type="secondary"):
            reset()

    if st.session_state.canSave:
        if st.button("Save Expression", type="primary"):
            if expr.strip():
                st.session_state.expressions.append(expr)
                disp = expr.replace('_', '\,')
                st.success(f"Expression '{disp}' saved!")
                reset()
            else:
                st.error("Please enter a valid expression.")
                st.session_state.expr = ''

    # Display and delete saved expressions
    st.header("Saved Expressions")
    for i, expr in enumerate(st.session_state.expressions):
        disp = expr.replace('_', '\,')
        if st.button(f"Delete: {disp}", key=f"delete_{i}"):
            st.session_state.expressions.pop(i)
            st.rerun()

    # Plotting Expression Builder Graphs
    if st.session_state.expressions:
        fig_expr = go.Figure()

        for expr in st.session_state.expressions:
            try:
                # Extract variables from expression
                variables = set()
                start = 0
                while True:
                    start = expr.find('$', start)
                    if start == -1:
                        break
                    end = expr.find('$', start + 1)
                    if end == -1:
                        raise ValueError("Unmatched $ in expression")
                    var_name = expr[start + 1:end]
                    variables.add(var_name)
                    start = end + 1

                # Create function from expression
                math_func = create_math_function(expr, variables)

                # Compute expression values
                result = [math_func(*[row[var] for var in variables]) for _, row in filtered_data.iterrows()]

                # Add trace to plot
                fig_expr.add_trace(go.Scatter(
                    x=filtered_data['insert_d'],
                    y=result,
                    mode='lines',
                    name=expr
                ))
            except Exception as e:
                st.error(f"Error evaluating expression '{expr}': {e}")

        # Format and display the plot
        def fix_date(dt):
            return str(dt).split()[0]

        fig_expr.update_layout(
            title=f"Plotted Expressions from {fix_date(start_date)} to {fix_date(end_date)}",
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_dark",
            showlegend=True
        )

        st.plotly_chart(fig_expr)
    else:
        st.write("No expressions saved yet. Please build and save an expression.")



def plot_histograms(df_analyzed_data, session):
     # New Section: Histogram of Dice Pairs
    st.header("🎲 Dice Pair Predictions Histogram")
    df_analyzed_data['insert_d'] = pd.to_datetime(df_analyzed_data['insert_d'], errors='coerce')

    # Ensure valid min and max dates for slider
    min_date = df_analyzed_data['insert_d'].min()
    max_date = df_analyzed_data['insert_d'].max()

    if pd.isnull(min_date) or pd.isnull(max_date):
        st.error("No valid dates available for plotting.")
        return

    min_date = min_date.to_pydatetime()
    max_date = max_date.to_pydatetime()

    # Create date range slider
    start_date, end_date = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD",
        key='hist_slider'
    )
    # Fetch dice pairs within the selected date range
    dice_pairs_query = session.query(
        Prediction.dice_number1,
        Prediction.dice_number2
    ).filter(
        Prediction.insert_dt >= start_date,
        Prediction.insert_dt <= end_date
    )

    dice_pairs_df = fetch_data(dice_pairs_query, session)

    if not dice_pairs_df.empty:
        dice_pairs_df['dice_pair'] = dice_pairs_df.apply(
            lambda row: f"{min(row['dice_number1'], row['dice_number2'])}-{max(row['dice_number1'], row['dice_number2'])}",
            axis=1
        )
        ordered_dice_pairs = []
        for i in range(1, 7):
            for j in range(i, 7):
                ordered_dice_pairs.append(f"{str(i)}-{str(j)}")
        all_dice_pairs_df = pd.DataFrame({"dice_pair": ordered_dice_pairs})
        dice_counts = dice_pairs_df['dice_pair'].value_counts().reset_index()
        dice_counts.columns = ['dice_pair', 'count']
        merged_df = all_dice_pairs_df.merge(dice_counts, on='dice_pair', how='left').fillna(0)
        merged_df['dice_pair'] = pd.Categorical(merged_df['dice_pair'], categories=ordered_dice_pairs, ordered=True)
        merged_df = merged_df.sort_values('dice_pair')

        # Plot histogram
        fig_dice = go.Figure()

        fig_dice.add_trace(go.Bar(
            x=merged_df['dice_pair'],
            y=merged_df['count'],
            name="Dice Pairs",
            marker_color='#1f77b4',
            opacity=0.75
        ))

        # Update layout
        fig_dice.update_layout(
            title=f"Histogram of Dice Pairs from {start_date.date()} to {end_date.date()}",
            xaxis_title="Dice Pair",
            yaxis_title="Frequency",
            template="plotly_dark",
            showlegend=True,
            bargap=0.1
        )

        st.plotly_chart(fig_dice)
    else:
        st.write("😢 No dice pair predictions found in the selected date range.")
        
        
def plot_frequent_graphs(df_analyzed_data):
    count_wallets = df_analyzed_data['count_wallets']
    new_wallets = df_analyzed_data['new_wallets_count']
    joined_players = df_analyzed_data['joined_players_count']
    predictions = df_analyzed_data['predictions_count']
    
    signals = [count_wallets, new_wallets, joined_players, predictions]
    titles = ['Wallets', 'New Wallets', 'Joined Players', 'Predictions']
    
    