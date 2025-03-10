import os
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, ForeignKey, func, distinct, case, desc
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import plotly.graph_objects as go
import sympy as sp
from langchain_openai import ChatOpenAI
import random

# Set up the environment variables
host = os.getenv("POSTGRES_HOST")
dbname = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")

host_dashboard_db = os.getenv("POSTGRES_HOST_DASHBOARD")
dbname_dashboard = os.getenv("POSTGRES_DB_DASHBOARD")
user_dashboard = os.getenv("POSTGRES_USER_DASHBOARD")
db_password_dashboard = os.getenv("POSTGRES_PASSWORD_DASHBOARD")
port_dashboard = os.getenv("POSTGRES_PORT_DASHBOARD")


STREAMLIT_PASSWORD = os.getenv("STREAMLIT_PASSWORD")
API_KEY = os.getenv("API_KEY")
llm = ChatOpenAI(model="gpt-4o", api_key=API_KEY, temperature=0.3)


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
    player_ref = relationship("Player", backref="predictions")

class UserReferral(Base):
    __tablename__ = 'user_referral'
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('player.telegram_id'))
    referee_id = Column(Integer, ForeignKey('player.telegram_id'))
    insert_dt = Column(DateTime)
    referrer_ref = relationship("Player", backref="referrals", foreign_keys=[referrer_id])
    referee_ref = relationship("Player", backref="referred_by", foreign_keys=[referee_id])



class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.telegram_id'))
    symbol = Column(String)
    balance = Column(BigInteger)
    decimal = Column(Integer)
    

class RandomTable(Base):
    __tablename__ = 'random_table'
    id = Column(Integer, primary_key=True)
    random_value = Column(String)
    insert_dt = Column(DateTime, default=datetime.utcnow) 
    
# Create the engine and session
engine = create_engine(f'postgresql://{user}:{db_password}@{host}:{port}/{dbname}')
Session = sessionmaker(bind=engine)
session = Session()

# Create the engine and session for the dashboard database
engine_dashboard = create_engine(f'postgresql://{user_dashboard}:{db_password_dashboard}@{host_dashboard_db}:{port_dashboard}/{dbname_dashboard}')
Session_dashboard = sessionmaker(bind=engine_dashboard)
session_dashboard = Session_dashboard()

def test_db():
    # Define a new ORM class for the random table
    

    # Create the table in the dashboard database
    Base.metadata.create_all(engine_dashboard)

    # Insert a random value into the random table
    new_entry = RandomTable(random_value=str(random.randint(1, 100)))
    session_dashboard.add(new_entry)
    session_dashboard.commit()

    st.write("Inserted a new random value into the random_table.")
    
    
def show_test_db():
    test_db()
    test_db()
    # Fetch the random values from the random table
    query = session_dashboard.query(RandomTable).all()
    if query:
        st.write("🎲 **Random")
        for entry in query:
            st.write(f"Random Value: {entry.random_value}")
    else:
        st.write("😢 No random values found.")
    
# Helper function to fetch data from the database
def fetch_data(query):
    return pd.read_sql(query.statement, session.bind)

# Fetch analyzed data grouped by date
def fetch_analyzed_data_grouped_by_date():
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
    df_analyzed_data = fetch_data(result_query)
    df_analyzed_data['unique_wallets_predictions_count'] = df_analyzed_data['unique_wallets_predictions_count'].fillna(0)   

    # Fill NaN values with 0
    df_analyzed_data['count_referrals'] = df_analyzed_data['count_referrals'].fillna(0)
    df_analyzed_data['count_joined_player_noref_wallet'] = df_analyzed_data['count_joined_player_noref_wallet'].fillna(0)

    # Calculate joined without referral
    df_analyzed_data['joined_without_referral'] = df_analyzed_data['joined_players_count'] - df_analyzed_data['count_referrals']
    df_analyzed_data = df_analyzed_data.sort_values(by='insert_d').reset_index(drop=True)
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
def fetch_winners_grouped_by_date():
    query = session.query(
        func.date(Prediction.insert_dt).label('insert_dt'),
        func.count(distinct(Prediction.player_id)).label('number_of_winners'),
        func.array_agg(distinct(Player.wallet_address)).label('winners_wallet_addresses'),
        func.array_agg(distinct(Player.telegram_id)).label('winners_telegram_ids'),
        func.array_agg(distinct(Player.telegram_username)).label('winners_telegram_usernames')
    ).join(Player, Prediction.player_id == Player.telegram_id) \
     .filter(Prediction.is_win == True) \
     .group_by(func.date(Prediction.insert_dt))
    
    df = fetch_data(query)
    df['amount_per_winner'] = 100.0 / df['number_of_winners']
    return df
# Fetch data for a specific date
def fetch_data_for_date(selected_date):
    # Query players who made predictions on the selected date
    players = session.query(Player).join(Prediction).filter(func.date(Prediction.insert_dt) == selected_date).all()
    
    # Query referrals made on the selected date
    referrals = session.query(UserReferral).filter(func.date(UserReferral.insert_dt) == selected_date).all()
    
    return players, referrals

