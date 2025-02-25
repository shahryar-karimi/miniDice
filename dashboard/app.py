import os
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy import func
import plotly.graph_objects as go



# Set up the environment variables
host = os.getenv("POSTGRES_HOST")
dbname = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")

STREAMLIT_PASSWORD = os.getenv("STREAMLIT_PASSWORD")

# Define the base for the ORM
Base = declarative_base()

# Define the ORM classes
class Player(Base):
    __tablename__ = 'player'
    
    telegram_id = Column(Integer, primary_key=True)
    telegram_username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    telegram_language_code = Column(String)
    wallet_address = Column(String)
    wallet_insert_dt = Column(DateTime)
    insert_dt = Column(DateTime)

class Prediction(Base):
    __tablename__ = 'prediction'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.telegram_id'))
    insert_dt = Column(DateTime)
    countdown_id = Column(Integer)
    dice_number1 = Column(Integer)
    dice_number2 = Column(Integer)
    slot = Column(Integer)
    is_win = Column(Integer)
    is_active = Column(Integer)
    
    # Define the relationship with the Player model
    player_ref = relationship("Player", backref="predictions")

class UserReferral(Base):
    __tablename__ = 'user_referral'
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('player.telegram_id'))
    referee_id = Column(Integer, ForeignKey('player.telegram_id'))
    insert_dt = Column(DateTime)
    
    # Specify the foreign_keys argument to clarify which column to use for the relationship
    referrer_ref = relationship(
        "Player", 
        backref="referrals", 
        foreign_keys=[referrer_id],
        primaryjoin="UserReferral.referrer_id == Player.telegram_id"  # Explicit join condition
    )
    
    referee_ref = relationship(
        "Player", 
        backref="referred_by", 
        foreign_keys=[referee_id],
        primaryjoin="UserReferral.referee_id == Player.telegram_id"  # Explicit join condition
    )
# Create the engine and session
engine = create_engine(f'postgresql://{user}:{db_password}@{host}:{port}/{dbname}')
Session = sessionmaker(bind=engine)
session = Session()

def fetch_players():
    return session.query(Player).all()

def fetch_predictions():
    return session.query(Prediction).all()

def fetch_referrals():
    return session.query(UserReferral).all()

def fetch_data_for_previous_day():
    today = datetime.today().date()
    previous_day = today - timedelta(days=1)

    # Querying players who made predictions on the previous day
    players_prev_day = session.query(Player).join(Prediction).filter(func.date(Prediction.insert_dt) == previous_day).all()
    
    # Querying players who referred someone or were referred on the previous day
    referrals_prev_day = session.query(UserReferral).join(
        Player, 
        (UserReferral.referrer_id == Player.telegram_id)  # Join UserReferral to Player through referrer_id
    ).filter(func.date(UserReferral.insert_dt) == previous_day).all()    
    
    return players_prev_day, referrals_prev_day


def fetch_analyzed_data_grouped_by_date(df_players, df_predictions, df_referrals):
    
    df_players['insert_d'] = df_players['insert_dt'].apply(lambda x: str(x).split()[0])
    df_players_joined_grouped = df_players.groupby(by='insert_d').size().reset_index()
    df_players_joined_grouped.columns = ['insert_d', 'joined_players_count']

    df_players = df_players.loc[df_players['wallet_address'].notna()]
    df_players.loc[:, 'insert_d'] = df_players['wallet_insert_dt'].apply(lambda x: str(x).split()[0])
    df_players_grouped = df_players.groupby(by= 'insert_d').size().reset_index()
    df_players_grouped = pd.DataFrame(df_players_grouped)
    df_players_grouped.columns = ['insert_d', 'count']

    df_referrals['insert_d'] = df_referrals['insert_dt'].apply(lambda x: str(x).split()[0])
    df_referrals_grouped = df_referrals.groupby(by='insert_d').size().reset_index()
    df_referrals_grouped = pd.DataFrame(df_referrals_grouped)
    df_referrals_grouped.columns = ['insert_d', 'count']

    df_predictions['insert_d'] = df_predictions['insert_dt'].apply(lambda x: str(x).split()[0])
    df_predictions_grouped_wins = df_predictions.groupby(by= 'insert_d').agg(is_win=('is_win', 'sum'),
                                                                            unique_players_count=('player_id', 'nunique'),
                                                                            predictions_count=('player_id', 'size')).reset_index()

    df_predictions_grouped_wins = pd.DataFrame(df_predictions_grouped_wins)
    df_predictions_grouped_wins = df_predictions_grouped_wins.rename(columns={'is_win': 'winners_count'})

    df_analyzed_data = df_players_grouped.join(df_referrals_grouped.set_index('insert_d'), on='insert_d', lsuffix='_wallets', rsuffix='_referrals')
    df_analyzed_data = df_analyzed_data.join(df_predictions_grouped_wins.set_index('insert_d'), on='insert_d')
    df_analyzed_data = df_analyzed_data.join(df_players_joined_grouped.set_index('insert_d'), on='insert_d')

    df_analyzed_data['count_referrals'] = df_analyzed_data['count_referrals'].fillna(0)
    df_analyzed_data['joined_without_referral'] = df_analyzed_data['joined_players_count'] - df_analyzed_data['count_referrals']
    
    
    def get_joined_without_referrals_who_connected_wallet(players, referrals):
        players = players.loc[players['wallet_address'].notna()]
        referred_players = referrals['referee_id'].values
        players = players.loc[~players['telegram_id'].isin(referred_players)]
        players_grouped = players.groupby('insert_d').size().reset_index(name='count_joined_player_noref_wallet')
        return players_grouped
    
    df_joined_player_noref_wallet = get_joined_without_referrals_who_connected_wallet(df_players, df_referrals)
    df_analyzed_data = df_analyzed_data.join(df_joined_player_noref_wallet.set_index('insert_d'), on='insert_d')
    
    
    
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


