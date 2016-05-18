#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import celery
from celery import states
from celery.task import Task, TaskSet
from celery.result import TaskSetResult
from celery.utils import gen_unique_id, cached_property
from celery.decorators import periodic_task
from datetime import timedelta
from celery.utils.log import get_task_logger
import time
import pymongo
import random
from celery_app.App import app
from main_scrape import EateriesList, EateryData
from celery.registry import tasks
import logging
import inspect
from celery import task, subtask, group
from colored_print import bcolors
from colored import fg, bg, attr
from db_insertion import DBInsert
import pprint
from celery.exceptions import Ignore
import redis
import os 
from celery.task.control import revoke


FILE = os.path.basename(__file__)
connection = pymongo.Connection()
db = connection.intermediate
collection = db.intermediate_collection
import traceback
from error_decorators import print_messege
from selenium import webdriver
import re
import getpass
from google_n_pics import GoogleNPics
from google_places import find_google_places


logger = logging.getLogger(__name__)

##If set to True all the scraping results will be udpated to the database
UPDATE_DB = True
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read("zomato_dom.cfg")
driver_exec_path = "/home/%s/Downloads/chromedriver"%(getpass.getuser())
DRIVER_NAME = "CHROME"
PROXY_ADDRESS = config.get("proxy", "proxy_addr")

#StartScrapeChain.apply_async(["https://www.zomato.com/ncr/restaurants", 30, 0, False])
from blessings import Terminal
terminal = Terminal()
"""
To run tasks for scraping one restaurant 
runn.apply_async(["https://www.zomato.com/ncr/pita-pit-lounge-greater-kailash-gk-1-delhi", None, None, True])

TO scrape a list of restaurant use this
runn.apply_async(args=["https://www.zomato.com/ncr/south-delhi-restaurants", 30, 270, False])
	 Task.acks_late
	     If set to True messages for this task will be acknowledged after the task has been executed, 
	     not just before, which is the default behavior.
	
	Task.ErrorMail
	    If the sending of error emails is enabled for this task, then this is the class defining the 
	    logic to send error mails.
	
	Task.store_errors_even_if_ignored
	    If True, errors will be stored even if the task is configured to ignore results.

	
	Task.ErrorMail
	    If the sending of error emails is enabled for this task, then this is the class defining the 
	    logic to send error mails.


	 Task.rate_limit
	     Set the rate limit for this task type which limits the number of tasks that can be run in a 
	     given time frame. Tasks will still complete when a rate limit is in effect, but it may take 
	     some time before it’s allowed to start.
	     If this is None no rate limit is in effect. If it is an integer or float, it is interpreted as 
	     “tasks per second”.
	     The rate limits can be specified in seconds, minutes or hours by appending “/s”, “/m” or “/h” 
	     to the value. Tasks will be evenly distributed over the specified time frame.
	     Example: “100/m” (hundred tasks a minute). This will enforce a minimum delay of 600ms between 
	     starting two tasks on the same worker instance.
"""


r = redis.StrictRedis(host=config.get("redis", "ip"), port=config.getint("redis", "port"), db=config.getint("redis", "error_db"))
r_pics = redis.StrictRedis(host=config.get("redis", "ip"), port=config.getint("redis", "port"), db=config.getint("redis", "pics_error_db"))


