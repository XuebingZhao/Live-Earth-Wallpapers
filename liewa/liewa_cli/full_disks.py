import datetime
import json
import sys
import os
import urllib.request
from multiprocessing.pool import ThreadPool as Pool
import time

from PIL import Image

from liewa.liewa_cli.utils import download, get_project_path


sizes = {
    "goes-16": 678,
    "goes-17": 678,
    "goes-18": 678,
    "himawari": 688,
    "gk2a": 688,
    "meteosat-9": 464,
    "meteosat-0deg": 464,
    # "meteosat-11":464,
}


def get_time_code(satellite, name):
    url = f"https://rammb-slider.cira.colostate.edu/data/json/{satellite}/full_disk/{name}/latest_times.json"
    f = urllib.request.urlopen(url)
    data = json.load(f)
    latest = data["timestamps_int"][0]
    date = datetime.datetime.strptime(str(latest), "%Y%m%d%H%M%S").strftime("%Y/%m/%d")

    return latest, date


def calc_tile_coordinates(zoom_level):
    # zoomlevel 0-3 or 0-4 (depending on the satellite)
    t_n = 2**zoom_level
    row = range(0, t_n)
    col = range(0, t_n)
    return list(row), list(col)


def calc_scale(satellite, **kwargs):
    size = sizes[satellite]
    minimum_side = kwargs.get("size", 1024)
    scale = int(minimum_side / size / 1.2)  # up scale < 120%

    scale = max(min(scale.bit_length(), 4), 0)   # log_2 scale between 0-4
    if satellite.lower().startswith("meteosat") and scale == 4:
        scale = 3  # Meteosat 9 and 0deg only support up to 8x zoom

    return scale


def build_url(satellite, scale, **kwargs):
    if scale > 4:
        sys.exit("Does not support Zoom Levels greater than 4.")

    name = kwargs.get("color", "natural_color")
    supported_args = ["geocolor", "natural_color"]
    if name not in supported_args:
        raise ValueError(
            "Wrong parameter for colorMode: Meteorsat and Goes only support 'natural_color' or 'geocolor' as colorMode!"
        )

    time_code = kwargs.get("time_code", None)
    if time_code is None:
        time_code, date = get_time_code(satellite, name)
    else:
        time_code = str(time_code)
        date = f"{time_code[0:4]}/{time_code[4:6]}/{time_code[6:8]}"
    base_url = f"https://ik.imagekit.io/stevenzc/tr:q-95,f-jpg/https://rammb-slider.cira.colostate.edu/data/imagery/{date}/{satellite}---full_disk/{name}/{time_code}/0{scale}"
    return base_url


def load_geostationary(satellite, region=None, overlay_border=True, **kwargs):
    scale = calc_scale(satellite, **kwargs)
    base_url = build_url(satellite, scale, **kwargs)
    row, col = calc_tile_coordinates(scale)

    tilesize = sizes[satellite]
    fullsize = tilesize * (2 ** scale)
    tgt_size = kwargs.get("size", 1024)

    if region is None:
        region = [0, 0, fullsize, fullsize]

    if len(region) == 4 and all(isinstance(x, (int, float)) for x in region):
        load_region = [x * fullsize / tgt_size for x in region]

        row_col_pairs = []

        for r in row:
            if ((r+1) * tilesize <= load_region[1]) or (r * tilesize >= load_region[3]):
                continue
            for c in col:
                if ((c+1) * tilesize <= load_region[0]) or (c * tilesize >= load_region[2]):
                    continue
                row_col_pairs.append([r, c])

    elif all(isinstance(x, list) and all(isinstance(y, int) for y in x) and len(x) == 2 for x in region):
        row_col_pairs = region
    else:
        raise ValueError("Invalid region parameter.")

    img_map = {}
    print(f"Downloading {len(row_col_pairs)} images...")

    def download_func(row_col):
        r = row_col[0]
        c = row_col[1]
        url = base_url + f"/{str(r).zfill(3)}_{str(c).zfill(3)}.png"
        print(f"Downloading Image ({r},{c}).{url}")
        img = download(url)
        # store the images in a dict so we don't have to care about the order they're downloaded in
        img_map[str(r) + ":" + str(c)] = img
        return img

    start = time.time()

    with Pool(len(row_col_pairs)) as pool:
        pool.map(download_func, row_col_pairs)
        print("Stiching images...")

    # stich the images together based on the position in the grid.
    bg = Image.new("RGB", (tilesize * (max(col) + 1), tilesize * (max(row) + 1)))
    for r, c in row_col_pairs:
        img = img_map[str(r) + ":" + str(c)]
        bg.paste(img, (img.width * (c), (r) * img.height))

    end = time.time()
    print("Downloads took: ", end - start)

    if overlay_border:
        overlay_path = os.path.join(get_project_path(), "recources", f"border_{satellite}_{scale:02d}.png")
        if os.path.exists(overlay_path):
            overlay = Image.open(overlay_path).convert('RGBA')
            bg.paste(overlay, (0, 0), overlay)

    return bg


if __name__ == "__main__":
    for sat in sizes.keys():
        img_size = sizes[sat] * 2
        args = {"size": img_size, "color": "geocolor"}
        image = load_geostationary(sat, overlay_border=False, **args)
        image.save(f"{sat}.png")
