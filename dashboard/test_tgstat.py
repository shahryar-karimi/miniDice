import os
import unittest
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.tgstat_client import TGStatClient

class TestTGStatClient(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.client = TGStatClient(self.api_key)
        self.client.session = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {"status": "ok", "response": {}}
        self.client.session.request.return_value = self.mock_response
    
    def test_init(self):
        """Test client initialization"""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.BASE_URL, "https://api.tgstat.ru")
    
    def test_make_request(self):
        """Test _make_request method"""
        result = self.client._make_request("GET", "test/endpoint", {"param": "value"})
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/test/endpoint", 
            params={"param": "value", "token": self.api_key}
        )
        self.assertEqual(result, {"status": "ok", "response": {}})
    
    # =========================================================
    # API Stat - Channel Methods Tests
    # =========================================================
    
    def test_get_channel_info(self):
        """Test get_channel_info method"""
        self.client.get_channel_info("testchannel")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/get", 
            params={"channelId": "testchannel", "token": self.api_key}
        )
    
    def test_search_channels(self):
        """Test search_channels method"""
        self.client.search_channels("test", 20, 5, "US", "en", "news")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/search", 
            params={
                "q": "test", 
                "limit": 20, 
                "offset": 5, 
                "country": "US", 
                "language": "en", 
                "category": "news", 
                "token": self.api_key
            }
        )
    
    def test_get_channel_stats(self):
        """Test get_channel_stats method"""
        self.client.get_channel_stats("testchannel")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/stat", 
            params={"channelId": "testchannel", "token": self.api_key}
        )
    
    def test_get_channel_posts(self):
        """Test get_channel_posts method"""
        self.client.get_channel_posts("testchannel", 30, 10)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/posts", 
            params={"channelId": "testchannel", "limit": 30, "offset": 10, "token": self.api_key}
        )
    
    def test_get_channel_mentions(self):
        """Test get_channel_mentions method"""
        self.client.get_channel_mentions("testchannel", 25, 5)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/mentions", 
            params={"channelId": "testchannel", "limit": 25, "offset": 5, "token": self.api_key}
        )
    
    def test_get_channel_forwards(self):
        """Test get_channel_forwards method"""
        self.client.get_channel_forwards("testchannel", 15, 0)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/forwards", 
            params={"channelId": "testchannel", "limit": 15, "offset": 0, "token": self.api_key}
        )
    
    def test_get_channel_subscribers(self):
        """Test get_channel_subscribers method"""
        self.client.get_channel_subscribers("testchannel", "week")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/subscribers", 
            params={"channelId": "testchannel", "period": "week", "token": self.api_key}
        )
    
    def test_get_channel_avg_posts_reach(self):
        """Test get_channel_avg_posts_reach method"""
        self.client.get_channel_avg_posts_reach("testchannel", "month")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/avg-posts-reach", 
            params={"channelId": "testchannel", "period": "month", "token": self.api_key}
        )
    
    def test_get_channel_err(self):
        """Test get_channel_err method"""
        self.client.get_channel_err("testchannel")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/err", 
            params={"channelId": "testchannel", "token": self.api_key}
        )
    
    def test_get_channel_views(self):
        """Test get_channel_views method"""
        self.client.get_channel_views("testchannel", "day")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/views", 
            params={"channelId": "testchannel", "period": "day", "token": self.api_key}
        )
    
    def test_get_subscribers_graph(self):
        """Test get_subscribers_graph method"""
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        self.client.get_subscribers_graph("testchannel", start_date, end_date)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/subscribers", 
            params={
                "channelId": "testchannel", 
                "startDate": "2023-01-01", 
                "endDate": "2023-01-31", 
                "token": self.api_key
            }
        )
    
    def test_get_views_graph(self):
        """Test get_views_graph method"""
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        self.client.get_views_graph("testchannel", start_date, end_date)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/channels/views", 
            params={
                "channelId": "testchannel", 
                "startDate": "2023-01-01", 
                "endDate": "2023-01-31", 
                "token": self.api_key
            }
        )
    
    # =========================================================
    # API Stat - Post Methods Tests
    # =========================================================
    
    def test_get_post_info(self):
        """Test get_post_info method"""
        self.client.get_post_info(12345)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/posts/get", 
            params={"postId": 12345, "token": self.api_key}
        )
    
    def test_get_post_stats(self):
        """Test get_post_stats method"""
        self.client.get_post_stats(12345)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/posts/stat", 
            params={"postId": 12345, "token": self.api_key}
        )
    
    # =========================================================
    # API Search - Posts Search Methods Tests
    # =========================================================
    
    def test_search_posts(self):
        """Test search_posts method"""
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        self.client.search_posts(
            "test", 30, 10, 100, start_date, end_date, 
            True, "photo", True
        )
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/posts/search", 
            params={
                "q": "test", 
                "limit": 30, 
                "offset": 10, 
                "min_views": 100, 
                "startDate": "2023-01-01", 
                "endDate": "2023-01-31", 
                "extended": 1, 
                "media_type": "photo", 
                "exclude_forwards": 1, 
                "token": self.api_key
            }
        )
    
    def test_get_mentions_by_period(self):
        """Test get_mentions_by_period method"""
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        self.client.get_mentions_by_period("test", start_date, end_date)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/words/mentions-by-period", 
            params={
                "q": "test", 
                "startDate": "2023-01-01", 
                "endDate": "2023-01-31", 
                "token": self.api_key
            }
        )
    
    def test_get_mentions_by_channels(self):
        """Test get_mentions_by_channels method"""
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        self.client.get_mentions_by_channels("test", 40, 5, start_date, end_date)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/words/mentions-by-channels", 
            params={
                "q": "test", 
                "limit": 40, 
                "offset": 5, 
                "startDate": "2023-01-01", 
                "endDate": "2023-01-31", 
                "token": self.api_key
            }
        )
    
    # =========================================================
    # API Callback - Notification Methods Tests
    # =========================================================
    
    def test_set_callback_url(self):
        """Test set_callback_url method"""
        self.client.set_callback_url("https://example.com/callback")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/callback/set-callback-url", 
            params={"callbackUrl": "https://example.com/callback", "token": self.api_key}
        )
    
    def test_get_callback_info(self):
        """Test get_callback_info method"""
        self.client.get_callback_info()
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/callback/get-callback-info", 
            params={"token": self.api_key}
        )
    
    def test_subscribe_channel(self):
        """Test subscribe_channel method"""
        self.client.subscribe_channel("testchannel")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/callback/subscribe-channel", 
            params={"channelId": "testchannel", "token": self.api_key}
        )
    
    def test_subscribe_word(self):
        """Test subscribe_word method"""
        self.client.subscribe_word("testword")
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/callback/subscribe-word", 
            params={"word": "testword", "token": self.api_key}
        )
    
    def test_get_subscriptions_list(self):
        """Test get_subscriptions_list method"""
        self.client.get_subscriptions_list()
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/callback/subscriptions-list", 
            params={"token": self.api_key}
        )
    
    def test_unsubscribe(self):
        """Test unsubscribe method"""
        self.client.unsubscribe(123)
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/callback/unsubscribe", 
            params={"subscriptionId": 123, "token": self.api_key}
        )
    
    # =========================================================
    # Database Methods Tests
    # =========================================================
    
    def test_get_categories(self):
        """Test get_categories method"""
        self.client.get_categories()
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/database/categories", 
            params={"token": self.api_key}
        )
    
    def test_get_countries(self):
        """Test get_countries method"""
        self.client.get_countries()
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/database/countries", 
            params={"token": self.api_key}
        )
    
    def test_get_languages(self):
        """Test get_languages method"""
        self.client.get_languages()
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/database/languages", 
            params={"token": self.api_key}
        )
    
    # =========================================================
    # Usage Methods Tests
    # =========================================================
    
    def test_get_usage_stat(self):
        """Test get_usage_stat method"""
        self.client.get_usage_stat()
        self.client.session.request.assert_called_once_with(
            "GET", 
            "https://api.tgstat.ru/usage/stat", 
            params={"token": self.api_key}
        )


if __name__ == "__main__":
    unittest.main() 