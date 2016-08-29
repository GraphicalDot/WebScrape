#!/usr/bin/env python

from zomato_tasks import start_scraping


if __name__ == "__main__":
    urls = ["https://www.zomato.com/ncr/south-delhi-restaurants"]
    for url in urls:
        start_scraping.apply_async([url, 30, 0, None])
