"""Mavi API Client implementation."""

import os
import time
from typing import List, Optional, Union, Dict, Generator, Tuple, Any
import requests
import json
from .exceptions import *

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
            response = response.json()
            return response
        except json.JSONDecodeError:
            raise MaviAPIError("Failed to decode JSON response") from None
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise MaviAuthenticationError("Invalid API key") from e
            if response.status_code == 429:
                raise MaviBusySystemError("Mavi server is busy, please try again later") from e
            if response.status_code == 409:
                raise MaviDuplicateError("Duplicate request detected") from e
            if response.status_code == 403:
                raise MaviDisabledAccountError("Your account is disabled. Please contact support.") from e
            raise MaviAPIError(f"API request failed: {response.text}") from e
        except requests.exceptions.RequestException as e:
            raise MaviAPIError(f"Request failed: {str(e)}") from e
    
    def upload_video(
        self,
        video_path: str,
        callback_uri: Optional[str] = None
    ) -> Tuple[str, str]:
        """Upload a video to the Mavi platform.
        
        Args:
            video_path (str): Path to the video file
            callback_uri (str, optional): Public callback URL for processing results
            
        Returns:
            tuple: A tuple containing the video ID and the video name assigned by Mavi
            
        Raises:
            MaviValidationError: If the video file doesn't exist or is invalid
            MaviAPIError: If the upload fails
        """
        try:
            with open(video_path, "rb") as video_file:
                files = {"file": (video_file.name, video_file, "video/mp4")}
                params = {"callBackUri": callback_uri} if callback_uri else None
                content = self._make_request("POST", "upload", files=files, params=params)
                return (content['data']['videoNo'], content['data']['videoName'])
        except FileNotFoundError:
            raise MaviValidationError(f"Video file not found: {video_path}")
    
    def upload_video_from_url(
        self,
        video_url: str,
        callback_uri: Optional[str] = None
    ) -> Tuple[str, str]:
        """Upload a video from a URL to the Mavi platform.
        
        Args:
            video_url (str): URL of the video file
            callback_uri (str, optional): Public callback URL for processing results
            
        Returns:
            tuple: A tuple containing the video ID and the video name assigned by Mavi
            
        Raises:
            MaviValidationError: If the video URL is invalid
            MaviAPIError: If the upload fails
        """
        data = {
            "url": video_url,
        }
        
        params = {
            "callBackUri": callback_uri if callback_uri else None
        }            
        
        content = self._make_request("POST", "uploadUrl", json=data, params=params)
        return (content['data']['videoNo'], content['data']['videoName'])
    
    def search_video_metadata(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        video_status: Optional[str] = "PARSE",
        video_name: Optional[str] = None,
        range_bucket: Optional[int] = 1,
        num_results: Optional[int] = 10
    ) -> Dict[str, Any]:
        """Searches the Mavi database for videos matching the given specifications.
        
        Args:
            start_time (int, optional): The start time in milliseconds since epoch, default is 1 week ago
            end_time (int, optional): The end time in milliseconds since epoch, default is now
            video_status (str, optional): The status of the video, default is "PARSE" (finished processing)
            video_name (str, optional): The name of the video to search for, default is None
            num_results (int, optional): The number of results to return, default is 20
            page (int, optional): The range bucket for the search, default is 1. 
                The page is which “page” of results to return. I.e., if num_results=10,
                page=2, the function will return results 10-19.
        
        Returns:
            dict: A dictionary indexed by the video IDs and containing their metadata as a dictionary
                1. videoName (str): The name of the video
                2. videoStatus (str): The status of the video
                3. uploadTime (int): The upload time of the video in milliseconds since epoch
        
        Example:
            search_video_metadata(start_time=int((time.time()-HOUR_SECONDS*2)*1000), end_time=int(time.time()*1000),
                                  video_status="PARSE", page=2, num_results=20)
            
            This will search for videos that were uploaded between 2 hours ago and now, that are
            finished processing, and will return results 20-39.
        """
        if start_time is None:
            start_time = int((time.time() - self.HOUR_SECONDS * 24 * 7) * 1000) # 1 week ago
        if end_time is None:
            end_time = int(time.time() * 1000) # now
            
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "videoStatus": video_status,
            "videoName": video_name if video_name else None,
            "page": range_bucket,
            "pageSize": num_results
        }
        
        content = self._make_request("GET", "searchDB", params=params)
    
        videos = dict()
        for vid in content['data']['videoData']:
            videos[vid['videoNo']] = {
                "videoName": vid['videoName'],
                "videoStatus": vid['videoStatus'],
                "uploadTime": vid['uploadTime']
            }
        return videos
    
    def search_video(
        self,
        search_query: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Searches all videos from a natural language query and ranks results within milliseconds.
        
        Args:
            search_query (str): The natural language query used to search the videos
            limit (int, optional): The maximum number of results to return, default is None for all results
            
        Returns:
            dict: A dictionary indexed by the video IDs and containing their metadata as a dictionary
                1. videoName (str): The name of the video
                2. videoStatus (str): The status of the video
                3. uploadTime (int): The upload time of the video in milliseconds since epoch
            
        Example:
            search_video("find me videos with cars")
            This will search for videos that have cars in them.
        """
        data = {
            "searchValue": search_query,
            "limit": limit if limit else None
            }
        content = self._make_request("POST", "searchAI", json=data)
        videos = dict()
        for vid in content['data']['videos']:
            videos[vid['videoNo']] = {
                "videoName": vid['videoName'],
                "videoStatus": vid['videoStatus'],
                "uploadTime": vid['uploadTime']
            }
        return videos
    
    def search_key_clip(
        self,
        search_query: str,
        video_ids: List[str],
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieves the most relevant clips within one or multiple videos provided, sorted by relevance.
        
        Args:
            video_ids (list): A list of video IDs to search within, need a minimum of 1 video ID
            search_query (str): The natural language query used to search the videos
            limit (int, optional): The maximum number of results to return, default is None for all results
            
        Returns:
            list: A list of dictionaries containing the metadata of the clips
                1. videoNo (str): The ID of the video
                2. videoName (str): The name of the video
                3. fragmentStartTime (int): The start time of the clip in milliseconds since epoch
                4. fragmentEndTime (int): The end time of the clip in milliseconds since epoch
        """
        data = {
            "videoNos": video_ids,
            "searchValue": search_query,
            "limit": limit if limit else None
        }
        content = self._make_request("POST", "searchVideoFragment", json=data)
        
        clips = []
        for clip in content['data']['videos']:
            clips.append({
                "videoNo": clip['videoNo'],
                "videoName": clip['videoName'],
                "fragmentStartTime": clip['fragmentStartTime'],
                "fragmentEndTime": clip['fragmentEndTime'],
                "duration": clip['duration'],
            })
        return clips
    
    def chat_with_videos(
        self,
        video_nos: List[str],
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Chat with an AI assistant about specific videos.
        
        Args:
            video_nos (List[str]): List of video IDs to chat about
            message (str): Message to send to the AI assistant
            history (List[Dict[str, str]], optional): Chat history for context, default is None
            stream (bool, optional): Whether to stream the response, default is False
            
        Returns:
            Union[str, Generator]: The AI assistant's response or a generator for streaming responses
        """
        
        url = self.base_url + "chat"
        headers = {"Authorization": self.api_key}
            
        data = {
            "videoNos": video_nos,
            "message": message,
            "history": history or [],
            "stream": stream
        }
        if stream:
            return self._stream_response(url, headers, data)
        else:
            return self._get_full_response(url, headers, data)
    
    def _stream_response(
        self,
        url: str,
        headers: Dict[str, str],
        data: Dict[str, Any]
    ) -> Generator[str, None, None]:
        """Helper method to handle streaming responses
        
        Args:
            data (Dict[str, Any]): Data to send in the request
            
        Returns:
            Generator[str]: A generator yielding chunks of the response
        """
        try:
            response = requests.post(url, json=data, headers=headers, stream=True)
            response.raise_for_status()

            # Accumulate chunks into a buffer
            buffer = ""
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # Filter out keep-alive new chunks
                    try:
                        # Decode the chunk as UTF-8 and add it to the buffer
                        decoded_chunk = chunk.decode('utf-8').strip()
                        buffer += decoded_chunk
                        
                        # Remove the "data:" prefix if it exists
                        if buffer.startswith("data:"):
                            buffer = buffer[5:].strip()

                        # Attempt to parse the buffer as JSON
                        while True:
                            try:
                                json_data, index = json.JSONDecoder().raw_decode(buffer)
                                buffer = buffer[index:].strip()  # Remove the parsed part from the buffer
                                # Process JSON data
                                if json_data.get('code') != '0000':
                                    return json_data.get('code', ""), json_data.get('msg', "")
                                else:
                                    yield json_data.get('data', {}).get('msg', "")
                            except json.JSONDecodeError:
                                # Wait for more chunks if JSON is incomplete
                                break
                    except UnicodeDecodeError:
                        continue # Skip invalid UTF-8 sequences
        except requests.exceptions.RequestException as e:
            return e
        finally:
            if 'response' in locals():
                response.close()
    
    def _get_full_response(
        self,
        url: str,
        headers: Dict[str, str],
        data: Dict[str, Any]
    ) -> str:
        """Helper method to handle non-streaming responses
        
        Args:
            data (Dict[str, Any]): Data to send in the request
            
        Returns:
            str: The full response from the AI assistant
        """
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            # Remove the "data:" prefix if it exists
            if response.text.startswith("data:"):
                content = response.text[5:].strip()
            else:
                content = response.text
            content = json.loads(content)
            if content.get('code') != '0000':
                return content.get('code', ""), content.get('msg', "")
            else:
                return content.get('data', {}).get('msg', "")
        except requests.exceptions.RequestException as e:
            return e
        
    def transcribe_video(
        self, 
        video_id: str, 
        transcribe_type: str = "AUDIO", 
        callback_uri: Optional[str] = None
    ) -> str:
        """Transcription API converts visual and audio content of the video into text representations. 
        You can transcribe an uploaded video in two ways:
            AUDIO: Transcribing the video's audio content into text.
            VIDEO: Transcribing the video's visual content into text.
        

        Args:
            video_id (str): The ID of the video to transcribe
            transcribe_type (str): The type of transcription, either "AUDIO" or "VIDEO". Default is "AUDIO"
            callback_uri (str, optional): public callback URL. Ensure that the callback URL is publicly
                accessible, as the resolution results will be sent to this address via a POST
                request.
                
        Returns:
            str: The task ID for the transcription request
        """
        
        data = {
            "videoNo": video_id,
            "type": transcribe_type,
            "callBackUri": callback_uri if callback_uri else None
        }
                
        content = self._make_request("POST", "subTranscription", json=data)      
        print(content)  
        return content['data']['taskNo']
    
    def get_transcription(
        self,
        taskNo: str
    ) -> Dict[str, Any]:
        """Get the transcription results for a given task ID.
        
        Args:
            taskNo (str): The task ID for the transcription request
            
        Returns:
            Dict[str, Any]: The transcription results in the format:
                {
                    "status": ("FINISHED" or "UNFINISHED"),
                    "type": ("AUDIO" or "VIDEO"),
                    "videoNo": video_id,
                    "taskNo": taskNo,
                    "transcriptions": [
                        {
                            "id": transcription_id,
                            "startTime": start_time,
                            "endTime": end_time,
                            "content": transcription_text
                        },
                        ...
                    ]
                }
        """
        params = {
            "taskNo": taskNo
        }
        
        content = self._make_request("GET", "getTranscription", params=params)      
        return content['data']
    
    def delete_video(
        self,
        video_ids: List[str]
    ) -> None:
        """Delete videos from the Mavi platform.
        
        Args:
            video_ids (List[str]): List of video IDs to delete
            
        Returns:
            None
        """
        self._make_request("DELETE", "delete", json=video_ids)
        