import datetime
import json
import sys
import urllib.request
from multiprocessing.pool import ThreadPool as Pool
import time

from PIL import Image

from liewa.liewa_cli.utils import download, get_project_path


sizes = {
    "goes-16":678,
    "goes-17":678,
    "goes-18":678,
    "himawari":688,
    "gk2a":688,
    "meteosat-9":464,
    "meteosat-0deg":464,
    "meteorsat-11":464,
}

def get_time_code(sat, name):
    url = f"https://rammb-slider.cira.colostate.edu/data/json/{sat}/full_disk/{name}/latest_times.json"
    f = urllib.request.urlopen(url)
    data = json.load(f)
    latest = data["timestamps_int"][0]
    date = datetime.datetime.strptime(str(latest), "%Y%m%d%H%M%S").strftime("%Y/%m/%d")

    return latest, date


def calc_tile_coordinates(zoomLevel):
    # zoomlevel 0-3 or 0-4 (depending on the satellite)
    t_n = 2**zoomLevel
    row = range(0, t_n)
    col = range(0, t_n)
    return list(row), list(col)

def calc_scale(args,satellite):
    size = sizes[satellite]
    minimum_side = args["size"]
    scale = int(minimum_side / size / 1.2) # up scale < 120%
    return scale.bit_length()

def build_url(args,satellite,scale):
    if scale > 4:
        sys.exit("Does not support Zoom Levels greater than 4.")

    name = args["color"]
    if name == None:
        name = "natural_color"  # default color mode

    supported_args = ["geocolor", "natural_color"]
    if name not in supported_args:
        raise ValueError(
            "Wrong parameter for colorMode: Meteorsat and Goes only support 'natural_color' or 'geocolor' as colorMode!"
        )

    time_code, date = get_time_code(satellite, name)
    base_url = f"https://rammb-slider.cira.colostate.edu/data/imagery/{date}/{satellite}---full_disk/{name}/{time_code}/0{scale}"
    return base_url


def load_geostationary(args,satellite,region=None):
    scale = calc_scale(args,satellite)
    base_url = build_url(args,satellite,scale)
    row, col = calc_tile_coordinates(scale)

    tilesize = sizes[satellite]
    fullsize = tilesize * (2 ** scale)

    if region is None:
        region = [0, 0, fullsize, fullsize]
    load_region = [x * fullsize / args["size"] for x in region]

    row_col_pairs = []

    for r in row:
        if ((r+1) * tilesize <= load_region[1]) or (r * tilesize >= load_region[3]):
            continue
        for c in col:
            if ((c+1) * tilesize <= load_region[0]) or (c * tilesize >= load_region[2]):
                continue
            row_col_pairs.append([r, c])

    img_map = {}

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

    return bg


if __name__ == "__main__":
    for satellite in sizes.keys():
        size = sizes[satellite] * 8
        args = {"size": size, "color": "geocolor"}
        img = load_geostationary(args,satellite)
        img.save(f"{satellite}.png")
