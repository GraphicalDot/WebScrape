#!/usr/bin/env python

# project modules
from Testing_database import eatery_collection, review_collection
# from Testing_database import user_collection
from review_scrape import ZomatoReviews
from Testing_colored_print import bcolors
# from db_insertion import DBInsert
from error_decorators import print_messege, process_result

# external libraries
import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC1
from selenium.common.exceptions import WebDriverException
# from colored import fg, bg, attr
from retrying import retry
import pymongo
from blessings import Terminal
# import match

# standard library modules
# import sys
import os
import time
import random
# import re
# import timeit
import pprint
import ConfigParser
# import datetime
import urllib2
# import getpass
import hashlib

# setting up the global vars
terminal = Terminal()
FILE = os.path.basename(__file__)

config = ConfigParser.RawConfigParser()
config.read("global.cfg")
config.read("zomato_dom.cfg")

driver_exec_path = "driver/chromedriver"
DRIVER_NAME = "CHROME"

connection = pymongo.MongoClient(config.get("zomato", "host"), config.getint("zomato", "port"))
ZomatoReviewsCollection = connection[config.get("zomato", "database")][config.get("zomato", "reviews")]
PROXY_ADDRESS = config.get("proxy", "proxy_Addr")


class EateriesList(object):
    def __init__(self, url, number_of_restaurants=None, skip=0, is_eatery=False):
        '''
        Args:
            url: link on zomato for a city.
            number_of_restaurants: number of restaurants to be scrape
                                   (defualt: None, implies to scrape all the
                                   restuarants, applying multiple of 30 to
                                   scrape no. of pages.)
            skip: type int; number of pages to be skipped
            is_eatery: if True, it implies that the url is not the url having
                       lots of resturant listed.

        Notes:
            - if only first page needs to be scraped; number_of_restaurants=30.
            - if all the pages (restuarants) needs to be scraped, pass None in
              number of restaurants
            - Each page has 30 restaurants so number_of_restaurants must be
              multiple of 30

        '''
        self.eateries_list = []
        self.url = url

        if is_eatery:
            # if is_eatery is True that means url is a retrurant url, so we
            # update eateries_list with it and gets returned from this point
            self.eateries_list.append({"eatery_url": self.url})
            return

        self.number_of_restaurants = number_of_restaurants
        self.skip = skip

        # restaurants must be multiple of 30
        assert(number_of_restaurants%30==0)
        number_of_pages = number_of_restaurants/30 if number_of_restaurants else None

        # get the soup object for the page source of url
        self.soup_only_for_pagination = self.__prepare_soup(self.url)

        # get the pagination div (with text like Page 1 of 233)
        pagination_div = self.soup_only_for_pagination.find("div", {"class": "col-l-4 mtop pagination-number"})

        # get the total number of pages for restaurants on this url
        try:
            pages_number = str(pagination_div.text).split("of")[-1]
        except:
            pages_number = 1

        # forming the list of urls for all the result pages
        try:
            pages_url = ["%s?page=%s"%(self.url, page_number) for page_number in range(1, int(pages_number)+1)]
        except Exception as e:
            print " >> Err: EateriesList.__init__;", str(e)
            print "{start_color} Seems some problem with pagination  {end_color}".format(start_color=bcolors.FAIL, end_color=bcolors.RESET)

        # scrapping one result page at a time and collecting eateries info
        for page_link in pages_url[skip: skip+number_of_pages]:
            print "{start_color} -<Loading  {val}>- {end_color}".format(start_color=bcolors.OKBLUE, val=page_link, end_color=bcolors.RESET)
            temp_list = self.__prepare_and_return_eateries_list(page_link)
            self.eateries_list.extend(temp_list)

    def __prepare_soup(self, url):
        '''
        This method opens the url in the webdriver, downloads the source of the
        page, convert the html page source into the BeautifulSoup object and
        returns it.
        '''

        # load the webdriver
        if config.getboolean("proxy", "use_proxy"):
            if DRIVER_NAME == "PhantomJS":
                service_args =[config.get("proxy", "service_args")]
                driver = webdriver.PhantomJS(service_args=service_args)
            else:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--proxy-server=%s'%PROXY_ADDRESS)
                driver = webdriver.Chrome(driver_exec_path, chrome_options=chrome_options)
        else:
            if DRIVER_NAME == "PhantomJS":
                driver = webdriver.PhantomJS()
            else:
                driver = webdriver.Chrome(driver_exec_path)

        # open the url
        driver.get(url)

        # download the page source and convert the content into ascii ignoring
        # the unicode strings or characters
        html = driver.page_source
        content = html.encode('ascii', 'ignore').decode('ascii')

        # close the webdriver
        driver.quit()

        # return the BeautifulSoup object
        return BeautifulSoup.BeautifulSoup(content)

    def __prepare_and_return_eateries_list(self, page_link):
        '''
        This method downloads the content of each result page and extracts each
        eateries data from it. It returnes the list of dictionaries contaning
        eatries data.
        '''
        soup_of_each_page = self.__prepare_soup(page_link)

        # list to save dict having data for each eatry on the result page
        eateries_list = list()

        # [--UPDATE--]
        # [X] findAll("li",{"class":"js-search-result-li even  status 1"})
        for eatery_soup in soup_of_each_page.findAll("div", {"class": "js-search-result-li even  status 1"}):
            eatery = dict()
            eatery["eatery_id"] = eatery_soup.get("data-res_id")
            eatery["eatery_photo_link"] = eatery_soup.find("a").get("href")

            # local func to get eatery name and url
            def some(__soup, eatery_name=False):
                try:
                    # [--UPDATE--]
                    # [X] find("h3", {"class":" top-res-boxcim m-name left"}).find("a")
                    result = __soup.find("a", {"class":"result-title hover_feedback zred bold ln24   fontsize0 "})
                    return result['href'] if not eatery_name else result.text
                except:
                    if eatery_name:
                        print "{start_color} Eatery Name couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                    else:
                        print "{start_color} Eatery Title couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                    return None

            eatery["eatery_url"] = some(eatery_soup)
            eatery["eatery_name"] = some(eatery_soup, True)

            try:
                eatery["eatery_address"] = eatery_soup.find("div", {"class": "col-m-16 search-result-address grey-text nowrap ln22"})["title"]
            except:
                print "{start_color} Eatery address couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                eatery["eatery_address"] = None

            try:
                # [-- UPDATE --]
                # eatery["eatery_cuisine"] = eatery_soup.find("div", {"class":"res-cuisine mt2 clearfix"})["title"]
                eatery["eatery_cuisine"] = eatery_soup.find("div", {"class": "clearfix"}).findAll("span")[1].text
            except:
                print "{start_color} Eatery cuisine couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                eatery["eatery_cuisine"] = None

            try:
                # [-- UPDATE --]
                # eatery["eatery_cost"] = eatery_soup.find("div", {"class":"res-cost clearfix"}).findNext().findNext().text
                eatery["eatery_cost"] = eatery_soup.find("div", {"class":"res-cost clearfix"}).findAll("span")[1].text
            except:
                print "{start_color} Eatery cost couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                eatery["eatery_cost"] = None

            try:
                # [-- UPDATE --]
                # eatery["eatery_type"] = eatery_soup.find("div", {"class": 'res-snippet-small-establishment'}).text
                eatery["eatery_type"] = eatery_soup.find("div", {"class": 'res-snippet-small-establishment mt5'}).text
            except:
                print "{start_color} Eatery type couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                eatery["eatery_type"] = None

            try:
                # [-- UPDATE --]
                # try:
                #     delivery_time_span = delivery_time_tag.find("span")
                #     delivery_time_span.extract()
                # except:
                #    pass
                # delivery_time_tag = eatery_soup.find("div", {"class": "del-time"})
                eatery["eatery_delivery_time"] = eatery_soup.find("div", {"class": "res-timing clearfix"})["title"]
            except:
                print "{start_color} Eatery delivery time couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                eatery["eatery_delivery_time"] = None

            try:
                # [-- UPDATE --]
                # try:
                #     eatery_minimum_span = eatery_minimum_order_tag.find("span")
                #     eatery_minimum_span.extract()
                # except:
                #     pass
                eatery_minimum_order_tag = eatery_soup.find("div", {"class": "ui three item menu search-result-action mt0"})
                eatery["eatery_minimum_order"] = eatery_minimum_order_tag.findAll("a")[2].text
            except:
                print "{start_color} Eatery minimum order couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                eatery["eatery_minimum_order"] = None

            try:
                # [--UPDATE--]
                # eatery["eatery_rating"] = {"rating": eatery_soup.find("div",  {"class": "search_result_rating col-s-3  clearfix"}).findNext().text,
                #                           "votes": eatery_soup.find("div",  {"class": "rating-rank right"}).find("span").text }
                eatery["eatery_rating"] = {
                                            "rating": eatery_soup.find("div", {"class": "rating-popup rating-for-"+str(eatery['eatery_id'])+" res-rating-nf right level-9 bold"}).text.split()[0],
                                            "votes": eatery_soup.find("span", {"class": "rating-votes-div-"+eatery["eatery_id"]+" grey-text fontsize5"}).text.split(" ")[0]
                                        }
            except:
                print "{start_color} Eatery rating couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                eatery["eatery_rating"] = None

            try:
                collection_of_trending =  eatery_soup.find("div", {"class": "res-collections clearfix"}).findAll("a")
                eatery["eatery_trending"] = [element.text for element in collection_of_trending]
            except:
                print "{start_color} Eatery trending couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                eatery["eatery_trending"] = None

            try:
                eatery["eatery_total_reviews"] = eatery_soup.find("a", {"data-result-type": "ResCard_Reviews"}).text.split(" ")[0]
            except:
                print "{start_color} Eatery total reviews couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
                eatery["eatery_total_reviews"] = 0

            print "{start_color} Eatery with --<<{id}-->> is completed  {end_color}".format(start_color=bcolors.OKGREEN, id=eatery["eatery_id"], end_color=bcolors.RESET)
            eateries_list.append(eatery)

        return eateries_list


