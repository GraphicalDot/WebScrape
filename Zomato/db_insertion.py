#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
This is the file responsible for actually inserting data in the database.
"""

from Testing_database import DB, collection, client
#from custom_logging import exceptions_logger
import traceback
import sys
import os
import logging
import inspect
#from main_scrape import scrape
import pymongo
import traceback
import time
from pymongo.errors import BulkWriteError
from colored import fg, bg, attr
from error_decorators import print_messege

FILE = os.path.basename(__file__)  
#LOG_FILENAME = 'exceptions_logger.log'
#:wlogging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,)

import ConfigParser                                                                                                                                                                                                                        
config = ConfigParser.RawConfigParser()
config.read("global.cfg")
config.read("zomato_dom.cfg")

connection = pymongo.MongoClient(config.get("zomato", "host"), config.getint("zomato", "port"))
ZomatoReviews = connection[config.get("zomato", "database")][config.get("zomato", "reviews")]
ZomatoEateries = connection[config.get("zomato", "database")][config.get("zomato", "eatery")]
ZomatoUsers= connection[config.get("zomato", "database")][config.get("zomato", "users")]



class DBInsert(object):

	@staticmethod
	def db_insert_eateries(eatery):
		# db = client.modified_canworks  I think needed for bulk
		try:
			ZomatoEateries.update({"eatery_id": eatery.get("eatery_id")}, {"$set": eatery}, upsert=True)
                        messege = "Eatery with eatery_id: %s  and eatery_name: %s has been updated successfully"%(eatery["eatery_id"], eatery["eatery_name"]) 
                        try:

                                print_messege("success", messege, inspect.stack()[0][3], None,  eatery["eatery_id"], eatery["eatery_url"], None, FILE)
                        except Exception as e:
                                print e
                except Exception as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()                                                                                                                                                                    
                        error = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))  
                        messege = "Eatery with eatery_id: %s  and eatery_name: %s failed"%(eatery["eatery_id"], eatery["eatery_name"]) 
                        try:

                                print_messege("error", messege, inspect.stack()[0][3], error,  eatery["eatery_id"], eatery["eatery_url"], None, FILE)
                        except Exception as e:
                                print e
		return
	
	@staticmethod
	def db_insert_reviews(reviews):
		for review in reviews:
			try:
				ZomatoReviews.insert(review)
                                messege = "Review  with review_id: %s  has been updated successfully"%(review["review_id"]) 
                                print_messege("success", messege, inspect.stack()[0][3], None,  review["eatery_id"], None, review["review_id"], FILE)
                        
                        except Exception as e:
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                error = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))  
                                messege = "Review  with review_id: %s  failed"%(review["review_id"]) 
                                print_messege("error", messege, inspect.stack()[0][3], error,  review["eatery_id"], None, review["review_id"], FILE)
                                pass

                eatery_id = review.get("eatery_id") 
                return 


        @staticmethod
	def db_insert_users(reviews):
		for review in reviews:
			try:
				result = ZomatoUsers.update({"user_id": review.get("user_id"), "user_name": review.get("user_name")},{"$set": \
                                        {"user_url": review.get("user_url"), "user_followers": review.get("user_followers"), "user_reviews" : \
                                        review.get("user_reviews"), "updated_on": int(time.time())}}, upsert=True)
                                messege = "User with user_id: %s  and user_name: %s has been updated successfully"%(review["user_id"], review["user_name"]) 
                                print_messege("success", messege, inspect.stack()[0][3], None,  review["eatery_id"], None, review["review_id"], FILE)
			
                        except Exception as e:
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                error = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))  
                                messege = "User  with user_id: %s  failed"%(review["user_id"]) 
                                print_messege("error", messege, inspect.stack()[0][3], error,  review["eatery_id"], None, review["review_id"], FILE)
                                pass

		return


        @staticmethod
	def db_get_reviews_eatery(eatery_id):
                return ZomatoReviews.find({"eatery_id": eatery_id}).count()
        
        
        @staticmethod
	def flush_eatery(eatery_url):
                try:
			eatery_id = ZomatoEateries.find_one({"eatery_url": eatery_url}).get("eatery_id")
                	print ZomatoReviews.remove({"eatery_id": eatery_id})
                except Exception as e:
			print e
			pass
		return


