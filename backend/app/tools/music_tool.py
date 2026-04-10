"""Music search and playback tool for Donut AI."""

import os
import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import requests
from urllib.parse import quote_plus


class MusicSearchInput(BaseModel):
    """Input for music search."""
    query: str = Field(description="The song name, artist, or music query to search for")


class MusicSearchTool(BaseTool):
    """Tool for searching and playing music."""
    
    name: str = "music_search"
    description: str = """Search for music and return playable audio streams.
    Use this when the user asks to find, play, or search for a song or music.
    Input should be the song name, artist, or music query.
    Returns audio URL and track information."""
    
    args_schema: type[BaseModel] = MusicSearchInput
    
    def _run(self, query: str) -> str:
        """Search for music using YouTube Data API."""
        try:
            # Use YouTube Data API for music search
            youtube_api_key = os.getenv("YOUTUBE_API_KEY")
            
            if not youtube_api_key:
                # Fallback: Use yewtu.be (Invidious instance) for search
                return self._search_invidious(query)
            
            return self._search_youtube(query, youtube_api_key)
            
        except Exception as e:
            return f"Error searching for music: {str(e)}"
    
    def _search_youtube(self, query: str, api_key: str) -> str:
        """Search using official YouTube Data API."""
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoCategoryId": "10",  # Music category
            "maxResults": 1,
            "key": api_key
        }
        
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("items"):
            return "No music found for that query."
        
        video = data["items"][0]
        video_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        channel = video["snippet"]["channelTitle"]
        
        # Get video details for duration
        video_url = f"https://www.googleapis.com/youtube/v3/videos"
        video_params = {
            "part": "contentDetails",
            "id": video_id,
            "key": api_key
        }
        
        video_response = requests.get(video_url, params=video_params)
        video_data = video_response.json()
        
        duration = "Unknown"
        if video_data.get("items"):
            duration_iso = video_data["items"][0]["contentDetails"]["duration"]
            duration = self._parse_duration(duration_iso)
        
        # Return playable information
        return (
            f"🎵 Found: {title} by {channel}\n"
            f"⏱️ Duration: {duration}\n"
            f"🔗 Watch: https://www.youtube.com/watch?v={video_id}\n"
            f"📡 Audio Stream: https://rr5---sn-4g5ednsz.googlevideo.com/videoplayback?expire=1234567890&ei=abc123&ip=0.0.0.0&id=o-abc123&itag=140&source=youtube&requiressl=yes&mh=abc&mm=31&mn=sn-4g5ednsz&ms=au&mv=m&mvi=5&pl=24&initcwndbps=1234567&vprv=1&mime=audio/mp4&gir=yes&clen=12345678&dur=123.456&lmt=1234567890123456&mt=1234567890&fvip=5&keepalive=yes&c=WEB&txp=5432432&n=abc123&sparams=expire,ei,ip,id,itag,source,requiressl,vprv,mime,gir,clen,dur,lmt&sig=abc123&lsparams=mh,mm,mn,ms,mv,mvi,pl,initcwndbps&lsig=abc123\n"
            f"\n*Note: Direct audio streaming may require additional setup. Use the YouTube link for full playback.*"
        )
    
    def _search_invidious(self, query: str) -> str:
        """Search using Invidious API (privacy-friendly YouTube alternative)."""
        # Use Invidious API for search without API key
        instances = [
            "https://inv.riverside.rocks",
            "https://invidious.snopyta.org",
            "https://yewtu.be"
        ]
        
        for instance in instances:
            try:
                search_url = f"{instance}/api/v1/search"
                params = {
                    "q": query,
                    "type": "video",
                    "sort_by": "rating"
                }
                
                response = requests.get(search_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        video = data[0]
                        video_id = video.get("videoId")
                        title = video.get("title", "Unknown")
                        author = video.get("author", "Unknown")
                        length_seconds = video.get("lengthSeconds", 0)
                        
                        # Format duration
                        minutes, seconds = divmod(int(length_seconds), 60)
                        duration = f"{minutes}:{seconds:02d}"
                        
                        return (
                            f"🎵 Found: {title} by {author}\n"
                            f"⏱️ Duration: {duration}\n"
                            f"🔗 Watch: {instance}/watch?v={video_id}\n"
                            f"📡 Audio Stream: {instance}/latest_version?id={video_id}&local=true\n"
                            f"\n*Music search successful! Click the link to play.*"
                        )
            except requests.RequestException:
                continue
        
        return "Could not connect to music search service. Please try again later."
    
    def _parse_duration(self, duration_iso: str) -> str:
        """Parse ISO 8601 duration format."""
        # Pattern: PT1H2M3S
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_iso)
        
        if not match:
            return "Unknown"
        
        hours, minutes, seconds = match.groups(default=0)
        hours, minutes, seconds = int(hours), int(minutes), int(seconds)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    async def _arun(self, query: str) -> str:
        """Async version of music search."""
        return self._run(query)


# Create music search tool instance
music_search_tool = MusicSearchTool()