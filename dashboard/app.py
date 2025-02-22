
password = 0

import psycopg2
import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import os



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
    # password = st.text_input("Enter the password", type="password")
    password = STREAMLIT_PASSWORD
    # Check if the entered password is correct
    if password == STREAMLIT_PASSWORD:
        st.write("Welcome! You have access to this page.")
        # Your protected page content goes here
        
        df_players, df_predictions, df_referrals = fetch_data()
        
        
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

        df_tmp = df_players_grouped.join(df_referrals_grouped.set_index('insert_d'), on='insert_d', lsuffix='_wallets', rsuffix='_referrals')
        df_tmp = df_tmp.join(df_predictions_grouped_wins.set_index('insert_d'), on='insert_d')
        df_tmp = df_tmp.join(df_players_joined_grouped.set_index('insert_d'), on='insert_d')
        
        total_row = {'insert_d': 'Total'}
        for column in df_tmp.columns:
            if column == 'insert_d':
                continue
            total_row[column] = df_tmp[column].sum()

        print(total_row)
        df_tmp.loc[len(df_tmp)] = total_row
        
        st.write('Analyzed Data')
        st.dataframe(df_tmp)
        
        
        # Filter only winners from predictions
        df_winners = df_predictions[df_predictions['is_win'] == 1]

        # Merge with players data to get the player accounts and wallets for winners
        df_winners_merged = df_winners.merge(df_players[['telegram_id', 'wallet_address', 'telegram_username']], 
                                             how='left', left_on='player', right_on='telegram_id')

        # st.dataframe(df_winners_merged)
        # Extracting unique winners by date
        df_winners_grouped = df_winners_merged.groupby('insert_d').agg(
            winner_accounts=('telegram_username', lambda x: list(set(x))),
            winner_wallets=('wallet_address', lambda x: list(set(x)))
        ).reset_index()
        
        # st.dataframe(df_winners_grouped)
        
        df_winners_grouped['winners_count'] = df_winners_grouped['winner_wallets'].apply(lambda x: len(x))
        
        df_winners_grouped['winners_amount'] = df_winners_grouped['winners_count'].apply(lambda x: 100.0 / float(x))
        df_winners_grouped = df_winners_grouped.loc[:, ['insert_d', 'winners_count', 'winners_amount', 'winner_accounts', 'winner_wallets']]

        # Display the result for winner accounts and wallets by date
        st.write('Winners Accounts and Wallets by Date')
        st.dataframe(df_winners_grouped)
        
        
        
        st.write('Giveaways')
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
            st.write('20$ Prize')
            if st.button("Select a Random Player from Yesterday's Predictions"):
                random_player = player_list.sample(n=1).iloc[0]
                st.write(f"Randomly selected player details:")
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
            st.write('30$ Prize')
            if st.button("Select a Random Referrer from Yesterday's Referrals"):
                random_referrer = referrer_list.sample(n=1).iloc[0]
                st.write(f"Randomly selected referrer details (Date: {random_referrer['insert_d']}):")
                st.write(f"Telegram ID: {random_referrer['telegram_id']}")
                st.write(f"Username: {random_referrer['telegram_username']}")
                st.write(f"First Name: {random_referrer['first_name']}")
                st.write(f"Wallet Address: {random_referrer['wallet_address']}")
        else:
            st.write("No referrers made referrals yesterday.")

    else:
        st.write("Invalid password. Please try again.")
        
        
    



if __name__ == "__main__":
    main()
