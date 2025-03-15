import requests
from typing import Dict, Any, Optional

class TGstat:
    """
    A Python wrapper for the TGstat API.
    """
    BASE_URL = "https://api.tgstat.ru"

    def __init__(self, token: str, channel_id: str):
        """
        Initializes the TGstat client.
        :param token: Your TGstat API token.
        :param channel_id: The channel/chat ID or username.
        """
        self.token = token
        self.channel_id = channel_id
    
    def get_channel_statistics(self) -> Dict[str, Any]:
        """
        Fetches statistics for the specified Telegram channel.
        :return: A dictionary containing channel statistics.
        """
        endpoint = f"{self.BASE_URL}/channels/stat"
        params = {
            "token": self.token,
            "channelId": self.channel_id
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_channel_posts(self, limit: int = 20, offset: int = 0, start_time: Optional[int] = None, 
                          end_time: Optional[int] = None, hide_forwards: int = 0, hide_deleted: int = 0, 
                          extended: int = 0) -> Dict[str, Any]:
        """
        Fetches channel posts based on specified parameters.
        :return: A dictionary containing posts data.
        """
        endpoint = f"{self.BASE_URL}/channels/posts"
        params = {
            "token": self.token,
            "channelId": self.channel_id,
            "limit": limit,
            "offset": offset,
            "startTime": start_time,
            "endTime": end_time,
            "hideForwards": hide_forwards,
            "hideDeleted": hide_deleted,
            "extended": extended
        }
        
        try:
            response = requests.get(endpoint, params={k: v for k, v in params.items() if v is not None})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_channel_stories(self, limit: int = 20, offset: int = 0, start_time: Optional[int] = None, 
                            end_time: Optional[int] = None, hide_expired: int = 0, extended: int = 0) -> Dict[str, Any]:
        """
        Fetches channel stories based on specified parameters.
        :return: A dictionary containing stories data.
        """
        endpoint = f"{self.BASE_URL}/channels/stories"
        params = {
            "token": self.token,
            "channelId": self.channel_id,
            "limit": limit,
            "offset": offset,
            "startTime": start_time,
            "endTime": end_time,
            "hideExpired": hide_expired,
            "extended": extended
        }
        
        try:
            response = requests.get(endpoint, params={k: v for k, v in params.items() if v is not None})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

