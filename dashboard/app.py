
password = 0

import psycopg2
import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import os
from matplotlib import pyplot as plt


host = os.getenv("POSTGRES_HOST")
dbname = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")

STREAMLIT_PASSWORD = os.getenv("STREAMLIT_PASSWORD")



def fetch_data():
    conn_string = f"host='{host}' dbname='{dbname}' user='{user}' password='{db_password}' port='{port}'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor() 


    print("Database opened successfully")

    
    query = """
    SELECT table_name
  FROM information_schema.tables
 WHERE table_schema='public'
    """
    
    cursor.execute(query)
    res = cursor.fetchall()
    
        
    query = """
        SELECT telegram_id, telegram_username, first_name, last_name, telegram_language_code, wallet_address, wallet_insert_dt, insert_dt
        FROM player
    """
    cursor.execute(query) 
    df_players = pd.DataFrame(cursor.fetchall(), columns=['telegram_id', 'telegram_username', 'first_name', 'last_name', 'telegram_language_code', 'wallet_address', 'wallet_insert_dt', 'insert_dt'])
    
    query = """
        SELECT player_id, insert_dt, countdown_id, dice_number1, dice_number2, slot, is_win, is_active
        FROM prediction
    """
    cursor.execute(query)
    df_predictions = pd.DataFrame(cursor.fetchall(), columns=['player', 'insert_dt', 'countdown', 'dice_number1', 'dice_number2', 'slot', 'is_win', 'is_active'])
    
    
    query = """
        SELECT user_referral.referrer_id, user_referral.referee_id, user_referral.insert_dt
        FROM user_referral
    """
    cursor.execute(query)
    df_referrals = pd.DataFrame(cursor.fetchall(), columns=['referrer', 'referee', 'insert_dt'])
                
    conn.close()
    print("Database Closed successfully")
    
    return df_players, df_predictions, df_referrals
    
    