@app.task()
class GenerateEateriesList(celery.Task):
        ignore_result = True
        max_retries = 3
        retry = True
	acks_late=True
        default_retry_delay=5
        print "{start_color} {function_name}:: This worker is meant to get all the eateries dict present\n\
                on the url given to it {end_color}".format(\
                start_color=bcolors.OKGREEN, function_name=inspect.stack()[0][3], end_color = bcolors.RESET)
        def run(self, url, number_of_restaurants, skip, is_eatery):
	        self.start = time.time()
                eateries_list = EateriesList(url, number_of_restaurants, skip, is_eatery)
                result = eateries_list.eateries_list
                for eatery in result:
	                print "{fg}{bg} Eatery with eatery details {eatery} {reset}".format(fg=fg("green"), \
                        bg=bg("dark_blue"), eatery=eatery, reset=attr("reset"))
            
                return result
        
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
                #exit point of the task whatever is the state
                logger.info("{fg} {bg}Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(fg=fg('white'), bg=bg('green'), \
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__,
                            time=time.time() -self.start, reset=attr('reset')))
                pass

        def on_failure(self, exc, task_id, args, kwargs, einfo):
                logger.info("{fg}{bg}Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(fg=fg("white"), bg=bg("red"),\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=attr('reset')))
                logger.info("{fg}{bg}{einfo}".format(fg=fg("white"), bg=bg("red"), einfo=einfo))
                self.retry(exc=exc)



@app.task()
class GoogleNPicsTask(celery.Task):
	ignore_result=True, 
	max_retries=5, 
	acks_late=True
	default_retry_delay = 500
        def run(self, eatery_id, __eatery_id, pics_url):
                self.eatery_id = eatery_id
                try:
                        instance = GoogleNPics(eatery_id, __eatery_id, pics_url)
                        instance.run()    
                except Exception as e:
                        print terminal.red("error occurred saving in redis %s for eatery_id %s"%(str(e), self.eatery_id))
                        r_pics.hset(eatery_id, "error",  str(e))
                return

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
                #exit point of the task whatever is the state
                pass

        def on_failure(self, exc, task_id, args, kwargs, einfo):
                print terminal.red("error occurred saving in redis %s for eatery_id %s"%(str(e), self.eatery_id))
                r_pics.hset(self.eatery_id, "error", str(e))
		revoke(task_id, terminate=True)
		return 


@app.task()
class ScrapeEachEatery(celery.Task):
	ignore_result=True, 
	max_retries=5, 
	acks_late=True
	default_retry_delay = 500
        print "{start_color} {function_name}:: This worker is when given a eatery_dict scrapes more information\n\
                about that eatery and also scrapes review that has been written after the last time eatery was \n\
                scraped, calls EateryData which returns eatery_dict and review_list\n\
                Also it is also responsible to inserting that data into backend database{end_color}".format(\
                start_color=bcolors.OKGREEN, function_name=inspect.stack()[0][3], end_color = bcolors.RESET)
	
                
        def run(self, eatery_dict, flush_eatery=False):
		self.eatery_dict = eatery_dict
	        self.start = time.time()

            
                if flush_eatery:
                        DBInsert.flush_eatery(self.eatery_dict["eatery_url"])


                logger.info("{fg} {bg}Starting eatery_url --<{url}>-- of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(fg=fg('white'), bg=bg('green'), \
                        url=eatery_dict["eatery_url"], task_name= self.__class__.__name__,
                            time=time.time() -self.start, reset=attr('reset')))
		
                __instance = EateryData(eatery_dict)

		eatery_dict, reviewslist = __instance.run()
                     
		DBInsert.db_insert_eateries(eatery_dict)
		DBInsert.db_insert_reviews(reviewslist)
		DBInsert.db_insert_users(reviewslist)
                
                reviews_in_db =DBInsert. db_get_reviews_eatery(eatery_dict["eatery_id"])
                if reviews_in_db !=  int(eatery_dict['eatery_total_reviews']):
                        messege = "Umatched reviews: present in DB %s and should be %s"%(reviews_in_db,  int(eatery_dict['eatery_total_reviews']))
                        print_messege("error", messege, "ScrapeEachEatery.run", None, eatery_dict["eatery_id"], eatery_dict["eatery_url"], None, module_name=FILE)
                        if not reviews_in_db -10 >= int(eatery_dict['eatery_total_reviews']) >= reviews_in_db + 10:
                        	r.hset(eatery_dict["eatery_url"], "unmatched_reviews", messege)
                        	r.hset(eatery_dict["eatery_url"], "total_reviews",  int(eatery_dict['eatery_total_reviews']))
                        	r.hset(eatery_dict["eatery_url"], "reviews_in_db", reviews_in_db)
                                r.hset(eatery_dict["eatery_url"], "error_cause", "zomato incompetency")
                                r.hset(eatery_dict["eatery_url"], "frequency", reviews_in_db -  int(eatery_dict['eatery_total_reviews']))
        
                print eatery_dict
                eatery_id, __eatery_id, eatery_name, eatery_photo_link, location = eatery_dict["eatery_id"], eatery_dict["__eatery_id"], \
                                                    eatery_dict["eatery_name"], eatery_dict["eatery_photo_link"], eatery_dict["location"]
                
                
                print terminal.blue("Trying pics for eatery_id=<<%s>>, __eatery_id=<<%s>>, eatery_photo_link=<<%s>>"%(eatery_id, __eatery_id, eatery_photo_link))
                try:
                        instance = GoogleNPics(eatery_id, __eatery_id, eatery_photo_link)
                        instance.run()    
                except Exception as e:
                        print terminal.red("error occurred saving in redis %s for eatery_id %s"%(str(e), eatery_dict["eatery_id"]))
                        r_pics.hset(eatery_id, "error",  str(e))

                google = find_google_places(eatery_id, __eatery_id, eatery_name, location)
                print google
                return

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
                #exit point of the task whatever is the state
                logger.info("{fg} {bg}Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(fg=fg('white'), bg=bg('green'), \
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__,
                            time=time.time() -self.start, reset=attr('reset')))
                pass

        def on_failure(self, exc, task_id, args, kwargs, einfo):
                logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
		r.hset(self.eatery_dict["eatery_url"], "error", "Failed with on failure")
		r.hset(self.eatery_dict["eatery_url"], "frequency", 0)
		revoke(task_id, terminate=True)
		return 






