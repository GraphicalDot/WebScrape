#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
# import csv
# import codecs
import time
import random
# import goose
import BeautifulSoup
import re
import math
import timeit
from Testing_database import eatery_collection, review_collection, user_collection
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from review_scrape import ZomatoReviews
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from Testing_db_insertion import DBInsert
from Testing_colored_print import bcolors
from db_insertion import DBInsert
import pprint
from colored import fg, bg, attr
from error_decorators import print_messege, process_result
import ConfigParser
import datetime 
from selenium.common.exceptions import WebDriverException
from retrying import retry
import urllib2
import getpass
import hashlib
import pymongo
from blessings import Terminal
terminal= Terminal()
FILE = os.path.basename(__file__)  

config = ConfigParser.RawConfigParser()
config.read("global.cfg")
config.read("zomato_dom.cfg")

driver_exec_path = "/home/%s/Downloads/chromedriver"%(getpass.getuser())
DRIVER_NAME = "CHROME"


connection = pymongo.MongoClient(config.get("zomato", "host"), config.getint("zomato", "port"))
ZomatoReviewsCollection = connection[config.get("zomato", "database")][config.get("zomato", "reviews")]
PROXY_ADDRESS = config.get("proxy", "proxy_Addr")



class AllEateriesUrl(object):
        def __init__(self, url):
                """
                Get all the pagination link present for paricular region for example delhi ncr
                """



        def prepare_soup(self, url):
                if DRIVER_NAME == "PhantomJS":
                        driver = webdriver.PhantomJS()
                        driver.get(url)
                else:
                        driver = webdriver.Chrome(driver_exec_path)
                        driver.get(url)
                
                
                html = driver.page_source
        	content = html.encode('ascii', 'ignore').decode('ascii')
        	soup = BeautifulSoup.BeautifulSoup(content)
        	driver.close()
                return soup





