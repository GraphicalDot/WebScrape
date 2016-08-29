#!/usr/bin/env python
#-*- coding: utf-8 -*-

# project imports
# from Testing_colored_print import bcolors
from error_decorators import process_result, print_messege

# external libraries imports
import BeautifulSoup

# python standard library imports
import time
import traceback
import hashlib
import os
import sys
import re

# temprory used libraries for testing
# from selenium import webdriver
# from selenium.common.exceptions import NoSuchElementException
# import pprint

# defining Global vars
FILE = os.path.basename(__file__)
driver_exec_path = "driver/chromedriver"


class ZomatoReviews(object):
    def __init__(self, soup, area_or_city, eatery_id, eatery_url):
        '''
        Args:
            soup: BeatifulSoup object created from the page source of the url
                  It is supposed to be a fully loaded with all the reviews or
                  number of reviews that need to be stored.

            area_or_city: location of the resturant (eatery).

            eatery_id: resturant id (eatery id) of the resturant whose reviews
                       are to be parsed.

            eatery_url: URL of the page of resturant on Zomato.
        '''
        self.soup = soup
        self.area_or_city = area_or_city
        self.eatery_id = eatery_id
        self.eatery_url = eatery_url
        try:
            # getting the list of all reviews block elements
            self.reviews_list = self.soup.findAll("div", {"itemprop": "review"})
        except:
            raise StandardError("Failed to find div tag with attr 'itemprop'='review'")

        # print' Total Reviews :', len(self.reviews_list)

        # list that will contain the dicts of the data for each review
        self.reviews_data = []

        # collecting reviews now
        self.__get_all_reviews()

    def __get_all_reviews(self):
        '''
        Extracts the reviews data from the list of reviews blocks, save each data
        into the dict and updates the list by appending entry for each review.
        '''
        for item in self.reviews_list:
            # extracting the blocks to get reviews text and reviews fields, user
            # info and user fields. This is being done to isolate the blocks so
            # that particular data can be extracted from within that block

            # content block; gives review_id, eatery_id, review_likes,
            # management_response and helps in extracting user_info, user_str,
            # review_link and review_desc
            try:
                self.content_block = item.find("div",
                                            {"data-snippet": "restaurant-review"}
                                            )
            except:
                # print 'No Content Block'
                self.content_block = None

            try:
                user_block = self.content_block.find("div",{"class": "ui item clearfix "})
            except:
                # print "No user block"
                user_block = None

            try:
                # user_info; gives user_url and user_name
                self.user_info = user_block.find("div",
                                                {"class": "header nowrap ui left"}
                                                ).find("a")
            except:
                # print "No user info"
                self.user_info = None

            try:
                # user_str; gives user_reviews and user_followers
                self.user_str = user_block.find("span",
                                                {"class": "grey-text fontsize5 nowrap"}
                                                ).text
            except:
                # print 'No User Str'
                self.user_str = None

            try:
                # review_link; gives review_url and review_time
                self.review_link = self.content_block.find("div",
                                                    {"class": "fs12px pbot0 clearfix"}
                                                    ).find("a")
            except:
                # print "No review Link"
                self.review_link = None

            try:
                self.review_desc = self.content_block.find("div",
                                                           {"itemprop": "description"}
                                                           )
            except:
                # print "No review desc"
                self.review_desc = None

            __reviews = dict()

            __reviews['review_id'] = self.__get_review_id(item)
            __reviews['eatery_id'] = self.__get_eatery_id(item)
            __reviews['review_likes'] = self.__get_review_likes(item)
            __reviews['user_url'] = self.__get_user_url(item)
            __reviews['user_id'] = self.__get_user_id(__reviews['user_url'])
            __reviews['user_name'] = self.__get_user_name(item)
            __reviews['user_reviews'] = self.__get_user_reviews(item)
            __reviews['user_followers'] = self.__get_user_followers(item)
            __reviews['review_url'] = self.__get_review_url(item)
            __reviews['review_time'] = self.__get_review_time(item)
            __reviews['review_text'] = self.__get_review_text(item)
            __reviews['management_response'] = self.__get_management_response(item)

            __reviews['readable_review_year'] = self.__get_readable_review_year(
                                                __reviews['review_time'])
            __reviews['readable_review_month'] = self.__get_readable_review_month(
                                                __reviews['review_time'])
            __reviews['readable_review_day'] = self.__get_readable_review_day(
                                                __reviews['review_time'])
            __reviews['converted_epoch'] = self.__get_converted_epoch(
                                            __reviews['review_time'])

            __reviews['area_or_city'] = self.area_or_city
            __reviews['scraped_epoch'] = int(time.time())
            __reviews['__review_id'] = hashlib.sha256(
                                        str(__reviews["review_id"])+\
                                        str(__reviews["review_text"])
                                        ).hexdigest()

            self.reviews_data.append(__reviews)

    def exception_handling(func):
        '''
        Decorator that defines a wrapper for handling exceptions.
        '''
        def deco(self, review):
            '''
            Wrapper function, that will be used by exception_handling decorator
            around all the functions in this class; this executes the function
            to which decorator is used, and checks for exception while execution.
            '''
            try:
                return func(self, review)
            except ValueError as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error = repr(traceback.format_exception(exc_type, exc_value,
                                                        exc_traceback))
                print_messege("error", "value error occurred", func.__name__,
                              error, self.eatery_id, self.eatery_url,
                              None, module_name=FILE)
                return None
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error = repr(traceback.format_exception(exc_type, exc_value,
                                                        exc_traceback))
                print_messege("error", "error occurred", func.__name__,
                              error, self.eatery_id, self.eatery_url,
                              None, module_name=FILE)
                return None
        return deco

    @exception_handling
    def __get_review_id(self, review):
        return self.content_block["data-review_id"]

    @exception_handling
    def __get_eatery_id(self, review):
        return self.content_block["data-res_id"]

    @exception_handling
    def __get_review_likes(self, review):
        return self.content_block.find("div",
                                       {"data-action": "like"}
                                       )["data-likes"]

    @exception_handling
    def __get_user_id(self, url):
        if url:
            return url[url.rfind("/")+1:]
        else:
            return None

    @exception_handling
    def __get_user_url(self, review):
        if self.user_info:
            return self.user_info['href']

    @exception_handling
    def __get_user_name(self, review):
        if self.user_info:
            return self.user_info.text

    @exception_handling
    def __get_user_reviews(self, review):
        if self.user_str:
            return self.user_str.split()[0]

    @exception_handling
    def __get_user_followers(self, review):
        if self.user_str:
            return self.user_str.split()[3]

    @exception_handling
    def __get_review_url(self, review):
        if self.review_link:
            return self.review_link['href']

    @exception_handling
    def __get_review_time(self, review):
        if self.review_link:
            return self.review_link.find("time")['datetime']

    @exception_handling
    def __get_review_text(self, review):
        if self.review_desc:
            # convert the html block into unicode then convert it to string
            # safley, so to avoid unicode char errors
            rev_text = (unicode(self.review_desc)).encode('ascii', 'ignore')
            # getting the text part out of the html
            a = rev_text.find('</div>')+len('</div>')
            b = rev_text.find('<div class="clear"')
            # removing html tags appearing between the text
            text = re.sub('<[^<]+?>', '', rev_text[a:b])

            # return the text by replacing extra spaces with ''
            return text.replace('  ','')

    @exception_handling
    def __get_management_response(self, review):
        # get the block if present; i.e. if this section is avaliable in the
        # review, and return the text part after extracting it
        block = self.content_block.find("div", {"class": "review-replies-container mtop"})
        return block.find("div", {"class": "text"}).text

    def __get_converted_epoch(self, obj):
        '''
        Converts the datetime string of the reviews to epoch time format. This
        is done in order to make search queries easy and faster.
        Arg:
            obj: datetime string extracted of the review, i.e. datetime when
                 the review was writteb by the user
        Example:
            obj = 2014-04-10 16:57:07;
            returns 1401525098
        '''
        try:
            return time.mktime(time.strptime(obj, "%Y-%m-%d %H:%M:%S"))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = repr(traceback.format_exception(exc_type, exc_value,
                                                    exc_traceback))
            print_messege("error", "error occurred", '__get__converted_epoch',
                          error, self.eatery_id, self.eatery_url,
                          None, module_name=FILE)

    def __get_readable_review_year(self, obj):
        '''
        Returns the year in which the review was written.
        Arg:
            obj: Datetime string of the review.
        '''
        try:
            epoch = self.__get_converted_epoch(obj)
            return time.strftime("%Y", time.localtime(int(epoch)))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = repr(traceback.format_exception(exc_type, exc_value,
                                                    exc_traceback))
            print_messege("error", "error occurred",'__get_readable_review_year',
                          error, self.eatery_id, self.eatery_url,
                          None, module_name=FILE)

    def __get_readable_review_month(self, obj):
        '''
        Returns the year in which the review was written.
        Arg:
            obj: Datetime string of the review.
        '''
        try:
            epoch = self.__get_converted_epoch(obj)
            return time.strftime("%m", time.localtime(int(epoch)))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = repr(traceback.format_exception(exc_type, exc_value,
                                                    exc_traceback))
            print_messege("error", "error occurred",'__get_readable_review_month',
                          error, self.eatery_id, self.eatery_url,
                          None, module_name=FILE)

    def __get_readable_review_day(self, obj):
        '''
        Returns the year in which the review was written.
        Arg:
            obj: Datetime string of the review.
        '''
        try:
            epoch = self.__get_converted_epoch(obj)
            return time.strftime("%d", time.localtime(int(epoch)))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = repr(traceback.format_exception(exc_type, exc_value,
                                                    exc_traceback))
            print_messege("error", "error occurred",'__get_readable_review_day',
                          error, self.eatery_id, self.eatery_url,
                          None, module_name=FILE)


