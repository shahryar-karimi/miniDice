import os
import requests
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta

class TGStatClient:
    """
    TGStat API Client for interacting with the TGStat API
    Documentation: https://api.tgstat.ru/docs/ru/start/intro.html
    """
    
    BASE_URL = "https://api.tgstat.ru"
    
    def __init__(self, api_key: str):
        """Initialize TGStat API client with API key"""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the TGStat API"""
        if params is None:
            params = {}
            
        # Add API token to params
        params['token'] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"

        print('===============================================')
        print(f"URL: {url}")
        print(f"Params: {params}")
        print('===============================================')
        
        response = self.session.request(method, url, params=params)
        
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_details = {}
            try:
                error_details = response.json()
            except:
                pass
            raise Exception(f"TGStat API request failed: {str(e)}, Details: {error_details}")

    # =========================================================
    # API Stat - Channel Methods
    # =========================================================
    
    def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """
        Get information about a channel
        
        Args:
            channel: Channel username without @ or channel ID
            
        Returns:
            Channel information
        """
        return self._make_request('GET', 'channels/get', {'channelId': channel})
    
    def search_channels(self, q: str, limit: int = 50, offset: int = 0, 
                       country: str = None, language: str = None, category: str = None) -> Dict[str, Any]:
        """
        Search for channels by query
        
        Args:
            q: Search query
            limit: Results limit (default: 50, max: 1000)
            offset: Results offset
            country: Filter by country code
            language: Filter by language code
            category: Filter by category ID
            
        Returns:
            Search results
        """
        params = {
            'q': q,
            'limit': limit,
            'offset': offset
        }
        
        if country:
            params['country'] = country
        if language:
            params['language'] = language
        if category:
            params['category'] = category
            
        return self._make_request('GET', 'channels/search', params)
    
    def get_channel_stats(self, channel: str) -> Dict[str, Any]:
        """
        Get channel statistics
        
        Args:
            channel: Channel username without @ or channel ID
            
        Returns:
            Channel statistics
        """
        return self._make_request('GET', 'channels/stat', {'channelId': channel})
    
    def get_channel_posts(self, channel: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get channel posts
        
        Args:
            channel: Channel username without @ or channel ID
            limit: Results limit (default: 50, max: 1000)
            offset: Results offset
            
        Returns:
            Channel posts
        """
        params = {
            'channelId': channel,
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'channels/posts', params)
    
    def get_channel_mentions(self, channel: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get channel mentions
        
        Args:
            channel: Channel username without @ or channel ID
            limit: Results limit (default: 50, max: 1000)
            offset: Results offset
            
        Returns:
            Channel mentions
        """
        params = {
            'channelId': channel,
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'channels/mentions', params)
    
    def get_channel_forwards(self, channel: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get channel forwards
        
        Args:
            channel: Channel username without @ or channel ID
            limit: Results limit (default: 50, max: 1000)
            offset: Results offset
            
        Returns:
            Channel forwards
        """
        params = {
            'channelId': channel,
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'channels/forwards', params)
    
    def get_channel_subscribers(self, channel: str, startDate: str = None, endDate: str = None, group: str = "day") -> Dict[str, Any]:
        """
        Get channel subscribers statistics
        
        Args:
            channel: Channel username without @ or channel ID
            period: Period for statistics (day, week, month)
            
        Returns:
            Channel subscribers statistics
        """
        params = {
            'channelId': channel,
            'group': group
        }
        
        if startDate:
            params['startDate'] = startDate
        if endDate:
            params['endDate'] = endDate
            
        return self._make_request('GET', 'channels/subscribers', params)
    
    def get_channel_avg_posts_reach(self, channel: str, period: str = "week") -> Dict[str, Any]:
        """
        Get channel average posts reach
        
        Args:
            channel: Channel username without @ or channel ID
            period: Period for statistics (day, week, month)
            
        Returns:
            Channel average posts reach
        """
        params = {
            'channelId': channel,
            'period': period
        }
        return self._make_request('GET', 'channels/avg-posts-reach', params)
    
    def get_channel_err(self, channel: str) -> Dict[str, Any]:
        """
        Get channel error rate (ratio of views to subscribers)
        
        Args:
            channel: Channel username without @ or channel ID
            
        Returns:
            Channel error rate
        """
        return self._make_request('GET', 'channels/err', {'channelId': channel})
    
    def get_channel_views(self, channel: str, period: str = "week") -> Dict[str, Any]:
        """
        Get channel views statistics
        
        Args:
            channel: Channel username without @ or channel ID
            period: Period for statistics (day, week, month)
            
        Returns:
            Channel views statistics
        """
        params = {
            'channelId': channel,
            'period': period
        }
        return self._make_request('GET', 'channels/views', params)
    
    def get_subscribers_graph(self, channel: str, startDate: Optional[datetime] = None, 
                            endDate: Optional[datetime] = None, group: str = "day") -> Dict[str, Any]:
        """
        Get channel subscribers graph data
        
        Args:
            channel: Channel username without @ or channel ID
            startDate: Start date (format: YYYY-MM-DD)
            endDate: End date (format: YYYY-MM-DD)
            group: Grouping results (hour, day, week, month)
            
        Returns:
            Channel subscribers graph data
        """
        params = {'channelId': channel, 'group': group}
        
        if startDate:
            params['startDate'] = startDate.strftime('%Y-%m-%d')
        if endDate:
            params['endDate'] = endDate.strftime('%Y-%m-%d')
            
        return self._make_request('GET', 'channels/subscribers', params)
    
    def get_views_graph(self, channel: str, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get channel views graph data
        
        Args:
            channel: Channel username without @ or channel ID
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)
            
        Returns:
            Channel views graph data
        """
        params = {'channelId': channel}
        
        if start_date:
            params['startDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
            
        return self._make_request('GET', 'channels/views', params)
    
    # =========================================================
    # API Stat - Post Methods
    # =========================================================
    
    def get_post_info(self, post_id: int) -> Dict[str, Any]:
        """
        Get information about a specific post
        
        Args:
            post_id: Post ID
            
        Returns:
            Post information
        """
        return self._make_request('GET', 'posts/get', {'postId': post_id})
    
    def get_post_stats(self, post_id: int) -> Dict[str, Any]:
        """
        Get statistics for a specific post
        
        Args:
            post_id: Post ID
            
        Returns:
            Post statistics
        """
        return self._make_request('GET', 'posts/stat', {'postId': post_id})
    
    # =========================================================
    # API Search - Posts Search Methods
    # =========================================================
    
    def search_posts(self, q: str, limit: int = 50, offset: int = 0, 
                    min_views: int = None, start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None, extended: bool = False,
                    media_type: str = None, exclude_forwards: bool = False) -> Dict[str, Any]:
        """
        Search for posts
        
        Args:
            q: Search query
            limit: Results limit (default: 50, max: 1000)
            offset: Results offset
            min_views: Minimum views count
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)
            extended: Get extended information
            media_type: Filter by media type (text, photo, video, document, audio)
            exclude_forwards: Exclude forwards from search results
            
        Returns:
            Search results
        """
        params = {
            'q': q,
            'limit': limit,
            'offset': offset
        }
        
        if min_views:
            params['min_views'] = min_views
        if start_date:
            params['startDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
        if extended:
            params['extended'] = 1
        if media_type:
            params['media_type'] = media_type
        if exclude_forwards:
            params['exclude_forwards'] = 1
            
        return self._make_request('GET', 'posts/search', params)
    
    def get_mentions_by_period(self, q: str, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get mentions by period
        
        Args:
            q: Search query
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)
            
        Returns:
            Mentions by period
        """
        params = {'q': q}
        
        if start_date:
            params['startDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
            
        return self._make_request('GET', 'words/mentions-by-period', params)
    
    def get_mentions_by_channels(self, q: str, limit: int = 50, offset: int = 0,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get mentions by channels
        
        Args:
            q: Search query
            limit: Results limit (default: 50, max: 1000)
            offset: Results offset
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)
            
        Returns:
            Mentions by channels
        """
        params = {
            'q': q,
            'limit': limit,
            'offset': offset
        }
        
        if start_date:
            params['startDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
            
        return self._make_request('GET', 'words/mentions-by-channels', params)
    
    # =========================================================
    # API Callback - Notification Methods
    # =========================================================
    
    def set_callback_url(self, callback_url: str) -> Dict[str, Any]:
        """
        Set callback URL for notifications
        
        Args:
            callback_url: URL to receive notifications
            
        Returns:
            Operation status
        """
        return self._make_request('GET', 'callback/set-callback-url', {'callbackUrl': callback_url})
    
    def get_callback_info(self) -> Dict[str, Any]:
        """
        Get information about configured callback
        
        Returns:
            Callback information
        """
        return self._make_request('GET', 'callback/get-callback-info')
    
    def subscribe_channel(self, channel: str) -> Dict[str, Any]:
        """
        Subscribe to channel notifications
        
        Args:
            channel: Channel username without @ or channel ID
            
        Returns:
            Subscription status
        """
        return self._make_request('GET', 'callback/subscribe-channel', {'channelId': channel})
    
    def subscribe_word(self, word: str) -> Dict[str, Any]:
        """
        Subscribe to keyword notifications
        
        Args:
            word: Keyword to subscribe
            
        Returns:
            Subscription status
        """
        return self._make_request('GET', 'callback/subscribe-word', {'word': word})
    
    def get_subscriptions_list(self) -> Dict[str, Any]:
        """
        Get list of active subscriptions
        
        Returns:
            List of subscriptions
        """
        return self._make_request('GET', 'callback/subscriptions-list')
    
    def unsubscribe(self, subscription_id: int) -> Dict[str, Any]:
        """
        Unsubscribe from notifications
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Operation status
        """
        return self._make_request('GET', 'callback/unsubscribe', {'subscriptionId': subscription_id})
    
    # =========================================================
    # Database Methods
    # =========================================================
    
    def get_categories(self) -> Dict[str, Any]:
        """
        Get list of available categories
        
        Returns:
            List of categories
        """
        return self._make_request('GET', 'database/categories')
    
    def get_countries(self) -> Dict[str, Any]:
        """
        Get list of available countries
        
        Returns:
            List of countries
        """
        return self._make_request('GET', 'database/countries')
    
    def get_languages(self) -> Dict[str, Any]:
        """
        Get list of available languages
        
        Returns:
            List of languages
        """
        return self._make_request('GET', 'database/languages')
    
    # =========================================================
    # Usage Methods
    # =========================================================
    
    def get_usage_stat(self) -> Dict[str, Any]:
        """
        Get usage statistics
        
        Returns:
            Usage statistics
        """
        return self._make_request('GET', 'usage/stat') 