class EateriesList(object):

	def __init__(self, url, number_of_restaurants=None, skip=0, is_eatery=False):
                """
                Args:
                        url
                        number_of_restaurants: number_of_restaurants to be scraped
                                default: None, which implies to scrape whole url
                                else multiple of 30 to scrape number of pages

                        skip: type int
                            number of pages to be skipped


                if only second page  to be scraped 
                    pass number_of_restaurants= 30
                    skip = 1

                if all pages to scraped:
                    pass None to skip and number_of_restaurants
                """
                self.eateries_list = []

		if is_eatery:
			#This implies that the url that has been given to initiate this class is the restaurant url not a url on which 
			#lots of restaurant urls are present
			self.url = url
			eatery_dict= {"eatery_url": self.url}
		        self.eateries_list.append(eatery_dict) 
		else:
			self.url = url
			self.number_of_restaurants = number_of_restaurants
			self.skip = skip

                        ##Each page has 30 eateries, so number_of_restaurants must be a multiple of 30
                        assert(number_of_restaurants%30 == 0)

                        if number_of_restaurants:
                                number_of_pages = number_of_restaurants/30
                        else:
                                number_of_pages = None

                        
			self.soup_only_for_pagination = self.prepare_soup(self.url)
				
                        pagination_divs = self.soup_only_for_pagination.findAll("div", {"class": "col-l-3 mtop0 alpha tmargin pagination-number"})
			
                        for div in pagination_divs:
					try:
						pages_number=int(div.div.string.split(" ")[-2])
					except :
						pages_number=1
			try:
			        pages_url = ["%s?page=%s"%(self.url, page_number) for page_number in range(1, int(pages_number)+1)]
				"""Pagination Done"""
                        except Exception as e:
                                print e
				print "{start_color} Seems some problem with pagination  {end_color}".format(start_color=bcolors.FAIL, end_color=bcolors.RESET)

                   


                        print "number_of_pages == %s"%number_of_pages
                        print "Pages to be scraped %s"%pages_url[skip: skip+number_of_pages]
			for page_link in pages_url[skip: skip+number_of_pages]:
					print "{start_color} -<Loading  {val}>- {end_color}".format(start_color=bcolors.OKBLUE, val=page_link, end_color=bcolors.RESET)
					"""
                                        if page_link == self.url:
						# self.prepare_and_return_eateries_list(self.soup_only_for_pagination,page_link)
						temp_list=self.prepare_and_return_eateries_list(self.soup_of_each_page, page_link)
						self.Calling_Processing_one_eatery______(temp_list)
					
                                        else:
						self.soup_of_each_page = self.prepare_soup(page_link)
						temp_list=self.prepare_and_return_eateries_list(self.soup_of_each_page,page_link)
						self.Calling_Processing_one_eatery______(temp_list)
                                        """
					# self.prepare_and_return_eateries_list(self.soup_only_for_pagination,page_link)
					temp_list = self.prepare_and_return_eateries_list(page_link)
                                        self.eateries_list.extend(temp_list)
                
                return 
    
        def prepare_soup(self, url):
        	# if url.find("=")==-1:
                if config.getboolean("proxy", "use_proxy"):
                        if DRIVER_NAME == "PhantomJS":
                                service_args =[config.get("proxy", "service_args")]
                                driver = webdriver.PhantomJS(service_args=service_args)
                                driver.get(url)
                        else:
                                chrome_options = webdriver.ChromeOptions()
                                chrome_options.add_argument('--proxy-server=%s' % PROXY_ADDRESS)
                                driver = webdriver.Chrome(driver_exec_path, chrome_options=chrome_options)
                                driver.get(url)

                else:
                        if DRIVER_NAME == "PhantomJS":
                                driver = webdriver.PhantomJS()
                                driver.get(url)
                        else:
                                driver = webdriver.Chrome(driver_exec_path)
                                driver.get(url)
                
                
                html = driver.page_source
        	# f=open("Testingfile.txt","w")
        	content = html.encode('ascii', 'ignore').decode('ascii')
        	# f.write(content)
        	# f.close()

        	# with open("Testingfile.txt","r") as content_file:
        	# 	content = content_file.read()
        	soup = BeautifulSoup.BeautifulSoup(content)
        	driver.quit()
                return soup

	def prepare_and_return_eateries_list(self, page_link):
                soup_of_each_page = self.prepare_soup(page_link)

        
		eateries_list=list()
                for eatery_soup in soup_of_each_page.findAll("li",{"class":"js-search-result-li even  status 1"}):
			eatery = dict()
			eatery["eatery_id"] = eatery_soup.get("data-res_id")
			eatery["eatery_photo_link"] = eatery_soup.find("a").get("href")
                        def some(__soup, eatery_name=None):
                                try:
                                        result = __soup.find("h3", {"class":" top-res-box-name left"}).find("a")

                                except Exception as e:
                                        result = __soup.find("h3", {"class":"pt5 top-res-box-name left"}).find("a")
                                        
                                return result["href"] if not eatery_name else result.text
                        eatery["eatery_url"] = some(eatery_soup)
			eatery["eatery_name"] = some(eatery_soup, True)

                        try:
                                eatery["eatery_address"] = eatery_soup.find("div", {"class": "search-result-address zdark"})["title"]
			except Exception:
				print "{start_color} Eatery address couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)
				eatery["eatery_address"] = None
                                
			try:
                                eatery["eatery_cuisine"] = eatery_soup.find("div", {"class":"res-cuisine mt2 clearfix"})["title"]
			except Exception:
				eatery["eatery_cuisine"] = None
				print "{start_color} Eatery cuisine couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.WARNING, id=eatery["eatery_id"], end_color=bcolors.RESET)

			try:
                                eatery["eatery_cost"] = eatery_soup.find("div", {"class":"res-cost clearfix"}).findNext().findNext().text
			except Exception:
				eatery["eatery_cost"] = None
				print "{start_color} Eatery cost couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.FAIL, id=eatery["eatery_id"], end_color=bcolors.RESET)


			try:
                                eatery["eatery_type"] = eatery_soup.find("div", {"class": 'res-snippet-small-establishment'}).text

			except Exception:
				eatery["eatery_type"] = None
				print "{start_color} Eatery type  couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.FAIL, id=eatery["eatery_id"], end_color=bcolors.RESET)




                        ##eatery_delivery_time
                        try:
                                delivery_time_tag = eatery_soup.find("div", {"class": "del-time"})
                                try:
                                        delivery_time_span = delivery_time_tag.find("span")
                                        delivery_time_span.extract()
                                except:
                                        pass
                                
                                eatery["eatery_delivery_time"] = delivery_time_tag.text
                        
			except Exception:
				eatery["eatery_delivery_time"] = None
				print "{start_color} Eatery delivery time couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.FAIL, id=eatery["eatery_id"], end_color=bcolors.RESET)



                        ##eatery_minimum_order
                        try:
                                eatery_minimum_order_tag = eatery_soup.find("div", {"class": "del-min-order"})
                                try:
                                        eatery_minimum_span = eatery_minimum_order_tag.find("span")
                                        eatery_minimum_span.extract()
                                except:
                                        pass
                                eatery["eatery_minimum_order"] = eatery_minimum_order_tag.text


			except Exception:
				eatery["eatery_minimum_order"] = None
				print "{start_color} Eatery minimum order couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.FAIL, id=eatery["eatery_id"], end_color=bcolors.RESET)
			
                        
                        
                        try:
                                eatery["eatery_rating"] = {"rating": eatery_soup.find("div",  {"class": "search_result_rating col-s-3  clearfix"}).findNext().text,
                                    "votes": eatery_soup.find("div",  {"class": "rating-rank right"}).find("span").text }                                
			except Exception:
				eatery["eatery_rating"] = None
				print "{start_color} Eatery rating couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.FAIL, id=eatery["eatery_id"], end_color=bcolors.RESET)

			try:
				eatery["eatery_title"] = eatery_soup.findNext().get("title")
			except Exception:
				eatery["eatery_title"] = None
				print "{start_color} Eatery title couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.FAIL, id=eatery["eatery_id"], end_color=bcolors.RESET)
			
			try:
				collection_of_trending =  eatery_soup.find("div", {"class": "srp-collections"}).findAll("a")
				eatery["eatery_trending"] = [element.text for element in collection_of_trending]

			except Exception:
				eatery["eatery_trending"] = None
				print "{start_color} Eatery trending  couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.FAIL, id=eatery["eatery_id"], end_color=bcolors.RESET)

			##Finding total number of reviews for each eatery soup
			try:
				eatery["eatery_total_reviews"] = eatery_soup.find("a", {"data-result-type": "ResCard_Reviews"}).text.split(" ")[0]
			except Exception:
				eatery["eatery_total_reviews"] = 0
				print "{start_color} Eatery aotal reviews  couldnt be found for eatery_id --<<{id}-->> {end_color}".format(start_color=bcolors.FAIL, id=eatery["eatery_id"], end_color=bcolors.RESET)

			
                        print "{start_color} Eatery with --<<{id}-->> is completed  {end_color}".format(start_color=bcolors.OKGREEN, id=eatery["eatery_id"], end_color=bcolors.RESET)
			eateries_list.append(eatery)
		return eateries_list

