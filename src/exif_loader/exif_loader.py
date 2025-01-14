import glob
import os
from typing import Any

import polars as pl
from PIL import Image, ExifTags

from constants import COLUMN_APERTURE, COLUMN_ISO, COLUMN_LENS, COLUMN_FOCAL_LENGTH, COLUMN_CAMERA, COLUMN_EXPOSURE, \
    COLUMN_DATETIME, COLUMN_FILENAME, COLUMN_LABEL, COLUMN_EXPOSURE_PRETTY, COLUMN_APERTURE_PRETTY, \
    COLUMN_FOCAL_LENGTH_PRETTY, COLUMN_DIRECTORY


def extract_exif_data(filename: str):
    """Extracts relevant EXIF data from an image file using PIL."""
    try:
        image = Image.open(filename)
        # Although it is nice to have an API, we know the exact fields we want
        # and not mess with the whole reorganization of metadata struct
        exif_data = image._getexif()

        # Extract relevant tags
        # https://exiv2.org/tags.html
        lens = exif_data.get(42036, None)  # Lens
        camera = exif_data.get(272, None)  # Camera
        exposure = exif_data.get(33434, None)  # ExposureTime
        aperture = exif_data.get(33437, None)  # FNumber
        focal_length = exif_data.get(37386, None)  # FocalLength
        iso = exif_data.get(34855, None)  # ISOSpeedRatings
        datetime = exif_data.get(306, None)  # DateTime

        return lens, camera, exposure, aperture, focal_length, iso, datetime
    except (FileNotFoundError, AttributeError, KeyError) as e:
        print(e)
        return None, None, None, None, None, None, None

def __prettify_exposure(exposure: Any) -> str:
    if exposure is not None:
        if exposure > 1:
            return f'{exposure}"'
        else:
            return f"1 / {f'{1 / exposure:.5f}'.rstrip('0').rstrip('.')}"
    return 'Unavailable'

def __prettify_string(s: Any) -> str:
    if s and len(s.replace('\x00', '').rstrip()) > 1 and s not in ['None']:
        return s.replace('\x00', '').rstrip()
    return 'Unavailable'

def __prettify_aperture(aperture: Any) -> Any:
    if aperture == 0 or aperture is None:
        return 'Unavailable'
    return f'f/{aperture}'

def __prettify_focal_length(focal_length: Any) -> str:
    if focal_length == 0 or focal_length is None:
        return 'Unavailable'
    return f'{float(focal_length):.0f}mm'

def __prettify_directory(filename: str, global_directory: str):
    if global_directory[-1:] != os.sep:
        global_directory = global_directory + os.sep

    directory = filename.replace(global_directory, '').split(os.sep)
    return os.sep.join(directory[:-1])


def load_dataframe_pictures(base_directory: str, glob_path: str, label: str) -> (pl.DataFrame, str | None):
    """
    Load dataframe of pictures
    :param base_directory: Base directory
    :param glob_path: Glob Path
    :param label: Label of pictures
    :return: Dataframe, error (if any)
    """
    if not base_directory:
        return pl.DataFrame(), 'Missing base directory'
    if not glob_path:
        return pl.DataFrame(), 'Missing glob path'
    image_files = [f for f in glob.glob(os.path.join(base_directory, glob_path))]

    data = []
    for filename in image_files:
        lens, camera, exposure, aperture, focal_length, iso, datetime = extract_exif_data(filename)
        data.append({
            COLUMN_LENS: __prettify_string(lens),
            COLUMN_CAMERA: __prettify_string(camera),
            COLUMN_EXPOSURE: exposure,
            COLUMN_EXPOSURE_PRETTY: __prettify_exposure(exposure),
            COLUMN_APERTURE: aperture,
            COLUMN_APERTURE_PRETTY: __prettify_aperture(aperture),
            COLUMN_FOCAL_LENGTH: focal_length,
            COLUMN_FOCAL_LENGTH_PRETTY: __prettify_focal_length(focal_length),
            COLUMN_ISO: iso,
            COLUMN_DATETIME: datetime,
            COLUMN_FILENAME: filename,
            COLUMN_DIRECTORY: __prettify_directory(filename, base_directory),
        })
    if len(data) == 0:
        return pl.DataFrame(), 'No pictures found'

    return pl.from_records(data).with_columns(
        pl.col(COLUMN_DATETIME).str.to_datetime('%Y:%m:%d %H:%M:%S', strict=False, ambiguous='null').dt.truncate('1d'),
        pl.lit(label).alias(COLUMN_LABEL),
    ), None