def main():
    # Create a password input box
    
    global password
    password = st.text_input("Enter the password", type="password")
    # password = STREAMLIT_PASSWORD
    # Check if the entered password is correct
    if password == STREAMLIT_PASSWORD:
        st.write("Welcome! You have access to this page.")
        # Your protected page content goes here
        
        df_players, df_predictions, df_referrals = fetch_data()
        
        st.markdown('---')        
        with st.expander("Data Sheets"):

            # st.write("Players Dataframe")
            # st.dataframe(df_players)
            
            # st.write("Predictions Dataframe")
            # st.dataframe(df_predictions)
            
            # st.write("Referrals Dataframe")
            # st.dataframe(df_referrals)
            
            
            df_players['player_insert_d'] = df_players['insert_dt'].apply(lambda x: str(x).split()[0])
            df_players_joined_grouped = df_players.groupby(by='player_insert_d').size().reset_index()
            df_players_joined_grouped.columns = ['insert_d', 'joined_players_count']
            
            
            df_players = df_players.loc[df_players['wallet_address'].notna()]
            df_players['insert_d'] = df_players['wallet_insert_dt'].apply(lambda x: str(x).split()[0])
            df_players_grouped = df_players.groupby(by= 'insert_d').size().reset_index()
            df_players_grouped = pd.DataFrame(df_players_grouped)
            df_players_grouped.columns = ['insert_d', 'count']
        
            
            df_referrals['insert_d'] = df_referrals['insert_dt'].apply(lambda x: str(x).split()[0])
            df_referrals_grouped = df_referrals.groupby(by='insert_d').size().reset_index()
            df_referrals_grouped = pd.DataFrame(df_referrals_grouped)
            df_referrals_grouped.columns = ['insert_d', 'count']
            
            df_predictions['insert_d'] = df_predictions['insert_dt'].apply(lambda x: str(x).split()[0])
            df_predictions_grouped_wins = df_predictions.groupby(by= 'insert_d').agg(is_win=('is_win', 'sum'),
                                                                                    unique_players_count=('player', 'nunique'),
                                                                                    predictions_count=('player', 'size')).reset_index()
            

            df_predictions_grouped_wins = pd.DataFrame(df_predictions_grouped_wins)
            df_predictions_grouped_wins = df_predictions_grouped_wins.rename(columns={'is_win': 'winners_count'})

            df_analyzed_data = df_players_grouped.join(df_referrals_grouped.set_index('insert_d'), on='insert_d', lsuffix='_wallets', rsuffix='_referrals')
            df_analyzed_data = df_analyzed_data.join(df_predictions_grouped_wins.set_index('insert_d'), on='insert_d')
            df_analyzed_data = df_analyzed_data.join(df_players_joined_grouped.set_index('insert_d'), on='insert_d')
            
            total_row = {'insert_d': 'Total'}
            for column in df_analyzed_data.columns:
                if column == 'insert_d':
                    continue
                try:
                    total_row[column] = df_analyzed_data[column].sum()
                except:
                    total_row[column] = '-'

            df_analyzed_data.loc[len(df_analyzed_data)] = total_row
            
            st.write('Analyzed Data')
            st.dataframe(df_analyzed_data.reset_index())
            
            
            # Filter only winners from predictions
            df_winners = df_predictions[df_predictions['is_win'] == 1]

            # Merge with players data to get the player accounts and wallets for winners
            df_winners_merged = df_winners.merge(df_players[['telegram_id', 'wallet_address', 'telegram_username']], 
                                                how='left', left_on='player', right_on='telegram_id')

            # st.dataframe(df_winners_merged)
            # Extracting unique winners by date
            df_winners_grouped = df_winners_merged.groupby('insert_d').agg(
                winner_accounts=('telegram_username', lambda x: list(set(x))),
                winner_wallets=('wallet_address', lambda x: list(set(x))),
                winner_ids=('telegram_id', lambda x: list(set(x)))
            ).reset_index()
            
            # st.dataframe(df_winners_grouped)
            
            df_winners_grouped['winners_count'] = df_winners_grouped['winner_wallets'].apply(lambda x: len(x))
            
            df_winners_grouped['winners_amount'] = df_winners_grouped['winners_count'].apply(lambda x: 100.0 / float(x))
            df_winners_grouped = df_winners_grouped.loc[:, ['insert_d', 'winners_count', 'winners_amount', 'winner_accounts', 'winner_wallets', 'winner_ids']]

            # Display the result for winner accounts and wallets by date
            st.write('Winners Accounts and Wallets by Date')
            st.dataframe(df_winners_grouped.reset_index())
        
        
        st.markdown('---', )
        with st.expander('Giveaways'):
            # Get the current date and calculate the previous day
            today = datetime.today().date()
            previous_day = today - timedelta(days=1)

            # Filter the predictions to get those from the previous day
            df_predictions_prev_day = df_predictions[df_predictions['insert_d'] == str(previous_day)]

            # Merge with the player dataframe to get player details
            df_predictions_prev_day_merged = df_predictions_prev_day.merge(df_players[['telegram_id', 'telegram_username', 'first_name', 'wallet_address']], how='left', left_on='player', right_on='telegram_id')

            # List of players who predicted the previous day
            player_list = df_predictions_prev_day_merged[['player', 'telegram_username', 'first_name', 'wallet_address']]

            if len(player_list) > 0:
                # Randomly select one player from the list
                st.markdown('---')
                st.write('20$ Prize')
                if st.button("Select a Random Player from Yesterday's Predictions"):
                    random_player = player_list.sample(n=1).iloc[0]
                    
                    # Save the selected player's details to session state
                    st.session_state.selected_player = {
                        'player': random_player['player'],
                        'telegram_username': random_player['telegram_username'],
                        'first_name': random_player['first_name'],
                        'wallet_address': random_player['wallet_address']
                    }
    
                if 'selected_player' in st.session_state:
                    random_player = st.session_state.selected_player
                    st.write(f"Telegram ID: {random_player['player']}")
                    st.write(f"Username: {random_player['telegram_username']}")
                    st.write(f"First Name: {random_player['first_name']}")
                    st.write(f"Wallet Address: {random_player['wallet_address']}")

            else:
                st.write("No players made predictions yesterday.")
                
            # Extracting the date from the datetime fields
            df_predictions['insert_d'] = df_predictions['insert_dt'].apply(lambda x: str(x).split()[0])
            df_referrals['insert_d'] = df_referrals['insert_dt'].apply(lambda x: str(x).split()[0])

            # Get the current date and calculate the previous day
            today = datetime.today().date()
            previous_day = today - timedelta(days=1)

            # Filter the referrals to get those from the previous day
            df_referrals_prev_day = df_referrals[df_referrals['insert_d'] == str(previous_day)]

            # Merge with the player dataframe to get referrer details (username, first name, wallet address)
            df_referrals_prev_day_merged = df_referrals_prev_day.merge(df_players[['telegram_id', 'telegram_username', 'first_name', 'wallet_address']], how='left', left_on='referrer', right_on='telegram_id')

            # List of referrers who referred someone the previous day
            referrer_list = df_referrals_prev_day_merged[['telegram_id', 'telegram_username', 'first_name', 'wallet_address', 'insert_d']]

            if len(referrer_list) > 0:
                # Randomly select one referrer from the list
                st.markdown('---')
                st.write('30$ Prize')
                if st.button("Select a Random Referrer from Yesterday's Referrals"):
                    random_referrer = referrer_list.sample(n=1).iloc[0]
                    
                    # Save the selected player's details to session state
                    st.session_state.selected_referrer = {
                        'player': random_referrer['telegram_id'],
                        'telegram_username': random_referrer['telegram_username'],
                        'first_name': random_referrer['first_name'],
                        'wallet_address': random_referrer['wallet_address']
                    }
    
                if 'selected_referrer' in st.session_state:
                    random_referrer = st.session_state.selected_referrer
                    st.write(f"Telegram ID: {random_referrer['player']}")
                    st.write(f"Username: {random_referrer['telegram_username']}")
                    st.write(f"First Name: {random_referrer['first_name']}")
                    st.write(f"Wallet Address: {random_referrer['wallet_address']}")
                    
            else:
                st.write("No referrers made referrals yesterday.")
                
        st.markdown('---', )
        with st.expander('Graphs'):
            # Assuming df_analyzed_data is your DataFrame and 'insert_d' is the date column
            df_analyzed_data['insert_d'] = pd.to_datetime(df_analyzed_data['insert_d'], errors='coerce')  # Ensure 'insert_d' is in datetime format

            # Convert pandas Timestamps to native datetime objects for use in st.slider
            min_date = df_analyzed_data['insert_d'].min().to_pydatetime()
            max_date = df_analyzed_data['insert_d'].max().to_pydatetime()

            # Create the slider for selecting the date range with native datetime objects
            start_date, end_date = st.slider(
                "Select Date Range",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
                format="YYYY-MM-DD"
            )

            # Filter the DataFrame based on the selected date range
            filtered_data = df_analyzed_data[(df_analyzed_data['insert_d'] >= pd.to_datetime(start_date)) & (df_analyzed_data['insert_d'] <= pd.to_datetime(end_date))]

            # Extract the x-values (dates) after filtering
            x = filtered_data['insert_d'].apply(lambda x: str(x).split('T')[0].split()[0]).values

            # Loop through each column for plotting
            for column in df_analyzed_data.columns:
                if column == 'insert_d':
                    continue
                try:
                    y = filtered_data[column].values
                    fig, ax = plt.subplots()
                    ax.plot(x, y)
                    ax.set_xticks(range(len(x)))  # Set tick positions
                    ax.set_xticklabels(x, rotation=90)  # Set the labels and rotate them

                    ax.set_title(f"{column} from {str(start_date).split()[0]} to {str(end_date).split()[0]}")
                    ax.set_ylabel('Count')
                    ax.set_xlabel('Date')
                    ax.grid(True)
                    st.pyplot(fig)
                except Exception as e:
                    print(e)
                    print(f'Plotting for {column} encountered an error')
                    
    

        st.markdown('---', )
        with st.expander('Extract Wallet Information'):
            wallet_address = st.text_input("Enter the wallet address")

            players_with_this_wallet_address = df_players.loc[df_players['wallet_address'] == wallet_address].reset_index()
            if len(players_with_this_wallet_address) == 0:
                pass
            else:
                st.write('Static Data')
                wins_all = 0
                amount_won = 0 
                for j in range(len(df_winners_grouped)):
                    row = df_winners_grouped.iloc[j]
                    winner_wallets = row['winner_wallets']
                    if wallet_address in winner_wallets:
                        wins = winner_wallets.count(wallet_address)
                        wins_all += wins
                        amount_won += wins * row['winners_amount']
                st.write(f'Winning predictions counts: {wins_all}')
                st.write(f'Amount won: {round(amount_won, 2)}')
                
                
                st.markdown('---')
                st.write('Players Connected to this wallet')
                st.dataframe(players_with_this_wallet_address.reset_index())
                
                st.markdown('-'*3)
                st.write('Predictions')
                for i in range(len(players_with_this_wallet_address)):
                    row = players_with_this_wallet_address.iloc[i]
                    telegram_id = row['telegram_id']
                    predictions_for_this_id = df_predictions.loc[df_predictions['player'] == telegram_id].reset_index()
                    if len(predictions_for_this_id) > 0:
                        st.write(f'Predictions for id: {telegram_id}')
                        st.dataframe(predictions_for_this_id.reset_index())
                    else:
                        st.write(f'No prediction for id: {telegram_id}')

                st.markdown('-'*3)
                st.write('Referrals')
                
                for i in range(len(players_with_this_wallet_address)):
                    row = players_with_this_wallet_address.iloc[i]
                    telegram_id = row['telegram_id']
                    referres_for_this_id = df_referrals.loc[df_referrals['referrer'] == telegram_id]
                    if len(referres_for_this_id) > 0:
                        st.write(f'Referrals for id: {telegram_id}')
                        st.dataframe(referres_for_this_id.reset_index())
                    else:
                        st.write(f'No Referrals for id: {telegram_id}')
                
                
                    
        st.markdown('---')
        with st.expander('Extract Player Information'):
            telegram_id_extract_player = st.text_input("Enter the player telegram ID")
            if telegram_id_extract_player != '':
                try:
                    telegram_id_extract_player = int(telegram_id_extract_player)
                    player_df = df_players.loc[df_players['telegram_id'] == telegram_id_extract_player].reset_index()
                    if len(player_df) == 0:
                        st.write('Player not found!')
                    else:
                        st.write('Static Data')
                        wins_all = 0
                        amount_won = 0 
                        for j in range(len(df_winners_grouped)):
                            row = df_winners_grouped.iloc[j]
                            winner_ids = row['winner_ids']
                            if telegram_id_extract_player in winner_ids:
                                wins = winner_ids.count(telegram_id_extract_player)
                                wins_all += wins
                                amount_won += wins * row['winners_amount']
                        st.write(f'Winning predictions counts: {wins_all}')
                        st.write(f'Amount won: {round(amount_won, 2)}')
                        
                        
                        st.write('Information:')
                        st.dataframe(player_df.reset_index())
                        
                        
                        player_predictions_df = df_predictions.loc[df_predictions['player'] == telegram_id_extract_player].reset_index()
                        st.markdown('---')
                        st.write('Predictions:')
                        st.dataframe(player_predictions_df.reset_index())
                except:
                    st.write('ID must be a number')
            
        del df_players, df_predictions, df_referrals
            

if __name__ == "__main__":
    main()