# Player giveaway function
def player_giveaway(players):
    if players:
        st.write("🎰 **20$ Prize**")
        if st.button("🎲 Select a Random Player from Selected Date's Predictions"):
            random_player = players[0]  # Simplified for demonstration
            st.session_state.selected_player = random_player

        if 'selected_player' in st.session_state:
            player = st.session_state.selected_player
            st.write(f"🆔 Telegram ID: `{player.telegram_id}`")
            st.write(f"👤 Username: `{player.telegram_username}`")
            st.write(f"📛 First Name: `{player.first_name}`")
            st.write(f"💳 Wallet Address: `{player.wallet_address}`")
    else:
        st.write("😢 No players made predictions on the selected date.")

# Referrer giveaway function
def referrer_giveaway(referrals):
    if referrals:
        st.write("🎁 **30$ Prize**")
        if st.button("🎲 Select a Random Referrer from Selected Date's Referrals"):
            random_referrer = referrals[0]  # Simplified for demonstration
            st.session_state.selected_referrer = random_referrer

        if 'selected_referrer' in st.session_state:
            referrer = st.session_state.selected_referrer
            st.write(f"🆔 Telegram ID: `{referrer.referrer_id}`")
            st.write(f"👤 Username: `{referrer.referrer_ref.telegram_username}`")
            st.write(f"📛 First Name: `{referrer.referrer_ref.first_name}`")
            st.write(f"💳 Wallet Address: `{referrer.referrer_ref.wallet_address}`")
    else:
        st.write("😢 No referrers made referrals on the selected date.")

# Main function

def create_math_function(expression, variables):
    # Create symbolic variables
    sym_vars = {var: sp.symbols(var) for var in variables}

    # Replace $var$ with the symbolic variable
    for var in variables:
        expression = expression.replace(f'${var}$', str(sym_vars[var]))

    # Parse the expression into a symbolic expression
    sym_expr = sp.sympify(expression)

    # Create a lambda function from the symbolic expression
    func = sp.lambdify(list(sym_vars.values()), sym_expr, 'numpy')

    return func


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

    # Plotting
    if st.session_state.expressions:
        fig = go.Figure()

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
                fig.add_trace(go.Scatter(
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

        fig.update_layout(
            title=f"Plotted Expressions from {fix_date(start_date)} to {fix_date(end_date)}",
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_dark",
            showlegend=True
        )

        st.plotly_chart(fig)
    else:
        st.write("No expressions saved yet. Please build and save an expression.")
        
        
def extract_wallet_information():
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
            winners_grouped = fetch_winners_grouped_by_date()
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


def extract_player_information():
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
                winners_grouped = fetch_winners_grouped_by_date()
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
                      

def fetch_random_eligible_player(min_predictions, min_wins, min_referrals):
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
def generate_success_story(player, game_description, instruction):
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

def success_story():
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
        selected_player = fetch_random_eligible_player(min_predictions, min_wins, min_referrals)
        print(selected_player)
        if not selected_player:
            st.warning("No players meet the selected criteria. Try adjusting the values.")
        else:
            # Generate a success story
            success_story = generate_success_story(selected_player, game_description, instruction)

            # Display the generated story
            st.subheader("✨ Success Story")
            st.write(success_story)




def assets_section():
    
    query = session.query(
        Asset.symbol,
        func.count(Asset.id).label('total_repeats'),
    ).group_by(Asset.symbol).order_by(desc('total_repeats'))
    
    st.write("💰 **Table of All Assets**")
    result_df = fetch_data(query)
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



def main():
    test_db()
    test_db()
    
    
    if 'auth' not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        password = st.text_input("🔑 Enter the password", type="password")
        if password == STREAMLIT_PASSWORD:
            st.session_state.auth = True
            st.rerun()
    else:
        st.title("📊 Analytics Dashboard")

        # Fetch data
        df_analyzed_data = fetch_analyzed_data_grouped_by_date()
        df_winners_grouped = fetch_winners_grouped_by_date()

        # Display data
        with st.expander("📄 Data Sheets"):
            st.write("📋 Analyzed Data")
            st.dataframe(df_analyzed_data.iloc[::-1])
            st.write("🏆 Winners Data")
            st.dataframe(df_winners_grouped)

        # Giveaways
        with st.expander("🎁 Giveaways"):
            default_date = datetime.today().date() - timedelta(days=1)
    
            # Allow user to select a custom date
            selected_date = st.date_input("Select a date", value=default_date, max_value=datetime.today().date())
            
            # Fetch data for the selected date
            players, referrals = fetch_data_for_date(selected_date)
    
            # Display player giveaway section
            st.header("Player Giveaway")
            player_giveaway(players)
            
            # Display referrer giveaway section
            st.header("Referrer Giveaway")
            referrer_giveaway(referrals)


        # Graphs
        with st.expander("📈 Graphs"):
            plot_graphs(df_analyzed_data)
            
        with st.expander("💸 Extract Wallet Information"):
            extract_wallet_information()
            
        with st.expander("👨🏻‍💼 Extract Player Information"):
            extract_player_information()
        with st.expander("🎉 Generate a Player Success Story"):
            success_story()
            
        with st.expander("🪙 Assets"):
            assets_section()
            
        with st.expander("Test"):
            show_test_db()

if __name__ == "__main__":
    main()