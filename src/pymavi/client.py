"""Mavi API Client implementation."""

import time
from typing import List, Optional, Union, Dict, Any
import requests
from .exceptions import MaviAuthenticationError, MaviAPIError, MaviValidationError

class MaviClient:
    """Client for interacting with the Mavi Video AI Platform API.
    
    This client provides methods to interact with the Mavi API, including video upload,
    search, and management operations.
    
    Attributes:
        api_key (str): The API key for authentication
        base_url (str): The base URL for the Mavi API
        session (requests.Session): A session object for making HTTP requests
    """
    
    HOUR_SECONDS = 3600
    DEFAULT_BASE_URL = "https://mavi-backend.openinterx.com/api/serve/video/"
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize the Mavi client.
        
        Args:
            api_key (str): Your Mavi API key
            base_url (str, optional): Custom base URL for the API. Defaults to the standard URL.
        
        Raises:
            MaviValidationError: If the API key is empty or invalid
        """
        if not api_key or not isinstance(api_key, str):
            raise MaviValidationError("API key must be a non-empty string")
            
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Authorization": self.api_key})
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Mavi API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint to call
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Dict[str, Any]: JSON response from the API
            
        Raises:
            MaviAuthenticationError: If authentication fails
            MaviAPIError: If the API request fails
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise MaviAuthenticationError("Invalid API key") from e
            raise MaviAPIError(f"API request failed: {response.text}") from e
        except requests.exceptions.RequestException as e:
            raise MaviAPIError(f"Request failed: {str(e)}") from e
    
    def upload_video(
        self,
        video_name: str,
        video_path: str,
        callback_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a video to the Mavi platform.
        
        Args:
            video_name (str): Name to store the video under
            video_path (str): Path to the video file
            callback_uri (str, optional): Public callback URL for processing results
            
        Returns:
            Dict[str, Any]: Upload response containing video details
            
        Raises:
            MaviValidationError: If the video file doesn't exist or is invalid
            MaviAPIError: If the upload fails
        """
        try:
            with open(video_path, "rb") as video_file:
                files = {"file": (video_name, video_file, "video/mp4")}
                params = {"callBackUri": callback_uri} if callback_uri else None
                return self._make_request("POST", "upload", files=files, params=params)
        except FileNotFoundError:
            raise MaviValidationError(f"Video file not found: {video_path}")
    
    def search_video_metadata(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        video_status: str = "PARSE",
        range_bucket: int = 1,
        num_results: int = 10
    ) -> Dict[str, Any]:
        """Search for videos in the Mavi database.
        
        Args:
            start_time (int, optional): Start time in milliseconds since epoch
            end_time (int, optional): End time in milliseconds since epoch
            video_status (str): Status of videos to search for
            range_bucket (int): Page number for pagination
            num_results (int): Number of results per page
            
        Returns:
            Dict[str, Any]: Search results
        """
        if start_time is None:
            start_time = int((time.time() - self.HOUR_SECONDS * 24 * 7) * 1000)
        if end_time is None:
            end_time = int(time.time() * 1000)
            
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "videoStatus": video_status,
            "page": range_bucket,
            "pageSize": num_results
        }
        
        return self._make_request("GET", "searchDB", params=params)
    
    def search_video(self, search_query: str) -> Dict[str, Any]:
        """Search videos using natural language query.
        
        Args:
            search_query (str): Natural language search query
            
        Returns:
            Dict[str, Any]: Search results
        """
        data = {"searchValue": search_query}
        return self._make_request("POST", "searchAI", json=data)
    
    def search_key_clip(
        self,
        search_query: str,
        video_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Search for specific clips within videos.
        
        Args:
            search_query (str): Natural language search query
            video_ids (List[str], optional): List of video IDs to search within
            
        Returns:
            Dict[str, Any]: Search results
        """
        data = {
            "videoNos": video_ids or [],
            "searchValue": search_query
        }
        return self._make_request("POST", "searchVideoFragment", json=data)
    
    def chat_with_videos(
        self,
        video_nos: List[str],
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """Chat with an AI assistant about specific videos.
        
        Args:
            video_nos (List[str]): List of video IDs to chat about
            message (str): Message to send to the AI assistant
            history (List[Dict[str, str]], optional): Chat history for context
            stream (bool): Whether to stream the response
            
        Returns:
            Union[str, Dict[str, Any]]: AI assistant's response
        """
        data = {
            "videoNos": video_nos,
            "message": message,
            "history": history or [],
            "stream": stream
        }
        return self._make_request("POST", "chat", json=data)
    
    def delete_video(self, video_ids: List[str]) -> Dict[str, Any]:
        """Delete videos from the Mavi platform.
        
        Args:
            video_ids (List[str]): List of video IDs to delete
            
        Returns:
            Dict[str, Any]: Deletion response
        """
        return self._make_request("DELETE", "delete", json=video_ids) 