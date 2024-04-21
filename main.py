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

load_dotenv()

UNSPLASH_ACCESS_KEY = "ESoVUH1y2o_Ymf0D75dGwQ-5PbTFcVlCxGUezWbVonA"
PEXELS_API_KEY = "0C9jOgR1p85iMebGlpr7StHWBDy03pCUJzd1xRkeuKeg9zw0GbalHJ9F"

def create_image():
    image_path = 'icon.png'  # Adjust the path to where your icon is stored
    icon_image = Image.open(image_path)
    return icon_image


def fetch_wallpaper():
    """Fetches a random wallpaper from multiple sources."""
    source = random.choice(['unsplash', 'bing', 'pexels'])
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
    
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))
    image_path = os.path.join(temp_folder, 'wallpaper.bmp')
    image.save(image_path, 'BMP')
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    return image_path

def save_wallpaper(icon, item):
    """Saves the current wallpaper to the selected folder."""
    global current_wallpaper_path
    if current_wallpaper_path:
        base_name = os.path.basename(current_wallpaper_path)
        save_path = os.path.join(desired_folder, base_name)
        Image.open(current_wallpaper_path).save(save_path)
        print(f"Wallpaper saved to {save_path}")

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
