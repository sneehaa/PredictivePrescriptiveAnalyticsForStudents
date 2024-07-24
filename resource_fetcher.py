import re
import requests
import xml.etree.ElementTree as ET

# Function to fetch YouTube video ID from video link
def get_video_id(video_link):
    pattern = r"(?<=v=|\/videos\/|embed\/|youtu.be\/|\/v\/|\/e\/|watch\?v=|&v=|%2Fv%2F|youtu.be%2F|embed%2F|v=)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, video_link)
    if match:
        return match.group(1)
    return None

# Function to fetch YouTube videos based on subject
def fetch_youtube_videos(subject):
    api_key = 'AIzaSyDaRS1e-NgFlogsNNr1ilAxEhr3nU_T5AM'
    search_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={subject}&type=video&key={api_key}'
    response = requests.get(search_url)
    videos = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get('items', []):
            video_id = item['id']['videoId']
            videos.append({
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'link': f"https://www.youtube.com/watch?v={video_id}",
                'subject': subject,
                'learning_style': 'Visual',
                'resource_type': 'video'
            })
    return videos

# Function to fetch research papers based on subject (example uses arXiv API)
def fetch_research_papers(subject):
    search_url = f'http://export.arxiv.org/api/query?search_query=all:{subject}&start=0&max_results=5'
    response = requests.get(search_url)
    papers = []
    if response.status_code == 200:
        data = response.text
        root = ET.fromstring(data)
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
            link = entry.find('{http://www.w3.org/2005/Atom}id').text
            papers.append({
                'title': title,
                'description': summary,
                'link': link,
                'subject': subject,
                'learning_style': 'Reading/Writing',
                'resource_type': 'paper'
            })
    return papers

# Function to fetch books based on subject (example uses Google Books API)
def fetch_books(subject):
    api_key = 'AIzaSyASAQx7yIYq1o1AA-Jcl-czctHNjr1wNjg'
    search_url = f'https://www.googleapis.com/books/v1/volumes?q={subject}&key={api_key}'
    response = requests.get(search_url)
    books = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get('items', []):
            volume_info = item['volumeInfo']
            thumbnail_url = volume_info['imageLinks']['thumbnail'] if 'imageLinks' in volume_info else None
            books.append({
                'title': volume_info.get('title'),
                'description': volume_info.get('description'),
                'link': volume_info.get('infoLink'),
                'thumbnail': thumbnail_url,
                'subject': subject,
                'learning_style': 'In-person',
                'resource_type': 'book'
            })
    return books
