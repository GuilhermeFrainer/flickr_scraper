import pathlib
import requests
from photo import Photo
from tqdm import tqdm


class Scraper:
    key: str
    secret: str
    image_dir: pathlib.Path

    __ALT_SIZES = ("o", "n", "w", "z", "c", "b", "h", "k", "t", "q", "s", "3k", "4k", "f", "5k", "6k")


    def __init__(self, key: str, secret: str, image_dir="images"):
        self.key = key
        self.secret = secret
        self.image_dir = pathlib.Path(image_dir)


    def scrape_images_for_year(self, year: int, total=1000, per_page=250):
        images = []
        i = 1

        with tqdm(total=total, desc="Fetching Images", unit="image") as progress_bar:
            while len(images) < total:
                images += self.fetch_images_for_year(year, page=i, per_page=per_page)
                i += 1
                progress_bar.n = min(len(images), total)
                progress_bar.refresh()
            progress_bar.close()
        
        year_dir = self.image_dir / str(year)
        images = images[:total] # Take excess off
        Photo.download_photos(images, image_dir=year_dir, metadata_path=year_dir / "metadata.csv")


    def fetch_images_for_year(self, year: int, page=1, per_page=250) -> list[Photo]:
        query = self.__query_builder(year, page=page, per_page=per_page)
        r = requests.get(query)
        if r.status_code != 200:
            raise ValueError(f"Something went wrong while fetching images for {year}. Status code: {r.status_code}")

        photos = r.json()["photos"]["photo"]
        return [Photo(p) for p in photos]


    def __query_builder(self, year: int, page: int, per_page: int):
        min_date = f"{year}-01-01"
        max_date = f"{year}-12-31"
        query = f"https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key={self.key}"
        query += f"&min_taken_date={min_date}&max_taken_date={max_date}"
        query += f"&has_geo="
        query += "&extras=date_taken%2Cgeo%2Curl_m"
        alt_sizes = ("%2Curl_" + a for a in Scraper.__ALT_SIZES)
        for a in alt_sizes:
            query += a
        query += f"&per_page={per_page}"
        query += f"&page={page}&format=json&nojsoncallback=1"
        return query
    
