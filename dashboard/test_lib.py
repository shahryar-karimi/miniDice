from load_items import load_items
import sys
import os

DEBUG, STREAMLIT_PASSWORD, TGSTAT_APIKEY, session, session_dashboard, llm = load_items()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.tgstat_client import TGStatClient

client = TGStatClient(TGSTAT_APIKEY)

print("Channel Info:")
print(client.get_channel_info("dicemaniacs"))

print("Channel Stats:")
print(client.get_channel_stats("dicemaniacs"))

print("Channel Posts:")
print(client.get_channel_posts("dicemaniacs"))

print("Channel Mentions:")
print(client.get_channel_mentions("dicemaniacs"))

print("Channel Forwards:")  
print(client.get_channel_forwards("dicemaniacs"))


