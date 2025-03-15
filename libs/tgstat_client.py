import os
import requests
from typing import Optional, Dict, Any, List
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
        print("URL:")
        print(url)
        print("Params:")
        print(params)
        response = self.session.request(method, url, params=params)
        
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"TGStat API request failed: {str(e)}")

    # Channel Methods
    def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """Get information about a channel"""
        return self._make_request('GET', 'channels/get', {'channelId': channel})
    
    def get_channel_stats(self, channel: str) -> Dict[str, Any]:
        """Get channel statistics"""
        return self._make_request('GET', 'channels/stat', {'channelId': channel})
    
    def get_channel_posts(self, channel: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get channel posts"""
        params = {
            'channelId': channel,
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'channels/posts', params)
    
    def get_channel_mentions(self, channel: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get channel mentions"""
        params = {
            'channelId': channel,
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'channels/mentions', params)
    
    def get_channel_forwards(self, channel: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get channel forwards"""
        params = {
            'channelId': channel,
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'channels/forwards', params)
    
    def get_channel_subscribers_graph(self, channel: str, start_date: Optional[datetime] = None, 
                                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get channel subscribers graph data"""
        params = {'channelId': channel}
        
        if start_date:
            params['start_date'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['end_date'] = end_date.strftime('%Y-%m-%d')
            
        return self._make_request('GET', 'channels/subscribers-graph', params)
    
    def get_channel_views_graph(self, channel: str, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get channel views graph data"""
        params = {'channel': channel}
        
        if start_date:
            params['start_date'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['end_date'] = end_date.strftime('%Y-%m-%d')
            
        return self._make_request('GET', 'channels/views-graph', params)

    # Post Methods
    def get_post_info(self, post_id: int) -> Dict[str, Any]:
        """Get information about a specific post"""
        return self._make_request('GET', 'posts/get', {'post_id': post_id})
    
    def get_post_stats(self, post_id: int) -> Dict[str, Any]:
        """Get statistics for a specific post"""
        return self._make_request('GET', 'posts/stat', {'post_id': post_id})

    # Search Methods
    def search_channels(self, q: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Search for channels"""
        params = {
            'q': q,
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'channels/search', params)
    
    def search_posts(self, q: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Search for posts"""
        params = {
            'q': q,
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', 'posts/search', params)

    # Analytics Methods
    def get_countries(self, channel: str) -> Dict[str, Any]:
        """Get channel audience geography"""
        return self._make_request('GET', 'channels/countries', {'channelId': channel})
    
    def get_languages(self, channel: str) -> Dict[str, Any]:
        """Get channel audience languages"""
        return self._make_request('GET', 'channels/languages', {'channelId': channel})
    
    def get_views_by_hours(self, channel: str) -> Dict[str, Any]:
        """Get channel views by hours"""
        return self._make_request('GET', 'channels/views-by-hours', {'channelId': channel})
    
    def get_posting_by_hours(self, channel: str) -> Dict[str, Any]:
        """Get channel posting activity by hours"""
        return self._make_request('GET', 'channels/posting-by-hours', {'channelId': channel}) 