#!/usr/bin/env ipython

import random
import subprocess
from ZomatoScrapeTasks import GenerateEateriesList, StartScrapeChain, ScrapeEachEatery
#GenerateEateriesList.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 0, False])
#StartScrapeChain.apply_async(["https://www.zomato.com/mumbai/restaurants", 30, 0, False])

for e in range(0, 100):
		StartScrapeChain.apply_async(["https://www.zomato.com/bangalore/restaurants", 30, e, False])
	


"""

StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 2, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 3, False])

StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 4, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 5, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 6, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 7, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 8, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 9, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 10, False])

StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 11, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 12, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 13, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 14, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 15, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 16, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 17, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 18, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 19, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 20, False])

StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 21, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 22, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 23, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 24, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 25, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 26, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 27, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 28, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 29, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 30, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 31, False])

StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 32, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 33, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 34, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 35, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 36, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 37, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 38, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 39, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 40, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 41, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 42, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 43, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 44, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 45, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 46, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 47, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 48, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 49, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 50, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 51, False])

StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 52, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 53, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 54, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 55, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 56, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 57, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 58, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 59, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 60, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 61, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 62, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 63, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 64, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 65, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 66, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 67, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 68, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 69, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 70, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 71, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 72, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 73, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 74, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 75, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 76, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 77, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 78, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 79, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 80, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 81, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 82, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 83, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 84, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 85, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 86, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 87, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 88, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 89, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 90, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 91, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 92, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 93, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 94, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 95, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 96, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 97, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 98, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 99, False])


StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 502, False])
StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 31, False])
#ScrapeEachEatery.apply_async([{"eatery_url": "https://www.zomato.com/ncr/dilli-19-kalkaji-new-delhi"}])



for e in range(99, 150):
	StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, e, False])

"""


