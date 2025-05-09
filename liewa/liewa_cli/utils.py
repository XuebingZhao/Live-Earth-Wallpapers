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
        img.save(os.path.join(filename, file))


def get_time_str(in_time=None):
    if in_time is None:
        return datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
    else:
        # convert to local timezone
        local_timezone = datetime.datetime.now().astimezone().tzinfo
        in_time = in_time.astimezone(local_timezone)
        return in_time.strftime('%Y%m%d_%H%M%S')


def manage_backups(img, utc_time=None):
    backup_folder_path = os.path.join(get_project_path(), "recources", "backup")
    if not os.path.exists(backup_folder_path):
        os.makedirs(backup_folder_path)

    backup_file_name = os.path.join(backup_folder_path, f"{get_time_str(utc_time)}.jpg")
    img.save(backup_file_name, 'JPEG', quality=95)

    max_backups = 70 * 24 * 2  # 70 days of backups
    # max_backups = 100  # 100 backups max
    files = [f for f in os.listdir(backup_folder_path) if os.path.isfile(os.path.join(backup_folder_path, f))]
    if len(files) > max_backups:
        files.sort()
        for file in files[0:-max_backups]:
            os.remove(os.path.join(backup_folder_path, file))
