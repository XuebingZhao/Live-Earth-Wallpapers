import numpy as np
import io
from rasterio.transform import from_origin, from_bounds
from rasterio.crs import CRS
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.plot import show
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PIL import Image

from liewa.liewa_cli.full_disks import load_geostationary

long_0 = {
    'goes-16': -75.0,
    'goes-18': -137.0,
    'himawari': 140.7,
    'gk2a': 128.2,
    'meteosat-9': 45.5,
    'meteosat-0deg': 0.0,
}

scale_factor = {
    "goes-16": 1.0,
    "goes-18": 1.0,
    "himawari": 0.9874,
    "gk2a": 0.9856,
    "meteosat-9": 0.9765,
    "meteosat-0deg": 0.9765,
}

# "plot_projection" shound be the same as "dst_crs"
dst_crs_string = '+proj=aea +lat_1=25.0 +lat_2=47.0 +lon_0=105.0 +ellps=WGS84'  # Albers Equal Area
plot_projection = ccrs.AlbersEqualArea(central_longitude=105.0, standard_parallels=(25.0, 47.0))
wgs84_bounds = (75, 16.73, 145, 49.6)
dst_width = 3840
dst_height = 2160


def define_projection(image_size, satellite):
    # Specify the source projection and bounds
    sizex = 10868000 / image_size / scale_factor[satellite]  # Calculate the size of the image in meters, scale_factor is a correction factor
    sizey = sizex
    src_trans = from_origin(-image_size / 2 * sizex, image_size / 2 * sizey,
                            sizex, sizey)  # The source transform from upper-left corner
    src_crs_string = f'+proj=geos +h=35785831.0 +lon_0={long_0[satellite]} +ellps=WGS84'  # Geostationary Projection at 128.2E
    src_crs = CRS.from_string(src_crs_string)

    # Specify the destination projection and bounds
    wgs84_crs = CRS.from_string('EPSG:4326')
    dst_crs = CRS.from_string(dst_crs_string)
    dst_bounds = transform_bounds(wgs84_crs, dst_crs, *wgs84_bounds)
    # Set the destination width and height
    dst_trans = from_bounds(*dst_bounds, dst_width, dst_height)

    # Calculate for load region
    # src_bounds = transform_bounds(wgs84_crs, src_crs, *wgs84_bounds)
    src_bounds = transform_bounds(dst_crs, src_crs, *dst_bounds)
    src_px = np.round(np.array(src_bounds) / sizex * [1, -1, 1, -1] + image_size / 2).astype(int)
    src_px[1], src_px[3] = src_px[3], src_px[1]  # Swap the y-coordinates to match the image orientation
    return src_trans, src_crs, dst_trans, dst_crs, src_px.tolist()


def reprojection(src_image, src_trans, src_crs, dst_trans, dst_crs):
    array = np.array(src_image)
    _, _, bands = array.shape
    # Reproject the image
    dst_data = np.zeros((dst_height, dst_width, bands), dtype=array.dtype)
    for i in range(bands):
        reproject(
            source=array[:, :, i],
            destination=dst_data[:, :, i],
            src_transform=src_trans,
            src_crs=src_crs,
            src_nodata=0,
            dst_transform=dst_trans,
            dst_crs=dst_crs,
            resampling=Resampling.cubic,
            num_threads=8,
        )

    # Plot the image using Cartopy
    fig = plt.figure(figsize=(dst_width / 300, dst_height / 300))
    ax = fig.add_subplot(1, 1, 1, projection=plot_projection)

    # Add Border and Coastline
    res = '50m'
    ax.add_feature(cfeature.STATES.with_scale(res), linestyle=':', edgecolor='#ed8', linewidth=0.25)
    ax.add_feature(cfeature.BORDERS.with_scale(res), linestyle='--', edgecolor='#ed8', linewidth=0.35)
    ax.add_feature(cfeature.COASTLINE.with_scale(res), edgecolor='#8ee', linewidth=0.35)

    dst_data = np.transpose(dst_data, (2, 0, 1))
    show(dst_data, ax=ax, transform=dst_trans)

    ax.axis('off')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    ax.set_extent([wgs84_bounds[0], wgs84_bounds[2], wgs84_bounds[1], wgs84_bounds[3]], crs=ccrs.PlateCarree())

    # return plt.show() as PIL.Image
    buf = io.BytesIO()
    plt.savefig(buf, dpi=300, transparent=True)
    buf.seek(0)
    img = Image.open(buf)

    return img


def load_china(satellite):
    target_full_disk_size = 5500

    if satellite == "himawari":
        region = [[1, 2], [1, 1], [0, 3], [2, 1], [2, 2], [0, 2], [1, 0], [0, 1], [1, 3], [2, 0],
                  [2, 3], [1, 4], [0, 4], [2, 4], [3, 3], [1, 5], [3, 0],
                  [0, 5], [3, 4],
                  ]
    elif satellite == "gk2a":
        region = [[1, 3], [1, 2], [1, 1], [0, 3], [2, 2], [0, 4], [2, 3], [0, 2], [0, 1], [1, 4], [2, 1], [2, 4], [1, 5],
                  [2, 0], [2, 5], [0, 5], [1, 0], [3, 4],
                  [3, 5], [3, 0],
                  ]
    else:
        _, _, _, _, region = define_projection(target_full_disk_size, satellite)

    print("Loading China region in pixels:", region)
    args = {"size": target_full_disk_size, "color": 'geocolor'}
    img = load_geostationary(satellite, region=region,
                             overlay_border=False,
                             **args)
    src_trans, src_crs, dst_trans, dst_crs, _ = define_projection(img.size[0], satellite)
    img = reprojection(img, src_trans, src_crs, dst_trans, dst_crs)
    return img


if __name__ == '__main__':
    # Example usage
    sat = 'gk2a'
    image = load_china(sat)
    image.save(f'china_{sat}.png')
