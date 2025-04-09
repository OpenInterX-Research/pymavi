import requests
import time
import json


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
                
        Returns:
            str: The video ID of the uploaded video
            tuple (str, str): A tuple containing the error code and message if the upload fails
        """
        
        url = self.BASE_URL + "upload"
        headers = {"Authorization": self.API_KEY}
        data = {"file": (video_name, open(video_path, "rb"), "video/mp4")}
        params = {"callBackUri": callback_URI}
        response = requests.post(url=url,files=data,params=params,headers=headers)
        content = response.json()
        
        # Check if the request was successful
        if response.status_code != 200:
            return content['code'], content['msg']
        else:
            return content['data']['videoNo']
    
    def search_video_metadata(self, start_time=int((time.time()-HOUR_SECONDS*24*7)*1000), end_time=int(time.time()*1000),
                              video_status="PARSE", page=1, num_results=20):
        """Searches the Mavi database for videos matching the given specifications.
        
        Args:
            start_time (int): The start time in milliseconds since epoch, default is 1 week ago
            end_time (int): The end time in milliseconds since epoch, default is now
            video_status (str): The status of the video, default is "PARSE" (finished processing)
            num_results (int): The number of results to return, default is 20
            page (int): The range bucket for the search, default is 1. 
                The page is which “page” of results to return. I.e., if num_results=10,
                page=2, the function will return results 10-19.
        
        Returns:
            dict: A dictionary indexed by the video IDs and containing their metadata as a dictionary
                1. videoName (str): The name of the video
                2. videoStatus (str): The status of the video
                3. uploadTime (int): The upload time of the video in milliseconds since epoch
            tuple (str, str): A tuple containing the error code and message if the search fails
        
        Example:
            search_video_metadata(start_time=int((time.time()-HOUR_SECONDS*2)*1000), end_time=int(time.time()*1000),
                                  video_status="PARSE", page=2, num_results=20)
            
            This will search for videos that were uploaded between 2 hours ago and now, that are
            finished processing, and will return results 20-39.
        """
        
        url = self.BASE_URL + "searchDB"
        headers = {"Authorization": self.API_KEY}
        params={"startTime":start_time,"endTime":end_time,"videoStatus":video_status,
                "page":page,"pageSize":num_results}
        response = requests.get(url,params=params,headers=headers)
        content = response.json()
        
        if response.status_code != 200:
            return content['code'], content['msg']
        else:
            videos = dict()
            for vid in content['data']['videoData']:
                videos[vid['videoNo']] = {
                    "videoName": vid['videoName'],
                    "videoStatus": vid['videoStatus'],
                    "uploadTime": vid['uploadTime']
                }
            return videos
    
    def search_video(self, search_query):
        """Searches all videos from a natural language query and ranks results within milliseconds.
        
        Args:
            search_query (str): The natural language query used to search the videos
            
        Returns:
            dict: A dictionary indexed by the video IDs and containing their metadata as a dictionary
                1. videoName (str): The name of the video
                2. videoStatus (str): The status of the video
                3. uploadTime (int): The upload time of the video in milliseconds since epoch
            tuple (str, str): A tuple containing the error code and message if the search fails
            
        Example:
            search_video("find me videos with cars")
            This will search for videos that have cars in them.
        """
        
        url = self.BASE_URL + "searchAI"
        headers = {"Authorization": self.API_KEY}
        data = {"searchValue": search_query}
        response = requests.post(url, json=data, headers=headers)
        content = response.json()
        
        if response.status_code != 200:
            return content['code'], content['msg']
        else:
            videos = dict()
            for vid in content['data']['videos']:
                videos[vid['videoNo']] = {
                    "videoName": vid['videoName'],
                    "videoStatus": vid['videoStatus'],
                    "uploadTime": vid['uploadTime']
                }
            return videos
                
    def search_key_clip(self, search_query, video_ids=[]):
        """Retrieves the most relevant clips within one or multiple videos provided, sorted by relevance.
        
        Args:
            video_ids (list): A list of video IDs to search within, default is an empty list to search all videos
            search_query (str): The natural language query used to search the videos
            
        Returns:
            list: A list of dictionaries containing the metadata of the clips
                1. videoNo (str): The ID of the video
                2. videoName (str): The name of the video
                3. fragmentStartTime (int): The start time of the clip in milliseconds since epoch
                4. fragmentEndTime (int): The end time of the clip in milliseconds since epoch
            tuple (str, str): A tuple containing the error code and message if the search fails
        """
        
        url = self.BASE_URL + "searchVideoFragment"
        headers = {"Authorization": self.API_KEY}
        data = {"videoNos": video_ids, "searchValue": search_query}
        response = requests.post(url, json=data, headers=headers)
        content = response.json()
        
        if response.status_code != 200:
            return content['code'], content['msg']
        else:
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
    
    def chat_with_videos(self, videoNos, message, history=[], stream=False):
        """Allows users to interact with an LLM AI assistant based on the context of one or multiple videos. 
        Additionally supports streaming these responses to minimize latency during response generation.
        
        Args:
            videoNos (list): A list of video IDs to search within
            message (str): The message to send to the AI assistant
            history (list): A list of messages to provide context to the AI assistant, default is an empty list for new conversations
            stream (bool): Whether to stream the response or not, default is False
        
        Returns:
            If stream=True: Generator yielding chunks of the response
            If stream=False: Complete response as a string
        """
        url = self.BASE_URL + "chat"
        headers = {"Authorization": self.API_KEY}
        data = {
            "videoNos": videoNos,
            "message": message,
            "history": history,
            "stream": stream
        }
                
        if stream:
            return self._stream_response(url, headers, data)
        else:
            return self._get_full_response(url, headers, data)

    def _stream_response(self, url, headers, data):
        """Helper method to handle streaming responses"""
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

    def _get_full_response(self, url, headers, data):
        """Helper method to handle non-streaming responses"""
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
        
    def transcribe_video(self, video_id, transcribe_type="AUDIO", callback_URI=""):
        """Transcription API converts visual and audio content of the video into text representations. 
        You could transcribe an uploaded video in two ways:
            AUDIO: Transcribing the video's audio content into text.
            VIDEO: Transcribing the video's visual content into text.
        

        Args:
            video_id (str): The ID of the video to transcribe
            transcribe_type (str): The type of transcription, either "AUDIO" or "VIDEO". Default is "AUDIO"
            callback_URI (str): public callback URL. Ensure that the callback URL is publicly
                accessible, as the resolution results will be sent to this address via a POST
                request.
        """
        
        url = self.BASE_URL + "subTranscription"
        headers = {"Authorization": self.API_KEY}
        data = {
            "videoNo": video_id,
            "type": transcribe_type,
            "callBackUri": callback_URI
        }
        
        response = requests.post(url, json=data, headers=headers)
        content = response.json()
        
        '''
        INCOMPLETE, IGNORE
        '''
    
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