class EateryData(object):

	def __init__(self, eatery_dict):
                
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
	        
                #self.last_no_of_reviews_to_be_scrapped = int(self.no_of_reviews_to_be_scrapped) - int(no_of_blogs)
                ins = ZomatoReviews(review_soup, self.eatery["eatery_area_or_city"], self.eatery["eatery_id"], self.eatery["eatery_url"])
                return (self.eatery, ins.reviews_data)

        def make_soup(self):
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
			driver.find_elements_by_xpath('//*[@id="res-timings-toggle"]')[0].click()
                except Exception as e:
			print e
			pass
		time.sleep(3)
                html = driver.page_source
                driver.quit()
                
                return BeautifulSoup.BeautifulSoup(html)

        

        def get_reviews(self):
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
                time.sleep(50)
                try:
                        driver.find_element_by_css_selector("a.everyone.empty").click()
                        time.sleep(20)
                        driver.find_element_by_css_selector("a.everyone.empty").click()
                        driver.find_element_by_css_selector("a.everyone.empty").click()
                        driver.find_element_by_css_selector("a.everyone.empty").click()
                        driver.find_element_by_css_selector("a.everyone.empty").click()
                        driver.find_element_by_css_selector("a.everyone.empty").click()
			print "{start_color} Found love in clinking all_review button :)  {end_color}".format(\
                                start_color=bcolors.OKGREEN, end_color=bcolors.RESET)

                except NoSuchElementException:
                        print "{start_color} ERROR: Couldnt not clicked on all review button {end_color}".format(\
                                start_color=bcolors.FAIL, end_color=bcolors.RESET)
                        
                        pass

                time.sleep(10)


                try:
			reviews_to_be_scraped = int(self.eatery["eatery_total_reviews"]) - int(self.reviews_inDB)
			#reviews_to_be_scraped = int(self.eatery["eatery_total_reviews"]) - int(self.previous_total_reviews)
                        print "{start_color} No. of reviews to be scraped {number}{end_color}".format(\
                                start_color=bcolors.OKGREEN, number=reviews_to_be_scraped, end_color=bcolors.RESET)
                        
			print "{start_color} No. of reviews present in the DB  {number}{end_color}".format(\
                                start_color=bcolors.OKGREEN, number=int(self.reviews_inDB), end_color=bcolors.RESET)
			
                        print "{start_color} No. of reviews that were eariler on the page  {number}{end_color}".format(\
                                start_color=bcolors.OKGREEN, number=int(self.previous_total_reviews), end_color=bcolors.RESET)

			
                except TypeError as e:
                        print_messege("error", "total reviews key error", "EateryData.get_reviews", e, self.eatery["eatery_id"],\
                        self.eatery["eatery_url"], None)
                        return 


		

		def retry_if_standard_error(exception):
			"""Return True if we should retry (in this case when it's an StandardError), False otherwise"""
			return isinstance(exception, StandardError)




		@retry(retry_on_result=retry_if_standard_error, wait_fixed=10000, stop_max_attempt_number=5)
		def run_load_more():
                	try:
                        
                                	print "Click on loadmore <<{value}>> time".format(start_color=bcolors.OKBLUE, value=i, end_color=bcolors.RESET)
                                	##time.sleep(random.choice([2, 3]))
                                	driver.find_element_by_class_name("load-more").click()
                                	time.sleep(1)

                	except NoSuchElementException as e:
                        	print "{color} ERROR: Catching Exception -<{error}>- with messege -<No More Loadmore tag present>- {reset}".format(color=bcolors.OKGREEN, error=e, reset=bcolors.RESET)
				pass

                	except urllib2.URLError:
                        	driver.quit()
				#raise StandardError("Could not make the request")
				pass                	

			except WebDriverException:
                        	driver.quit()
				#raise StandardError("Could not make the request")
				pass			

			except Exception as e:
				print e		
				pass

		if ZomatoReviewsCollection.find({"eatery_id": self.eatery["eatery_id"]}).count() == 0:

			for i in range(0, reviews_to_be_scraped/5+500):
				run_load_more()
			
		else:
			for i in range(0, reviews_to_be_scraped/5+60):
				run_load_more()
				


                read_more_links = driver.find_elements_by_xpath("//div[@class='rev-text-expand']")
                read_more_count = range(0, len(read_more_links))[::-1]


		time.sleep(10)
		for link, __count in zip(read_more_links, read_more_count):
                        print "Click on read_more  <<{value}>>  <<{count}>>time".format(start_color=bcolors.OKBLUE, value=link, count=__count, end_color=bcolors.RESET)
                        time.sleep(random.choice([1, 2]))
                        link.click()

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
                return [[l.text  for l in e.findChildren()] for e in eval("self.soup.{0}".format(config.get("zomato", "eatery_opening_hours"))) ]


	def eatery_recommended_order(self):
                return eval("self.soup.{0}".format(config.get("zomato", "eatery_recommended_order")))
	
        def eatery_buffet_price(self):
                return eval("self.soup.{0}".format(config.get("zomato", "eatery_buffet_price")))
        
        def eatery_buffet_details(self):
                return eval("self.soup.{0}".format(config.get("zomato", "eatery_buffet_details")))
	
        
        def eatery_longitude_latitude(self):
                        __result = [ eval("self.soup.{0}".format(config.get("zomato", "eatery_latitude"))),  \
                                 eval("self.soup.{0}".format(config.get("zomato", "eatery_longitude")))]
		
                        return __result 
	
        def eatery_total_reviews(self):
                return eval("self.soup.{0}".format(config.get("zomato", "eatery_total_reviews")))
        
        def eatery_photo_link(self):
                return eval("self.soup.{0}".format(config.get("zomato", "eatery_photo_link")))


        """
	def eatery_reviews(self):
		eatery_area_or_city = self.eatery["eatery_area_or_city"]
		instance = Reviews(self.soup, eatery_area_or_city,int(self.no_of_reviews_to_be_scrapped),int(no_of_blogs))
		self.eatery["reviews"] = instance.reviews_data
		self.eatery["eatery_reviews_in_collection"]=len(self.eatery["reviews"])
		return
        """


if __name__ == "__main__":


	"""
	##number_of_restaurants = 60
	##skip = 10
	##is_eatery = False
        url = "https://www.zomato.com/ncr/restaurants"

	ins = EateriesList(driver_exec_path, url, 30, 5, False)
        for e in ins.eateries_list:
                print e
        """
        i = EateriesList("https://www.zomato.com/bangalore/restaurants", 30, 0, False)
        for e in i.eateries_list:
            print e
        #ins = EateryData({"eatery_url": "https://www.zomato.com/mumbai/between-breads-pali-hill-bandra-west"})
        #ins = EateryData({"eatery_url": "https://www.zomato.com/ncr/asian-haus-1-east-of-kailash-new-delhi"})
        #print ins.eatery



