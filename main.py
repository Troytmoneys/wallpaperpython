import os
import random
import requests
import ctypes
from pystray import MenuItem as item
from pystray import Icon as icon
from PIL import Image, ImageDraw
from io import BytesIO
from dotenv import load_dotenv
import webbrowser
import tkinter as tk
from tkinter import filedialog
from shutil import copyfile
load_dotenv()

UNSPLASH_ACCESS_KEY = "ESoVUH1y2o_Ymf0D75dGwQ-5PbTFcVlCxGUezWbVonA"
PEXELS_API_KEY = "0C9jOgR1p85iMebGlpr7StHWBDy03pCUJzd1xRkeuKeg9zw0GbalHJ9F"

def create_image():
    image_path = 'icon.png'  # Adjust the path to where your icon is stored
    icon_image = Image.open(image_path)
    return icon_image


def fetch_wallpaper():
    """Fetches a random wallpaper from multiple sources."""
    source = random.choice(['unsplash', 'bing', 'pexels', 'bingimages', 'googleimages'])
    if source == 'unsplash':
        url = f'https://api.unsplash.com/photos/random?client_id={UNSPLASH_ACCESS_KEY}'
        response = requests.get(url)
        image_url = response.json()['urls']['full']
    elif source == 'bing':
        url = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US'
        response = requests.get(url)
        image_url = 'https://www.bing.com' + response.json()['images'][0]['url']
    elif source == 'pexels':
        headers = {'Authorization': PEXELS_API_KEY}
        url = 'https://api.pexels.com/v1/curated'
        response = requests.get(url, headers=headers)
        image_url = random.choice(response.json()['photos'])['src']['original']
    elif source == 'bingimages':
        image_url = fetch_from_bing()
        print("bingimages")
    elif source == 'googleimages':
        imageurl = fetch_from_google()
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))
    image_path = os.path.join(temp_folder, 'wallpaper.bmp')
    image.save(image_path, 'BMP')
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    return image_path



def save_wallpaper(icon, item):
    """Saves the current wallpaper to the selected folder using a save file dialog."""
    root = tk.Tk()
    root.withdraw()  # Hides the main window

    # Set the default filename and file type filters
    file_path = filedialog.asksaveasfilename(
        defaultextension='.bmp',
        filetypes=[('Bitmap', '*.bmp'), ('JPEG', '*.jpg'), ('PNG', '*.png')],
        title="Save Wallpaper As"
    )

    root.destroy()

    if file_path:
        current_wallpaper_path = r'C:\Users\Troy\AppData\Local\Temp\wallpaper.bmp'
        if current_wallpaper_path:
            try:
                # Copy the current wallpaper to the selected path
                from shutil import copyfile
                copyfile(current_wallpaper_path, file_path)
                print(f"Wallpaper saved to {file_path}")
            except Exception as e:
                print(f"Failed to save wallpaper: {e}")

def open_about(icon, item):
    """Creates and displays an about page using tkinterweb."""
    webbrowser.open("google.com")

def exit_application(icon, item):
    """Exits the application."""
    icon.stop()

temp_folder = os.getenv('TEMP')
desired_folder = os.path.join(os.path.expanduser('~'), 'Saved Wallpapers')
os.makedirs(desired_folder, exist_ok=True)
current_wallpaper_path = None

menu = (
    item('Next Wallpaper', lambda icon, item: fetch_wallpaper()),
    item('Save Wallpaper', save_wallpaper),
    item('About', open_about),
    item('Exit', exit_application),
)

icon('TestIcon', create_image(), menu=menu).run()
def fetch_from_bing():
    """Fetches a random wallpaper using the Bing Image Search API."""
   

    # API details and endpoint
    api_key = '71fc3e3de595452597df8c3aedc25e95'
    endpoint = 'https://api.bing.microsoft.com/v7.0/images/search'
    headers = {'Ocp-Apim-Subscription-Key': api_key}
    params = {
        "q": "HD wallpapers",  # Search query for wallpapers
        "count": str(random.randint(0, 10000)),          # Number of results to return
        "offset": "0",         # Result offset for pagination
        "imageType": "Photo",
        "mkt": "en-US"
    }

    response = requests.get(endpoint, headers=headers, params=params)
    image_info = response.json()['value'][0]  # Assuming there is at least one result

    # Fetch the image
    image_url = image_info['contentUrl']
    image_response = requests.get(image_url)
    image_path = os.path.join(temp_folder, 'bing_wallpaper.bmp')
    
    with open(image_path, 'wb') as file:
        file.write(image_response.content)

    # Set as wallpaper
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    return image_path
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