class EateryData(object):
    def __init__(self, eatery_dict):
        '''
        Arg:
            eatery_dict: This is a dictionary containing the data for one eatery
                         (probably created from EateriesList).
                         E.g. Keys for eatery_dict are eatery_id, eatery_name,
                         eatery_url, eatery_collection, eatery_type etc.

        '''
        self.eatery = eatery_dict
        self.soup = self.make_soup()
        process_result(self.eatery, "eatery_name", FILE)(self.retry_eatery_name)()
        process_result(self.eatery, "eatery_id", FILE)(self.retry_eatery_id)()
        try:
            assert(self.eatery["eatery_id"] != None)
            assert(self.eatery["eatery_name"] != None)
        except Exception as e:
            print terminal.bold_red_on_green("Now changing eatery url to info url")
            eatery_url = self.eatery["eatery_url"]
            eatery_url = "%s/info"%eatery_url
            self.eatery["eatery_url"] = eatery_url
            print terminal.bold_red_on_green("New Info url for eatery_id %s is %s"%(self.eatery["eatery_id"], self.eatery["eatery_url"]))
            self.soup = self.make_soup()

            try:
                self.retry_eatery_address()
            except Exception as e:
                print str(e)
                print terminal.bold_red_on_green("No eatery address could be found for  eatery_id %s is %s"%(self.eatery["eatery_id"], self.eatery["eatery_url"]))

    def run(self):
        print "Found eatery_id==<<{eatery_id}>> and eatery_name==<<{eatery_name}>> time".format(start_color=bcolors.OKGREEN, eatery_id=self.eatery["eatery_id"], eatery_name=self.eatery["eatery_name"].encode("ascii", "ignore"), end_color=bcolors.RESET)
        __hash = hashlib.sha256(self.eatery["eatery_id"] + self.eatery["eatery_url"]).hexdigest()

        self.eatery.update({"__eatery_id": __hash})
        self.reviews_inDB = review_collection.find({"eatery_id": self.eatery["eatery_id"]}).count()

        try:
            self.previous_total_reviews = eatery_collection.find_one({"eatery_id": self.eatery["eatery_id"]}).get("eatery_total_reviews")
        except Exception as e:
            print "Eatery easnt present earlier so setting previous total reviews to 0"
            print e
            self.previous_total_reviews = 0

        messege = "Number of reviews present in the database %s"%self.reviews_inDB
        print_messege("info", messege, "EateryData.run", None, self.eatery["eatery_id"],\
                      self.eatery["eatery_url"], None, FILE)

        process_result(self.eatery, "eatery_cost", FILE)(self.retry_eatery_cost)()
        process_result(self.eatery, "eatery_trending", FILE)(self.retry_eatery_trending)()
        process_result(self.eatery, "eatery_rating", FILE)(self.retry_eatery_rating)()
        process_result(self.eatery, "eatery_cuisine", FILE)(self.retry_eatery_cuisine)()
        process_result(self.eatery, "eatery_highlights", FILE)(self.eatery_highlights)()
        process_result(self.eatery, "eatery_popular_reviews", FILE)(self.eatery_popular_reviews)()

        process_result(self.eatery, "location", FILE)(self.eatery_longitude_latitude)()
        process_result(self.eatery, "eatery_total_reviews", FILE)(self.eatery_total_reviews)()
        process_result(self.eatery, "eatery_buffet_price", FILE)(self.eatery_buffet_price)()
        process_result(self.eatery, "eatery_buffet_details", FILE)(self.eatery_buffet_details)()

        process_result(self.eatery, "eatery_recommended_order", FILE)(self.eatery_recommended_order)()
        process_result(self.eatery, "eatery_known_for", FILE)(self.eatery_known_for)()
        process_result(self.eatery, "eatery_area_or_city", FILE)(self.eatery_area_or_city)()
        process_result(self.eatery, "eatery_opening_hours", FILE)(self.eatery_opening_hours)()
        process_result(self.eatery, "eatery_photo_link", FILE)(self.eatery_photo_link)()
        process_result(self.eatery, "eatery_update_on", FILE)(self.eatery_update_on)()

        assert(self.eatery["location"] != None)
        review_soup = self.get_reviews()

        # self.last_no_of_reviews_to_be_scrapped = int(self.no_of_reviews_to_be_scrapped) - int(no_of_blogs)
        ins = ZomatoReviews(review_soup, self.eatery["eatery_area_or_city"], self.eatery["eatery_id"], self.eatery["eatery_url"])
        return (self.eatery, ins.reviews_data)
        # return self.eatery

    def make_soup(self):
        '''
        Loads the webdriver and open the url in self.eatery['eatery_url'],
        downloads the page source and returns its BeautifulSoup object.
        '''
        if config.getboolean("proxy", "use_proxy"):
            if DRIVER_NAME == "PhantomJS":
                service_args =[config.get("proxy", "service_args")]
                driver = webdriver.PhantomJS(service_args=service_args)
                driver.get(self.eatery["eatery_url"])
            else:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--proxy-server=%s' %PROXY_ADDRESS)
                driver = webdriver.Chrome(driver_exec_path, chrome_options=chrome_options)
                driver.get(self.eatery["eatery_url"])
        else:
            if DRIVER_NAME == "PhantomJS":
                driver = webdriver.PhantomJS()
                driver.get(self.eatery["eatery_url"])
            else:
                driver = webdriver.Chrome(driver_exec_path)
                driver.get(self.eatery["eatery_url"])

        if driver.title.startswith("404"):
            driver.close()
            raise StandardError("This url doesnt exists, returns 404 error")

        try:
            # clicking the button 'see more' to get opening hours of the eatery
            # for each day, so that this content appear in the page source
            driver.find_elements_by_xpath('//*[@id="res-timings-toggle"]')[0].click()
        except Exception as e:
            print e
            pass

        time.sleep(3)

        html = driver.page_source
        driver.quit()

        # converting the html source into BeautifulSoup object and returning it
        return BeautifulSoup.BeautifulSoup(html)

    def get_reviews(self):
        # fire up the webdriver
        if config.getboolean("proxy", "use_proxy"):
            if DRIVER_NAME == "PhantomJS":
                service_args =[config.get("proxy", "service_args")]
                driver = webdriver.PhantomJS(service_args=service_args)
                driver.get(self.eatery["eatery_url"])
            else:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--proxy-server=%s' % PROXY_ADDRESS)
                driver = webdriver.Chrome(driver_exec_path, chrome_options=chrome_options)
                driver.get(self.eatery["eatery_url"])
        else:
            if DRIVER_NAME == "PhantomJS":
                driver = webdriver.PhantomJS()
                driver.get(self.eatery["eatery_url"])
            else:
                driver = webdriver.Chrome(driver_exec_path)
                driver.get(self.eatery["eatery_url"])

        if driver.title.startswith("404"):
            raise StandardError("This url doesnt exists, returns 404 error")

        time.sleep(20)

        # clcking on 'All reviews' tab to get all the reviews avaliable, instead
        # of only 'Poupular reviews'
        try:
            for i in range(10):
                driver.find_element_by_xpath("//a[@data-sort='reviews-dd']").click()
                driver.implicitly_wait(3)
            #driver.find_element_by_css_selector("a.everyone.empty").click()
            #print "{start_color} Found love in clinking all_review button :)  {end_color}".\
            #    format(start_color=bcolors.OKGREEN, end_color=bcolors.RESET)
        except NoSuchElementException:
            print "{start_color} ERROR: Couldnt not clicked on all review button {end_color}".\
                format(start_color=bcolors.FAIL, end_color=bcolors.RESET)
            pass
        except:
            pass

        time.sleep(10)

        # checking out the number of reviews that are new in the page; we do
        # this by counting the records stored in database already and subracting
        # it by the total number of reviews found at the present time. This
        # count determines the number of reviews that are new and also how many
        # times the 'load-more' button needs to be clicked in order to access
        # all the remaining reviews
        try:
            reviews_to_be_scraped = int(self.eatery["eatery_total_reviews"]) - int(self.reviews_inDB)
            print "{start_color} No. of reviews to be scraped {number}{end_color}".\
                format(start_color=bcolors.OKGREEN, number=reviews_to_be_scraped, end_color=bcolors.RESET)
            print "{start_color} No. of reviews present in the DB  {number}{end_color}".\
                format(start_color=bcolors.OKGREEN, number=int(self.reviews_inDB), end_color=bcolors.RESET)
            print "{start_color} No. of reviews that were eariler on the page  {number}{end_color}".\
                format(start_color=bcolors.OKGREEN, number=int(self.previous_total_reviews), end_color=bcolors.RESET)
        except TypeError as e:
            print_messege("error", "total reviews key error", "EateryData.get_reviews", e, self.eatery["eatery_id"],\
                          self.eatery["eatery_url"], None)
            return

        #def retry_if_standard_error(exception):
        #    """Return True if we should retry (in this case when it's an StandardError), False otherwise"""
        #    return isinstance(exception, StandardError)

        #@retry(retry_on_result=retry_if_standard_error, wait_fixed=10000, stop_max_attempt_number=5)
        #def run_load_more():
        #    try:
        #        print "Click on loadmore <<{value}>> time".format(start_color=bcolors.OKBLUE, value=i, end_color=bcolors.RESET)
        #        driver.find_element_by_class_name("zs-load-more-count").click()
        #        time.sleep(1)
        #    except NoSuchElementException as e:
        #        print "{color} ERROR: Catching Exception -<{error}>- with messege -<No More Loadmore tag present>- {reset}".format(color=bcolors.OKGREEN, error=e, reset=bcolors.RESET)
        #        pass
        #    except urllib2.URLError:
        #        driver.quit()
        #        #raise StandardError("Could not make the request")
        #        pass
        #    except WebDriverException:
        #        driver.quit()
        #        #raise StandardError("Could not make the request")
        #        pass
        #    except Exception as e:
        #        print e
        #        pass

        #if ZomatoReviewsCollection.find({"eatery_id": self.eatery["eatery_id"]}).count() == 0:
        #    # for i in range(0, reviews_to_be_scraped/5+50):
        #    for i in range(0, reviews_to_be_scraped/5+10):
        #        run_load_more()
        #else:
        #    for i in range(0, reviews_to_be_scraped/5+60):
        #        run_load_more()

        # Function to constantly clicking on 'load-more' button. This function
        # keeps finding and clicking 'load-more' button until the limit passed
        # to it is exhausted or if the load-more button doesnt exists (i.e. all
        # the avaliable reviews are loaded). In the second case it checks for no
        # element condition 5 times before terminating
        def run_load_more(limit=None):
            # to track number of times
            # button is clicked successfully
            count=0

            # to track number of times
            # NoSuchElementException occurs
            no_element_count = 0
            exception_count = 0

            while True:
                try:
                    print "Click on loadmore <<{value}>> time".format(start_color=bcolors.OKBLUE, value=count, end_color=bcolors.RESET)
                    # locating load-more button and clicking on it
                    driver.find_element_by_class_name("zs-load-more-count").click()
                    driver.implicitly_wait(3)
                    count += 1 # incrementing the count
                    no_element_count = 0
                    exception_count = 0
                    if limit:
                        if count == limit:
                            print ' > got the reviews within  given limit'
                            # terminate loop since the limit is achieved
                            break
                except NoSuchElementException:
                    no_element_count += 1
                    print "{color} ERROR: Catching Exception -<{error}>- with messege -<No More Loadmore tag present>- {reset}".format(color=bcolors.OKGREEN, error="NoSuchElementException", reset=bcolors.RESET)
                    if no_element_count == 5:
                        # terminate since no element error has continouly
                        # occured 5 times (means this confirms that element
                        # doesnt exits at this point)
                        break
                except Exception as e:
                    print "{color} ERROR: Catching Unknown Exception -<{error}>- {reset}".format(color=bcolors.OKGREEN, error=e, reset=bcolors.RESET)
                    exception_count += 1
                    if exception_count == 10:
                        print ' > Terminating because of constantly occuring exception'
                        break
                    no_element_count = 0

        # if this is the first time data is being extracted for the resturant,
        # then call the run_load_more function with no args, which will make the
        # process terminate when the NoSuchElementException happens
        if ZomatoReviewsCollection.find({"eatery_id": self.eatery["eatery_id"]}).count() == 0:
            run_load_more()
        else:
            # if the entry is already there for this eatery page, then set the
            # limit to reviews_to_be_scraped/5 since only 5 reviews are present
            # at a time plus 60 times more so to remove any duplicacy occuring
            # on the website
            run_load_more(int(reviews_to_be_scraped/5)+60)

        # trying to read long reviews having 'read more' button
        read_more_links = driver.find_elements_by_xpath("//a[@class='read-more']")
        read_more_count = range(0, len(read_more_links))[::-1]
        time.sleep(10)

        for link, __count in zip(read_more_links, read_more_count):
            print "Click on read_more  <<{value}>>  <<{count}>>time".format(start_color=bcolors.OKBLUE, value=link, count=__count, end_color=bcolors.RESET)
            time.sleep(random.choice([1, 2]))
            try:
                link.send_keys("\n")
            except Exception as e:
                print "  >> Read More link err"
                print "  >>", str(e)

        html = driver.page_source
        content = html.encode('ascii', 'ignore').decode('ascii')
        driver.quit()

        return BeautifulSoup.BeautifulSoup(content)

    def retry_eatery_id(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_id") ))

    def retry_eatery_name(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_name")))

    def eatery_update_on(self):
        return time.time()

    def eatery_area_or_city(self):
        return self.eatery["eatery_url"].split("/")[3]

    def eatery_country(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_country") ))

    def retry_eatery_address(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_address")))

    def retry_eatery_cuisine(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_cuisine")))

    def retry_eatery_cost(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_cost")))

    def retry_eatery_rating(self):
        if not self.eatery.get("eatery_rating"):
            __result = {"rating": eval("self.soup.{0}".format(config.get("zomato", "eatery_rating"))),
                        "votes": eval("self.soup.{0}".format(config.get("zomato", "eatery_votes")))}
            return __result

    def retry_eatery_trending(self):
        return [e.text for e in eval("self.soup.{0}".format(config.get("zomato", "eatery_trending")))]

    def eatery_highlights(self):
        return [dom.text.replace("\n", "") for dom in eval("self.soup.{0}".format(config.get("zomato", "eatery_highlights")))]

    def eatery_popular_reviews(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_popular_reviews")))

    def eatery_known_for(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_known_for")))

    def eatery_opening_hours(self):
        return [[l.text  for l in e.findChildren()] for e in \
                eval("self.soup.{0}".format(config.get("zomato", "eatery_opening_hours"))) ]

    def eatery_recommended_order(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_recommended_order")))

    def eatery_buffet_price(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_buffet_price")))

    def eatery_buffet_details(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_buffet_details")))

    def eatery_longitude_latitude(self):
        __result = [eval("self.soup.{0}".format(config.get("zomato", "eatery_latitude"))),\
                    eval("self.soup.{0}".format(config.get("zomato", "eatery_longitude")))]
        return __result

    def eatery_total_reviews(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_total_reviews")))

    def eatery_photo_link(self):
        return eval("self.soup.{0}".format(config.get("zomato", "eatery_photo_link")))


'''
if __name__ == '__main__':
    # i = EateriesList("https://www.zomato.com/bangalore/restaurants", 30, 0, False)
    i = EateriesList("https://www.zomato.com/mumbai/restaurants", 30, 0, False)
    eateries = i.eateries_list
    print ' >> Total Eateries :', len(eateries)
    # x = EateryData({"eatery_url": "https://www.zomato.com/mumbai/udta-punjab-goregaon-west"})
    #x = EateryData({"eatery_url": "https://www.zomato.com/mumbai/ftn-malad-west"})
    for eatry in eateries[:1]:
        x = EateryData(eatry)
        result = x.run()
        print type(result)
        print len(result)
        pprint.pprint(result[0])
        # pprint.pformat(obj[0])
        # print '\n----8th review of Eatery----\n'
        # pprint.pprint(obj[1][7])
'''
