import pathlib
import requests
from photo import Photo
from tqdm import tqdm


class Scraper:
    key: str
    secret: str
    image_dir: pathlib.Path


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
        print(f"Fetched images: {len(images)}")
        Photo.download_photos(images, image_dir=year_dir, metadata_path=year_dir / "metadata.csv")


    def fetch_images_for_year(self, year: int, page=1, per_page=250) -> list[Photo]:
        query = self.__query_builder(year, page=page, per_page=per_page)
        r = requests.get(query)
        r.raise_for_status()

        photos = r.json()["photos"]["photo"]
        return [Photo(p) for p in photos]


    def __query_builder(self, year: int, page: int, per_page: int):
        min_date = f"{year}-01-01"
        max_date = f"{year}-12-31"
        query = f"https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key={self.key}"
        query += f"&min_taken_date={min_date}&max_taken_date={max_date}"
        query += f"&has_geo=1"
        query += "&extras=date_taken%2Cgeo%2Curl_m%2Curl_o%2Curl_n%2Curl_w%2Curl_z%2Curl_c%2Curl_b"
        query += "%2Curl_h%2Curl_k%2Curl_t%2Curl_q%2Curl_s%2Curl_3k%2Curl_4k"
        query += "%2Curl_f%2Curl_5k%2Curl_6k"
        query += f"&per_page={per_page}"
        query += f"&page={page}&format=json&nojsoncallback=1"
        return query
    