def fetch_winners_grouped_by_date():
    # Querying winners (where is_win == 1)
    winners = session.query(Prediction).filter(Prediction.is_win == True).all()
    
    # Group by insert date
    winners_details = []
    for winner in winners:
        player = session.query(Player).filter(Player.telegram_id == winner.player_id).first()
        winners_details.append({
            'insert_dt': winner.insert_dt.date(),  # Group by date
            'player_id': player.telegram_id,
            'telegram_username': player.telegram_username,
            'first_name': player.first_name,
            'wallet_address': player.wallet_address,
        })

    # Convert to DataFrame
    winners_df = pd.DataFrame(winners_details)

    # Group by the insert_dt (date) and aggregate the desired information
    winners_grouped = winners_df.groupby('insert_dt').agg(
        number_of_winners=('player_id', 'size'),
        winners_wallet_addresses=('wallet_address', lambda x: list(set(x))),
        winners_telegram_ids=('player_id', lambda x: list(set(x))),
        winners_telegram_usernames=('telegram_username', lambda x: list(set(x)))
    ).reset_index()

    # Calculate the amount each winner gets (100 / number of winners)
    winners_grouped['amount_per_winner'] = 100.0 / winners_grouped['number_of_winners']    
    winners_grouped = winners_grouped.loc[:, ['insert_dt', 'number_of_winners', 'amount_per_winner', 'winners_wallet_addresses', 'winners_telegram_ids', 'winners_telegram_usernames']]

    return winners_grouped

def player_giveaway(players_prev_day):
    player_list = pd.DataFrame([{
        'player': player.telegram_id,
        'telegram_username': player.telegram_username,
        'first_name': player.first_name,
        'wallet_address': player.wallet_address
    } for player in players_prev_day])

    if len(player_list) > 0:
        st.write('20$ Prize')
        if st.button("Select a Random Player from Yesterday's Predictions"):
            random_player = player_list.sample(n=1).iloc[0]
            st.session_state.selected_player = random_player

        if 'selected_player' in st.session_state:
            random_player = st.session_state.selected_player
            st.write(f"Telegram ID: {random_player['player']}")
            st.write(f"Username: {random_player['telegram_username']}")
            st.write(f"First Name: {random_player['first_name']}")
            st.write(f"Wallet Address: {random_player['wallet_address']}")
    else:
        st.write("No players made predictions yesterday.")

# Function to handle referrer giveaway
def referrer_giveaway(referrals_prev_day):
    referrer_list = pd.DataFrame([{
        'referrer': referrer.referrer_id,
        'telegram_username': referrer.referrer_ref.telegram_username,  # Access through the relationship
        'first_name': referrer.referrer_ref.first_name,  # Access through the relationship
        'wallet_address': referrer.referrer_ref.wallet_address  # Access through the relationship
    } for referrer in referrals_prev_day])
    
    if len(referrer_list) > 0:
        st.write('30$ Prize')
        if st.button("Select a Random Referrer from Yesterday's Referrals"):
            random_referrer = referrer_list.sample(n=1).iloc[0]
            st.session_state.selected_referrer = random_referrer

        if 'selected_referrer' in st.session_state:
            random_referrer = st.session_state.selected_referrer
            st.write(f"Telegram ID: {random_referrer['referrer']}")
            st.write(f"Username: {random_referrer['telegram_username']}")
            st.write(f"First Name: {random_referrer['first_name']}")
            st.write(f"Wallet Address: {random_referrer['wallet_address']}")
    else:
        st.write("No referrers made referrals yesterday.")
        
        
