from load_items import load_items
import sys
import os
from datetime import datetime, timedelta

DEBUG, STREAMLIT_PASSWORD, TGSTAT_APIKEY, session, session_dashboard, llm = load_items()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.tgstat_client import TGStatClient

# Initialize TGStat client
client = TGStatClient(TGSTAT_APIKEY)

# Test channel for demonstration
test_channel = "dicemaniacs"



start_date = "2025-02-16"
end_date = datetime.today().strftime("%Y-%m-%d")
# Convert start_date and end_date to timestamp
start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

print(f"Start Timestamp: {start_timestamp}")
print(f"End Timestamp: {end_timestamp}")
period = "hour"

subscribers = client.get_channel_subscribers(test_channel, start_timestamp, end_timestamp, period)
print(subscribers)
print(len(subscribers['response']))




# print("\n============= Basic Channel Information =============")
# print("Channel Info:")
# channel_info = client.get_channel_info(test_channel)
# print(channel_info)

# print("\nChannel Stats:")
# channel_stats = client.get_channel_stats(test_channel)
# print(channel_stats)

# print("\n============= Channel Content Analysis =============")
# print("Channel Posts (recent 5):")
# posts = client.get_channel_posts(test_channel, 5, 0)
# print(posts)

# print("\nChannel Mentions (recent 5):")
# mentions = client.get_channel_mentions(test_channel, 5, 0)
# print(mentions)

# print("\nChannel Forwards (recent 5):")  
# forwards = client.get_channel_forwards(test_channel, 5, 0)
# print(forwards)

# print("\n============= Channel Statistics =============")
# print("Channel Subscribers (daily):")
# subscribers = client.get_channel_subscribers(test_channel, "day")
# print(subscribers)

# print("\nChannel Views (weekly):")
# views = client.get_channel_views(test_channel, "week")
# print(views)

# print("\nChannel Average Post Reach:")
# avg_reach = client.get_channel_avg_posts_reach(test_channel)
# print(avg_reach)

# print("\nChannel Error Rate (views/subscribers ratio):")
# err_rate = client.get_channel_err(test_channel)
# print(err_rate)

# print("\n============= Search Functionality =============")
# print("Search for channels with 'dice':")
# channels_search = client.search_channels("dice", 5)
# print(channels_search)

# print("\nSearch for posts with 'dice':")
# posts_search = client.search_posts("dice", 5)
# print(posts_search)

# print("\n============= Database Information =============")
# print("Available Categories:")
# categories = client.get_categories()
# print(categories)

# print("\nAvailable Countries:")
# countries = client.get_countries()
# print(countries)

# print("\nAvailable Languages:")
# languages = client.get_languages()
# print(languages)

# print("\n============= API Usage =============")
# print("API Usage Statistics:")
# usage = client.get_usage_stat()
# print(usage)


