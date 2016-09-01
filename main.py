#!/usr/bin/env python

from zomato_tasks import start_scraping


if __name__ == "__main__":
    urls = ["https://www.zomato.com/ncr/restaurants"]
    for url in urls:
        start_scraping.apply_async([url, 30, 0, None])