# Assuming df_analyzed_data is your DataFrame

def plot_graphs(df_analyzed_data):
    # Ensure 'insert_d' is a datetime object for filtering
    df_analyzed_data['insert_d'] = pd.to_datetime(df_analyzed_data['insert_d'], errors='coerce')

    # Create the slider for selecting the date range
    min_date = df_analyzed_data['insert_d'].min().to_pydatetime()
    max_date = df_analyzed_data['insert_d'].max().to_pydatetime()

    start_date, end_date = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )

    # Filter the DataFrame based on the selected date range
    filtered_data = df_analyzed_data[(df_analyzed_data['insert_d'] >= pd.to_datetime(start_date)) & (df_analyzed_data['insert_d'] <= pd.to_datetime(end_date))]
    filtered_data.loc[:, 'insert_d'] = filtered_data['insert_d'].dt.date  # Ensure the date is just in the date format

    # Create checkboxes for column selection
    selected_columns = st.multiselect(
        "Select Columns to Plot",
        options=[col for col in df_analyzed_data.columns if col != 'insert_d'],  # Exclude 'insert_d' from options
        default=[col for col in df_analyzed_data.columns if col != 'insert_d']  # Default to all columns except 'insert_d'
    )

    # Plot using Plotly if any columns are selected
    if selected_columns:
        # Create a Plotly figure
        fig = go.Figure()

        # Loop through selected columns to plot each one
        for column in selected_columns:
            try:
                chart_data = filtered_data[['insert_d', column]]
                fig.add_trace(go.Scatter(
                    x=chart_data['insert_d'],
                    y=chart_data[column],
                    mode='lines',
                    name=column
                ))
            except Exception as e:
                st.write(f"Error plotting {column}: {e}")
        
        # Update layout for better visualization
        fig.update_layout(
            title=f"Selected Columns from {start_date} to {end_date}",
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_dark",  # Optional, change the theme
            showlegend=True
        )

        # Display the Plotly figure
        st.plotly_chart(fig)
    else:
        st.write("Please select at least one column to plot.")

# Extract Wallet Information Function
def extract_wallet_information(df_players, df_predictions, df_referrals, df_winners_grouped):
    
    wallet_address = st.text_input("Enter the wallet address")

    # Extract players with the specified wallet address
    players_with_this_wallet_address = df_players.loc[df_players['wallet_address'] == wallet_address].reset_index(drop=True)

    if len(players_with_this_wallet_address) == 0:
        st.write("No players found with this wallet address.")
    else:
        # Static Data
        st.write('Static Data')
        wins_all = 0
        amount_won = 0

        # Loop through winners grouped data to calculate the total wins and amount won for the wallet
        for j in range(len(df_winners_grouped)):
            row = df_winners_grouped.iloc[j]
            winner_wallets = row['winners_wallet_addresses']
            if wallet_address in winner_wallets:
                wins = winner_wallets.count(wallet_address)
                wins_all += wins
                amount_won += wins * row['amount_per_winner']

        st.write(f'Winning predictions count: {wins_all}')
        st.write(f'Amount won: {round(amount_won, 2)}')

        # Players connected to this wallet address
        st.markdown('---')
        st.write('Players Connected to this Wallet')
        st.dataframe(players_with_this_wallet_address.reset_index(drop=True))

        # Predictions for each player associated with the wallet
        st.markdown('-' * 3)
        st.write('Predictions')
        for i in range(len(players_with_this_wallet_address)):
            row = players_with_this_wallet_address.iloc[i]
            telegram_id = row['telegram_id']
            predictions_for_this_id = df_predictions.loc[df_predictions['player_id'] == telegram_id].reset_index()
            if len(predictions_for_this_id) > 0:
                st.write(f'Predictions for id: {telegram_id}')
                st.dataframe(predictions_for_this_id.reset_index(drop=True))
            else:
                st.write(f'No predictions for id: {telegram_id}')

        # Referrals for each player
        st.markdown('-' * 3)
        st.write('Referrals')
        for i in range(len(players_with_this_wallet_address)):
            row = players_with_this_wallet_address.iloc[i]
            telegram_id = row['telegram_id']
            referres_for_this_id = df_referrals.loc[df_referrals['referrer_id'] == telegram_id]
            if len(referres_for_this_id) > 0:
                st.write(f'Referrals for id: {telegram_id}')
                st.dataframe(referres_for_this_id.reset_index(drop=True))
            else:
                st.write(f'No referrals for id: {telegram_id}')


