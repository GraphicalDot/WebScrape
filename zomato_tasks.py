#!/usr/bin/env python

# local project imports
from main_scrape import EateriesList, EateryData
from colored_print import bcolors
from db_insertion import DBInsert
from google_n_pics import GoogleNPics
from error_decorators import print_messege
from google_places import find_google_places

# from celery_app.App import app

# libraries import
import celery
from celery import group, subtask, Celery, chain
from celery.task import Task
from celery.task.control import revoke
from colored import fg, bg, attr
import redis
from blessings import Terminal

# std library imports
import time
import os
import inspect
import logging
import ConfigParser


from traceback import print_exc

UPDATE_DB = True

terminal = Terminal()

app = Celery()
app.config_from_object('new_celeryconfig')

# defining vars
FILE = os.path.basename(__file__)

logger = logging.getLogger(__name__)

config = ConfigParser.RawConfigParser()

config.read("zomato_dom.cfg")

r = redis.StrictRedis(host=config.get("redis", "ip"),
                      port=config.getint("redis", "port"),
                      db=config.getint("redis", "error_db")
                      )

r_pics = redis.StrictRedis(host=config.get("redis", "ip"),
                           port=config.getint("redis", "port"),
                           db=config.getint("redis", "pics_error_db")
                           )


'''
Settings:
    abstract: Makes a class an Abstract Class, i.e. the class will be used as
              base class for a task.

    ignore_result: if True, state of the task is not stored, that means task
                   can't be used with AsyncResult to check if its ready and we
                   can't get its return value

    max_retries: maximum number of attempted retries before giving up on a task.
                 By default its 3, if set to None, the task will retry forever
                 until succeeds;
                 retry() is not automatically called, it needs to be called
                 manually.

    acks_late: If True, messages for the task will be acknowledged after the
               task has been executed, not just before, which is the default
               behavior.

    default_retry_delay: default time in seconds before a retry of the task
                         should be executed; default: 3 minutes

'''

class GetEateriesList_Base(Task):
    abstract = True
    max_retries = 3
    retry = True
    acks_late = True
    default_retry_delay = 5

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        logger.info("{fg}{bg} Ending --<get_eateries_list>-- \
                    task, Completed{reset}".format(fg=fg('white'),
                                        bg=bg('green'),
                                        reset=attr('reset')
                                        )
                    )
        print " >> GetEateriesList.after_retrun"
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.info("{fg}{bg} Ending --<get_eateries_list>-- \
                    task, failed miserably{reset}".format(fg=fg('white'),
                                        bg=bg('red'),
                                        reset=attr('reset')
                                        )
                    )

        logger.info("{fg}{bg}{einfo}".format(fg=fg("white"),
                                             bg=bg("red"),
                                             einfo=einfo
                                             )
                    )
        print " >> GetEateryList.on_failure"
        self.retry(exc=exc)


class ExecuteAllEatries_Base(Task):
    abstract = True
    max_retries = 3
    acks_late = True
    default_retry_delay = 5

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        logger.info("{fg}{bg} Ending --<execute_all_eateries>-- \
                    task, failed miserably{reset}".format(fg=fg('white'),
                                        bg=bg('green'),
                                        reset=attr('reset')
                                        )
                    )

        logger.info("{fg}{bg}{einfo}".format(fg=fg("white"),
                                             bg=bg("red"),
                                             einfo=einfo
                                             )
                    )

        print '>> ExecuteAllEatries.after_return'
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.info("{fg}{bg} Ending --<execute_all_eateries>-- \
                    task, failed miserably{reset}".format(fg=fg('white'),
                                        bg=bg('red'),
                                        reset=attr('reset')
                                        )
                    )

        logger.info("{fg}{bg}{einfo}".format(fg=fg("white"),
                                             bg=bg("red"),
                                             einfo=einfo
                                             )
                    )

        print '>> ExecuteAllEatries.on_failure'
        self.retry(exc=exc)


class GetEateryInfo_Base(Task):
    abstract = True
    ignore_result = True
    max_retries = 5
    acks_late = True
    default_retry_delay = 500

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        logger.info("{fg}{bg} Ending --<get_eatery_info>-- \
                    task, Completed{reset}".format(fg=fg('white'),
                                        bg=bg('green'),
                                        reset=attr('reset')
                                        )
                    )
        print ">> GetEateryInfo.after_return"
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.info("{fg}{bg} Ending --<get_eatery_info>-- \
                    task, failed miserably{reset}".format(fg=fg('white'),
                                        bg=bg('red'),
                                        reset=attr('reset')
                                        )
                    )

        logger.info("{fg}{bg}{einfo}".format(fg=fg("white"),
                                             bg=bg("red"),
                                             einfo=einfo
                                             )
                    )

        print ">> GetEateryInfo.on_failure"
        revoke(task_id, terminate=True)


class StartScraping_Base(Task):
    abstract = True
    ignore_result = True
    max_retries = 3
    acks_late = True
    default_retry_delay = 5

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        logger.info("{fg}{bg} Ending --<start_scraping>-- \
                    task, Completed{reset}".format(fg=fg('white'),
                                        bg=bg('green'),
                                        reset=attr('reset')
                                        )
                    )

        print ">> StartScraping.after_return"
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.info("{fg}{bg} Ending --<start_scraping>-- \
                    task, failed miserably{reset}".format(fg=fg('white'),
                                        bg=bg('red'),
                                        reset=attr('reset')
                                        )
                    )

        logger.info("{fg}{bg}{einfo}".format(fg=fg("white"),
                                             bg=bg("red"),
                                             einfo=einfo
                                             )
                    )

        print ">> StartScraping.on_failure"
        self.retry(exc=exc)


