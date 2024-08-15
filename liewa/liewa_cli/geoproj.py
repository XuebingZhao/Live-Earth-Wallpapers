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
wgs84_bounds = (76, 16, 150, 49.8)
dst_width = 3840
dst_height = 2160


def reprojection(image, satellite):
    array = np.array(image)

    height, width, bands = array.shape = array.shape

    # Specify the source projection and bounds
    sizex = 10868000 / width / scale_factor[
        satellite]  # Calculate the size of the image in meters, 1.002 is a correction factor
    sizey = sizex
    src_trans = from_origin(-width / 2 * sizex, height / 2 * sizex, sizex,
                            sizey)  # The source transform from upper-left corner
    src_crs_string = f'+proj=geos +h=35785831.0 +lon_0={long_0[satellite]} +ellps=WGS84'  # Geostationary Projection at 128.2E
    src_crs = CRS.from_string(src_crs_string)

    # Specify the destination projection and bounds
    wgs84_crs = CRS.from_string('EPSG:4326')
    dst_crs = CRS.from_string(dst_crs_string)
    dst_bounds = transform_bounds(wgs84_crs, dst_crs, *wgs84_bounds)
    # Set the destination width and height
    dst_trans = from_bounds(*dst_bounds, dst_width, dst_height)

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
            num_threads=4,
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


def load_china():
    img = load_geostationary({"size": 5504, "color": 'geocolor'},
                             'gk2a', region=[0, 0, 4200, 2700],
                             overlay_border=False)
    img = reprojection(img, 'gk2a')
    return img


if __name__ == '__main__':
    # Example usage
    # satellite = 'meteosat-9'
    # img = Image.open(f'{satellite}.png')
    # img = reprojection(img, satellite)
    # img.save(f'china_{satellite}.png')

    img = load_china()
    img.save('china_gk2a.png')