# Extract Player Information Function
def extract_player_information(df_players, df_predictions, df_referrals, df_winners_grouped):  
    telegram_id_extract_player = st.text_input("Enter the player Telegram ID")
    
    if telegram_id_extract_player != '':
        try:
            telegram_id_extract_player = int(telegram_id_extract_player)

            # Extract player data based on telegram_id
            player_df = df_players.loc[df_players['telegram_id'] == telegram_id_extract_player].reset_index()
            if len(player_df) == 0:
                st.write('Player not found!')
            else:
                # Static Data: Winning predictions and amount won
                st.write('Static Data')
                wins_all = 0
                amount_won = 0

                for j in range(len(df_winners_grouped)):
                    row = df_winners_grouped.iloc[j]
                    winner_ids = row['winners_telegram_ids']
                    if telegram_id_extract_player in winner_ids:
                        wins = winner_ids.count(telegram_id_extract_player)
                        wins_all += wins
                        amount_won += wins * row['amount_per_winner']
                st.write(f'Winning predictions count: {wins_all}')
                st.write(f'Amount won: {round(amount_won, 2)}')

                # Player Information
                st.write('Information:')
                st.dataframe(player_df.reset_index(drop=True))

                # Player Predictions Data
                player_predictions_df = df_predictions.loc[df_predictions['player_id'] == telegram_id_extract_player].reset_index()
                st.markdown('---')
                st.write('Predictions:')
                st.dataframe(player_predictions_df.reset_index(drop=True))
                
                st.markdown('---')
                referres_for_this_id = df_referrals.loc[df_referrals['referrer_id'] == telegram_id_extract_player]
                if len(referres_for_this_id) > 0:
                    st.write(f'Referrals for id: {telegram_id_extract_player}')
                    st.dataframe(referres_for_this_id.reset_index(drop=True))
                else:
                    st.write(f'No referrals for id: {telegram_id_extract_player}')
                    

        except ValueError:
            st.write('ID must be a number')
            
                
                
def main():
    # Create a password input box
    password = st.text_input("Enter the password", type="password")
    # password = STREAMLIT_PASSWORD
    if password == STREAMLIT_PASSWORD:
        st.write("Welcome! You have access to this page.")

        # Fetch data from the database only when needed
        df_players = pd.read_sql(session.query(Player).statement, session.bind)
        df_predictions = pd.read_sql(session.query(Prediction).statement, session.bind)
        df_referrals = pd.read_sql(session.query(UserReferral).statement, session.bind)

        st.markdown('---')        
        with st.expander("Data Sheets"):
            
            
            df_analyzed_data = fetch_analyzed_data_grouped_by_date(df_players, df_predictions, df_referrals)
            st.write('Analyzed Data')
            st.dataframe(df_analyzed_data.reset_index(drop=True))
            
            
            df_winners_grouped = fetch_winners_grouped_by_date()
            st.write('Winners Data')
            st.dataframe(df_winners_grouped.reset_index(drop=True))

        
        # Filter data for previous day (winners, players, referrals)
        players_prev_day, referrals_prev_day = fetch_data_for_previous_day()

        st.markdown('---')
        with st.expander('Giveaways'):
            st.markdown('---')
            player_giveaway(players_prev_day)
            st.markdown('---')
            referrer_giveaway(referrals_prev_day)
            
            
        st.markdown('---')
        with st.expander('Graphs'):
            # Process and plot data based on date ranges
            plot_graphs(df_analyzed_data)  # Implement the graph logic here (as in your original code)

        st.markdown('---')
        with st.expander('Extract Wallet Information'):
            extract_wallet_information(df_players, df_predictions, df_referrals, df_winners_grouped)
            
        st.markdown('---')
        with st.expander('Extract Player Information'):
            extract_player_information(df_players, df_predictions, df_referrals, df_winners_grouped)


if __name__ == "__main__":
    main()