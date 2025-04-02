import requests
import time


class MaviClient:
    """A client handling class for the Mavi API
    
    Attributes:
        API_KEY (str): The API key for the Mavi API
        BASE_URL (str): The base URL for the Mavi API
        HOUR_SECONDS (int): The number of seconds in an hour (3600)
    """
    
    HOUR_SECONDS = 3600
    
    def __init__(self, api_key):
        """Initializes the MaviClient with the given API key
        
        Args:
            api_key (str): The API key for the Mavi API
        """
        self.API_KEY = api_key
        self.BASE_URL = "https://mavi-backend.openinterx.com/api/serve/video/"
    
    def upload_video(self, video_name, video_path, callback_URI=""):
        """Uploads a video to the Mavi API
        
        Args:
            video_name (str): The video name to be stored in the Mavi database
            video_path (str): The path to the video file
            callback_URI (str): public callback URL. Ensure that the callback URL is publicly
                accessible, as the resolution results will be sent to this address via a POST
                request.
        """
        
        url = self.BASE_URL + "upload"
        headers = {"Authorization": self.API_KEY}
        data = {"file": (video_name, open(video_path, "rb"), "video/mp4")}
        params = {"callBackUri": callback_URI}
        print(headers, data, params)
        response = requests.post(url=url,files=data,params=params,headers=headers)
        return response.json()
    
    def search_video_metadata(self, start_time=int((time.time()-HOUR_SECONDS*24*7)*1000), end_time=int(time.time()*1000),
                              video_status="PARSE", range_bucket=1, num_results=10):
        """Searches the Mavi database for videos matching the given specifications.
        
        Args:
            start_time (int): The start time in milliseconds since epoch, default is 1 week ago
            end_time (int): The end time in milliseconds since epoch, default is now
            video_status (str): The status of the video, default is "PARSE" (finished processing)
            num_results (int): The number of results to return, default is 10
            range_bucket (int): The range bucket for the search, default is 1. 
                The range_bucket is which “page” of results to return. I.e., if num_results=10,
                range_bucket=2, the function will return results 11-20
        
        Example:
            search_video_metadata(start_time=int((time.time()-HOUR_SECONDS*2)*1000), end_time=int(time.time()*1000),
                                  video_status="PARSE", range_bucket=2, num_results=20)
            
            This will search for videos that were uploaded between 2 hours ago and now, that are
            finished processing, and will return results 21-40.
        """
        
        url = self.BASE_URL + "searchDB"
        headers = {"Authorization": self.API_KEY} # access token
        params={"startTime":start_time,"endTime":end_time,"videoStatus":video_status,
                "page":range_bucket,"pageSize":num_results}
        print(params)
        response = requests.get(url,params=params,headers=headers)
        return response.json()
    
    def search_video(self, search_query):
        """Searches all videos from a natural language query and ranks results within milliseconds.
        
        Args:
            search_query (str): The natural language query used to search the videos
            
        Example:
            search_video("find me videos with cars")
            
            This will search for videos that have cars in them.
        """
        
        url = self.BASE_URL + "searchAI"
        headers = {"Authorization": self.API_KEY}
        data = {"searchValue": search_query}
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    
    def search_key_clip(self, search_query, video_ids=[]):
        """Retrieves the most relevant clips within one or multiple videos provided, sorted by relevance.
        
        Args:
            video_ids (list): A list of video IDs to search within, default is an empty list to search all videos
            search_query (str): The natural language query used to search the videos
        """
        
        url = self.BASE_URL + "searchVideoFragment"
        headers = {"Authorization": self.API_KEY}
        data = {"videoNos": video_ids, "searchValue": search_query}
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    
    def chat_with_videos(self, videoNos, message, history=[], stream=False):
        """Allows users to interact with an LLM AI assistant based on the context of one or multiple videos. 
        Additionally supports streaming these responses to minimize latency during response generation.
        
        Args:
            videoNos (list): A list of video IDs to search within
            message (str): The message to send to the AI assistant
            history (list): A list of messages to provide context to the AI assistant, default is an empty list for new conversations
            stream (bool): Whether to stream the response or not, default is False
        """
        
        url = self.BASE_URL + "chat"
        headers = {"Authorization": self.API_KEY}
        data = {
            "videoNos": videoNos,
            "message": message,
            "history": history,
            "stream": stream
        }
        
        print(data)
        response = requests.post(url, json=data, headers=headers)
        return response.text
    
    def delete_video(self, video_ids):
        """Deletes a video from the Mavi database
        
        Args:
            video_ids (list): A list of video IDs to delete
        """
        
        url = self.BASE_URL + "delete"
        headers = {"Authorization": self.API_KEY}
        data = video_ids
        response = requests.delete(url, json=data, headers=headers)
        return response.json()