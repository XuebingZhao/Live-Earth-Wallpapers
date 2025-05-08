import os
import time
from io import BytesIO
import datetime

import requests
from PIL import Image


# downloads a image from a url and return a pil Image
def download(url):
    maxtry = 3
    for i in range(maxtry):
        try:
            with requests.get(url) as response:
                return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"{i}/{maxtry} Could not download Image '{url}'...")
            time.sleep(1)


def get_project_path():
    return os.path.dirname(os.path.realpath(__file__))


def save_image(img, filename, file):
    if file is None:
        img.save(os.path.join(filename))
    else:
        img.save(os.path.join(filename,file))


def get_current_time():
    return datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