@app.task()
class MapListToTask(celery.Task):
	ignore_result=True 
	max_retries=3 
	acks_late=True
	default_retry_delay = 5
        print "{start_color} {function_name}:: Maps EateriesList to EateryData, by creating parallel tasks \n\
                for EateryData {end_color}".format(\
                start_color=bcolors.OKGREEN, function_name=inspect.stack()[0][3], end_color = bcolors.RESET)
        def run(self, it, callback):
	# Map a callback over an iterator and return as a group
	        self.start = time.time()
	        callback = subtask(callback)
	        return group(callback.clone([arg,]) for arg in it)()

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
                logger.info("{fg} {bg}Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(fg=fg('white'), bg=bg('green'), \
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__,
                            time=time.time() -self.start, reset=attr('reset')))
                pass

        def on_failure(self, exc, task_id, args, kwargs, einfo):
                logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
                self.retry(exc=exc)


@app.task()
class StartScrapeChain(celery.Task):
	ignore_result=True 
	max_retries=3
	acks_late=True
	default_retry_delay = 5
        print "{start_color} {function_name}:: This worker is meant to scrape all the eateries present on the url \n\
                with their reviews, It forms chain between ScrapeEachEatery and GenerateEateriesList\n \
                for more information on monitoring of celery workers\n\
                visit: http://docs.celeryproject.org/en/latest/userguide/monitoring.html\n{end_color}".format(\
                start_color=bcolors.OKGREEN, function_name=inspect.stack()[0][3], end_color = bcolors.RESET)
        print "http://docs.celeryproject.org/en/latest/userguide/monitoring.html"
        
        def run(self, url, number_of_restaurants, skip, is_eatery):
	        self.start = time.time()
                global ip
                ip = None 
                #process_list = eateries_list.s(url, number_of_restaurants, skip, is_eatery)| dmap.s(process_eatery.s())
                process_list = GenerateEateriesList.s(url, number_of_restaurants, skip, is_eatery)| MapListToTask.s(ScrapeEachEatery.s())
	        process_list()
	        return
        
    
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
                #exit point of the task whatever is the state
                logger.info("{fg} {bg}IP:{IP}-- Ending --<{function_name}--> of task --<{task_name}>-- with time taken\
                        --<{time}>-- seconds  {reset}".format(fg=fg('white'), bg=bg('green'), \
                        IP=ip, function_name=inspect.stack()[0][3], task_name= self.__class__.__name__,
                        time=time.time() -self.start, reset=attr('reset')), extra={"ip": "182.98.89.90"})
                pass

        def on_failure(self, exc, task_id, args, kwargs, einfo):
                logger.info("{color} Ending --<{function_name}--> of task --<{task_name}>-- failed fucking\
                        miserably {reset}".format(color=bcolors.OKBLUE,\
                        function_name=inspect.stack()[0][3], task_name= self.__class__.__name__, reset=bcolors.RESET))
                logger.info("{0}{1}".format(einfo, bcolors.RESET))
                self.retry(exc=exc)
                
        
