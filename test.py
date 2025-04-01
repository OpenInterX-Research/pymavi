import os
from dotenv import load_dotenv
from maviclient import MaviClient

load_dotenv()

# Example usage
# get API key from environment variable
API_KEY = os.environ["MAVI_API_KEY"]
if API_KEY is None:
    raise ValueError("Please set the MAVI_API_KEY environment variable.")
client = MaviClient(API_KEY)
# print(client.upload_video("olympicRacer.mp4", "olympicRacer.mp4"))
print(client.search_video_metadata(video_status="PARSE"))
# print(client.search_video("Olympic athletes, running"))
# print(client.search_key_clip("athletes running", video_ids=['mavi_video_561730031559114752']))
# print(client.chat_with_videos(['mavi_video_561730031559114752'], "what is the video about?"))
# print(client.delete_video(['mavi_video_561730031559114752', 'mavi_video_558893484480659456',
#                            'mavi_video_555897793483374592', 'mavi_video_555515666648530944', 'mavi_video_555514752994902016',
#                            'mavi_video_554484858886291456', 'mavi_video_554480728872583168', 'mavi_video_554057974939648000',
#                            'mavi_video_554047521157021696']))