'''
# the code below is for testing purpose

def make_soup(url):
    driver = webdriver.Chrome(driver_exec_path)
    driver.get(url)
    driver.implicitly_wait(20)

    # get the element to click for getting all the reviews
    e = driver.find_element_by_xpath("//a[@data-sort='reviews-dd']")

    # performing successfull click on 'All reviews' element
    for i in range(10):
        e.click()
        driver.implicitly_wait(3)

    # getting the limit i.e setting how many times load more button has to be
    # clicked
    limit = 1
    # setting the count to number of times load more is clicked
    limit_count = 0

    while True:
        try:
            button = driver.find_element_by_class_name("zs-load-more-count")
            button.click()

            if limit:
                # if limit is set then increment the limit count and break
                # if count equals the limit
                limit_count += 1
                if limit_count == limit:
                    print 'got the reviews'
                    break

            driver.implicitly_wait(3)
        except NoSuchElementException:
            print 'No more load More button'
            break
        except:
            pass

    html = driver.page_source
    content = html.encode('ascii', 'ignore').decode('ascii')
    driver.close()

    return BeautifulSoup.BeautifulSoup(content)


if __name__ == "__main__":
    # url = "https://www.zomato.com/mumbai/between-breads-pali-hill-bandra-west"
    url = "https://www.zomato.com/mumbai/haazri-malad-east"
    soup = make_soup(url)
    obj = ZomatoReviews(soup, 'mumbai', 1, url)
    print len(obj.reviews_data)
    pprint.pprint(obj.reviews_data[3])
'''