# class GoogleNPicsTask_Base(Task):
#     abstract = True
#     ignore_result=True, 
#     max_retries=5, 
#     acks_late=True
#     default_retry_delay = 500

#     def after_return(self, status, retval, task_id, args, kwargs, einfo):
#             #exit point of the task whatever is the state
#             pass

#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         print terminal.red("error occurred saving in redis %s for eatery_id %s"%(str(e), self.eatery_id))
#         r_pics.hset(self.eatery_id, "error", str(e))
#         revoke(task_id, terminate=True)
#         return 


@app.task(base=GetEateriesList_Base)
def get_eateries_list(url, number_of_resturants, skip, is_eatery):
    '''
    This task returns the eateries (returants) present in the url passed to it.
    '''
    #print "{start_color} {function_name}:: This worker is meant to get all the \
    #    eateries dict present\non the url given to it {end_color}".format(
    #        start_color=bcolors.OKGREEN, function_name=inspect.stack()[0][3],
    #        end_color = bcolors.RESET)

    print " >> GetEateriesList.run"
    obj = EateriesList(url, number_of_resturants, skip, is_eatery)
    result = obj.eateries_list
    return result


@app.task(base=ExecuteAllEatries_Base)
def execute_all_eateries(eateries_list, callback_func):
    print '>> ExecuteAllEatries.run'
    #for eatery in eateries_list:
    #   p = chain(GetEateryInfo.s(eatery), SaveIntoDB.s())
    #    p.delay()
    callback = subtask(callback_func)
    return group(callback.clone([arg,]) for arg in eateries_list)()


@app.task(base=GetEateryInfo_Base)
def get_eatery_info(eatery_dict, flush_eatery=False):
    # return
    print '>> GetEateryInfo.run'
    if flush_eatery:
        DBInsert.flush_eatery(eatery_dict)

    obj = EateryData(eatery_dict)
    eatery_data, reviews_list = obj.run()

    DBInsert.db_insert_eateries(eatery_data)
    DBInsert.db_insert_reviews(reviews_list)
    DBInsert.db_insert_users(reviews_list)

    reviews_in_db = DBInsert.db_get_reviews_eatery(eatery_dict["eatery_id"])

    try:
        if reviews_in_db !=  int(eatery_dict['eatery_total_reviews']):
            messege = "Umatched reviews: present in DB %s and should be %s"%(reviews_in_db,  int(eatery_dict['eatery_total_reviews']))
            print_messege("error", messege, "ScrapeEachEatery.run", None, eatery_dict["eatery_id"], eatery_dict["eatery_url"], None, module_name=FILE)

            if not reviews_in_db - 10 >= int(eatery_dict['eatery_total_reviews']) >= reviews_in_db + 10:
                r.hset(eatery_dict["eatery_url"], "unmatched_reviews", messege)
                r.hset(eatery_dict["eatery_url"], "total_reviews",  int(eatery_dict['eatery_total_reviews']))
                r.hset(eatery_dict["eatery_url"], "reviews_in_db", reviews_in_db)
                r.hset(eatery_dict["eatery_url"], "error_cause", "zomato incompetency")
                r.hset(eatery_dict["eatery_url"], "frequency", reviews_in_db -  int(eatery_dict['eatery_total_reviews']))
    except Exception as e:
        print terminal.red("Error in saving data into redis")
        print_exc()

    try:
        eatery_id, __eatery_id, eatery_name, eatery_photo_link, location = eatery_data["eatery_id"], eatery_data["__eatery_id"], eatery_dict["eatery_name"], eatery_data["eatery_photo_link"], eatery_data["location"]

        print terminal.blue("Trying pics for eatery_id=<<%s>>, __eatery_id=<<%s>>, eatery_photo_link=<<%s>>"%(eatery_id, __eatery_id, eatery_photo_link))

        instance = GoogleNPics(eatery_id, __eatery_id, eatery_photo_link)
        instance.run()
    except Exception as e:
        print terminal.red("Error in saving eatery pictures")
        print_exc()
        r_pics.hset(eatery_id, "error",  str(e))

    try:
        google = find_google_places(eatery_id, __eatery_id, eatery_name, location)
        print google
    except Exception as e:
        print terminal.red("Error in running google_places "+str(e))
        print_exc()

    return


@app.task(base= StartScraping_Base)
def start_scraping(url, number_of_restaurants, skip, is_eatery):
    process_list = get_eateries_list.s(url, number_of_restaurants, skip, is_eatery) | execute_all_eateries.s(get_eatery_info.s())
    process_list.delay()


# @app.task(base=GoogleNPicsTask_Base)
# def google_n_pics_task(eatery_id, __eatery_id, pics_url):
#         try:
#                 instance = GoogleNPics(eatery_id, __eatery_id, pics_url)
#                 instance.run()    
#         except Exception as e:
#                 print terminal.red("error occurred saving in redis %s for eatery_id %s"%(str(e), eatery_id))
#                 r_pics.hset(eatery_id, "error",  str(e))
#         return

@app.task()
def google_n_pics_task():
    return "OK"
