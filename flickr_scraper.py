from dotenv import load_dotenv
import os
import argparse

from scraper import Scraper


def main():
    load_dotenv()
    api_key = os.getenv("FLICKR_API_KEY")
    api_secret = os.getenv("FLICKR_API_SECRET")

    parser = argparse.ArgumentParser(description="Flickr image scraper")
    parser.add_argument("year", type=parse_year_or_range, help="Year or range of years from which to scrape images")
    parser.add_argument("-n", type=int, default=1000, help="Total number of images to scrape")

    args = parser.parse_args()

    scraper = Scraper(api_key, api_secret)
    if isinstance(args.year, int):
        scraper.scrape_images_for_year(args.year, total=args.n)
    else:
        for y in args.year:
            print(f"Fetching images for year {y}")
            scraper.scrape_images_for_year(y, total=args.n)


def parse_year_or_range(value: str) -> int | list[int]:
    if "-" in value:
        start, end = map(int, value.split("-"))
        if start > end:
            raise argparse.ArgumentTypeError(f"Invalid range: {value}")
        return [i for i in range(start, end + 1)]
    else:
        try:
            return int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid year: {value}. Provide a single year or a range like 2000-2021")


if __name__ == "__main__":
    main()


