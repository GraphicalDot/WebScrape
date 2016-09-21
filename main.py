#!/usr/bin/env python

from zomato_tasks import start_scraping


if __name__ == "__main__":
    urls = ["https://www.zomato.com/ncr/restaurants"]
    # urls = ["https://www.zomato.com/HauzKhasSocial"]
    # urls = ["https://www.zomato.com/ncr/indian-grill-room-golf-course-road-gurgaon"]
    for url in urls:
        start_scraping.apply_async([url, 60, 0, False])
        # start_scraping.apply_async([url, 30, 0, True])
