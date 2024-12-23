import datetime
import json
import polars as pl
import pathlib
import requests
from tqdm import tqdm
import warnings
import time


class Photo:
    id: int
    latitude: float
    longitude: float
    url: str
    year: int

    __ALT_SIZES = ("o", "n", "w", "z", "c", "b", "h", "k", "t", "q", "s", "3k", "4k", "f", "5k", "6k")
    __WAIT_TIME = 1


    def __init__(self, photo_dict: dict):
        self.id = int(photo_dict["id"])
        self.latitude = float(photo_dict["latitude"])
        self.longitude = float(photo_dict["longitude"])
        try:
            self.url = photo_dict["url_m"]
        except KeyError:
            alt_urls = ("url_" + s for s in Photo.__ALT_SIZES)
            for a in alt_urls:
                if a in photo_dict:
                    self.url = photo_dict[a]
                    break
        if not self.url:
            raise KeyError(f"No url found in response: {str(photo_dict)}")
        self.year = datetime.datetime.fromisoformat(photo_dict["datetaken"]).year


    def __str__(self):
        return json.dumps(self.as_dict())
    

    def __repr__(self):
        return json.dumps(self.as_dict())


    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "url": self.url,
            "year": self.year
        }


    def download(self, image_dir: pathlib.Path):
        """
        Downloads photo.
        Raises HTTPError if status code isn't 200.

        Args:
            image_dir (pathlib.Path): path to the directory to save image to.
        """
        filename = str(self.id) + ".jpg"
        full_path = image_dir / filename
        if full_path.is_file():
            return

        r = requests.get(self.url)
        r.raise_for_status()
        
        with open(full_path, "wb") as f:
            f.write(r.content)


    @staticmethod
    def download_photos(photos: list["Photo"], image_dir: pathlib.Path, metadata_path: pathlib.Path):
        image_dir.mkdir(parents=True, exist_ok=True)
        
        rows = []
        skipped_images = 0
        with tqdm(total=len(photos), desc="Downloading Images", unit="image") as progress_bar:
            for p in photos:
                try:
                    p.download(image_dir)
                    rows.append(p.as_dict())
                    time.sleep(Photo.__WAIT_TIME)
                    progress_bar.update(1)
                except requests.HTTPError as e:
                    if e.response.status_code == 403 or e.response.status_code == 429:
                        skipped_images += 1
                        continue
                    else:
                        raise e
        if skipped_images > 0:
            warnings.warn(f"Total images skipped: {skipped_images}")
        df = pl.DataFrame(rows)
        df.write_csv(metadata_path)

