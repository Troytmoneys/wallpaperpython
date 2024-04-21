import requests
import os
import json
import random
import ctypes
temp_folder = os.getenv('TEMP')
def fetch_from_google():
    """Fetches a random image using Google Custom Search JSON API."""
    import requests
    import os

    # API details
    api_key = 'your_google_api_key'
    cse_id = 'your_custom_search_engine_id'
    search_query = 'HD wallpapers'  # Modify your search query as needed
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': search_query,
        'cx': cse_id,
        'searchType': 'image',
        'num': 1,  # Number of images to return
        'start': str(random.randint(0, 10000)),
        'key': api_key
    }

    response = requests.get(url, params=params)
    results = response.json()
    image_url = results['items'][0]['link']  # Assuming there is at least one image result

    # Download the image
    image_response = requests.get(image_url)
    image_path = os.path.join(temp_folder, 'google_wallpaper.bmp')
    
    with open(image_path, 'wb') as file:
        file.write(image_response.content)

    # Set as wallpaper
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    return image_path
fetch_from_google()