import os
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()

def load_items():
    DEBUG = os.getenv("DEBUG")
    DEBUG = DEBUG.lower() == 'true'
    print(DEBUG)
    # Set up environment variables
    host = os.getenv("POSTGRES_HOST")
    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    port = os.getenv("POSTGRES_PORT")
    # Database setup (unchanged)
    engine = create_engine(f'postgresql://{user}:{db_password}@{host}:{port}/{dbname}')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    if not DEBUG:
        host_dashboard_db = os.getenv("POSTGRES_HOST_DASHBOARD")
        dbname_dashboard = os.getenv("POSTGRES_DB_DASHBOARD")
        user_dashboard = os.getenv("POSTGRES_USER_DASHBOARD")
        db_password_dashboard = os.getenv("POSTGRES_PASSWORD_DASHBOARD")
        port_dashboard = os.getenv("POSTGRES_PORT_DASHBOARD")
        engine_dashboard = create_engine(f'postgresql://{user_dashboard}:{db_password_dashboard}@{host_dashboard_db}:{port_dashboard}/{dbname_dashboard}')
        Session_dashboard = sessionmaker(bind=engine_dashboard)
        session_dashboard = Session_dashboard()
        Base.metadata.drop_all(engine_dashboard)
        Base.metadata.create_all(engine_dashboard)
    else:
        session_dashboard = None
        
        
    STREAMLIT_PASSWORD = os.getenv("STREAMLIT_PASSWORD")
    API_KEY = os.getenv("API_KEY")
    llm = ChatOpenAI(model="gpt-4o", api_key=API_KEY, temperature=0.3)        

    
    return DEBUG, STREAMLIT_PASSWORD, session, session_dashboard, llm    
    