#!/usr/bin/env python
#-*- coding: utf-8 -*-

# project imports

# libraries imports
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from BeautifulSoup import BeautifulSoup
import getpass
from blessings import Terminal
import pymongo
from boto.s3.connection import S3Connection
from boto.exception import S3ResponseError, S3CreateError
import PIL
from PIL import Image
import requests

# std lib imports
import time
import os
import ConfigParser
import hashlib
import urllib2 as urllib
import shutil
from cStringIO import StringIO
import base64

from traceback import print_exc

terminal = Terminal()

FILE = os.path.basename(__file__)

config = ConfigParser.RawConfigParser()
config.read("zomato_dom.cfg")

driver_exec_path = "driver/chromedriver"
# DRIVER_NAME = "PhantomJS"
DRIVER_NAME = "Chrome"

connection = pymongo.MongoClient(config.get("zomato", "host"), config.getint("zomato", "port"))
ZomatoReviewsCollection = connection[config.get("zomato", "database")][config.get("zomato", "reviews")]
ZomatoEateriesCollection = connection[config.get("zomato", "database")][config.get("zomato", "eatery")]
PicturesCollection = connection[config.get("zomato", "picsdatabase")][config.get("zomato", "picscollection")]
PictureContentCollection = connection.PictureContentCollection.PictureContentCollection


class GoogleNPics(object):
    def __init__(self, eatery_id, __eatery_id, url):
        '''
        Args:
            eatery_id : id of the resturant on zomato

            __eatery_id : hash created for the eatery of eatery_id,
                          saved in database (mongo)

            url: link for the eatery
        '''
        self.eatery_id = eatery_id
        self.__eatery_id = __eatery_id
        if url:
            self.url = url
        else:
            try:
                self.find_photo_link()                        
            except StandardError as e:
                print terminal.red(str(e))
        try:
            s3_connection = S3Connection(config.get("aws", "key"), config.get("aws", "secret"))
        except Exception as e:
            print terminal.on_red("Error in creating connection to S3")
            print terminal.red(str(e))
            self.terminate_process = True

        try:
            # self.bucket = s3_connection.get_bucket(config.get("aws", "bucket"))

            # lookup works same as get_bucket; except it returns None if bucket is not present;
            # getting the bucket 
            self.bucket = s3_connection.lookup(config.get("aws", "bucket"))

            if not self.bucket:
                # self.bucket will be None if bucket is not present on the s3 server;
                # so we create the bucket first and get it into self.bucket
                print 'creating new bucket...'
                s3_connection.create_bucket(config.get("aws", "bucket"))
                self.bucket = s3_connection.lookup(config.get("aws", "bucket"))
        except Exception as e:
            print terminal.on_red("Error in accessing Bucket")
            print terminal.red(str(e))
            self.terminate_process = True
            return

        self.basewidth = 400
        self.image_format = "jpeg"

        # flag to indicate if error occurs in connecting to S3 server
        self.terminate_process = False


    def find_photo_link(self):
        '''
        Returns the url for the image page after getting the url from database or using
        the url provided within the construtor.
        '''
        __eatery = ZomatoEateriesCollection.find_one({"eatery_id": self.eatery_id})
        __url = "%s/info"%(__eatery.get("eatery_url"))

        driver = webdriver.Chrome(driver_exec_path)
        time.sleep(10)
        driver.get(__url)

        html = driver.page_source
        soup = BeautifulSoup(html)

        try:
            # updating the url for the photo section
            # of the page from eatery url
            self.url += __url

            if self.url[-1] != '/':
                self.url += '/'

            self.url += 'photos'

            ZomatoEateriesCollection.update({"eatery_id": self.eatery_id},
                                            {"$set": 
                                                {"eatery_photo_link": self.url}
                                            }, upsert=False)
        except Exception as e:
            driver.close()
            # raise StandardError("Culdnt get the eatery photo link for eatery id %s"%self.eatery_id)
            print terminal.red("Error in getting photo link for eatery")

        try:
            eatery_area_or_city = soup.find("div", {"class": "borderless res-main-address"}).text

            print terminal.blue("eatery_area_or_city is <<%s>> for eatery id \
                                <%s>> for eatery url <<%s>>"%(eatery_area_or_city,
                                                              self.eatery_id,
                                                              __eatery.get("eatery_url"))) 

            ZomatoEateriesCollection.update({"eatery_id": self.eatery_id},
                                            {"$set": 
                                                {"eatery_area_or_city": eatery_area_or_city}
                                            }, upsert=False)
        except Exception as e:
            driver.close()
            print terminal.red("eatery_area_or_city couldnt be found for eatery id \
                                <<%s>> for eatery url <<%s>>"%(self.eatery_id, 
                                                                __eatery.get("eatery_url"))) 

        print ZomatoEateriesCollection.find_one({"eatery_id": self.eatery_id})
        driver.close()
        return

    def run(self):
        '''
        Start the process of fetching images from the photos section of the eatery,
        and storing all the images on the aws server.
        '''

        if self.terminate_process:
            return

        self.pictures = None
        # if urls of the pictures for the eatery are already present in the database,
        # get all the urls, else get the urls by loading the webdriver with the link
        prev_pictures_urls = ZomatoEateriesCollection.find_one({"eatery_id": self.eatery_id})
        if prev_pictures_urls:
            self.pictures = prev_pictures_urls.get("pictures")

        if self.pictures:
            print terminal.blue("Pictures for the eatery_id %s has already been found"%self.eatery_id)
            self.pictures = prev_pictures_urls.get("pictures")
            # self.pictures = ZomatoEateriesCollection.find_one({"eatery_id": self.eatery_id}).get("pictures")
        else:
            if self.get_image_urls():
                print 'ok...'
                ZomatoEateriesCollection.update({"eatery_id": self.eatery_id},
                                                {"$set": 
                                                    {"pictures": self.pictures}
                                                }, upsert=False, multi=False)
            else:
                print terminal.on_red("Terminating process")
                print terminal.on_red("Failed to get images urls")
                return
        
        print terminal.blue("Total number of pics found %s"%len(self.pictures))

        # getting the cdn pics only from the list of all urls
        zomato_cdn_pics = [image for image in self.pictures if image.startswith("https://b.zmtcdn.com")]
        print terminal.blue("Total number of pics  found  on zomato cdn %s"%len(zomato_cdn_pics))

        if PicturesCollection.find({"eatery_id": self.eatery_id}).count() > 25:
            print terminal.red("Images for eatery_id %s has already been stored on s3"%self.eatery_id)
            return 

        i = 0

        # storing top (last from list) 30 images of the eatry to the amazon sever
        for image_link in zomato_cdn_pics[-30:]: # should be 30
            if i > 30: # should be 30
                break
            try:
                # if not self.each_image(image_link, i):
                #     print terminal.on_red(" >> Failed to save image at "+str(image_link))
                #     print terminal.red(" >> Err: "+str(e))

                key, s3_url, s3_url_original, image_contents, height, width = self.each_image(image_link)

                # convert the image contents into base64 encoding
                image_contents = base64.b64encode(image_contents)

                # inserting into database (mongo)
                print PicturesCollection.insert({"s3_url": s3_url,
                                                 "url": image_link, 
                                                 "s3_url_original": s3_url_original,
                                                 "height": height,
                                                 "width": width,
                                                 "image_id": key,
                                                 "eatery_id":  self.eatery_id,
                                                 "__eatery_id": self.__eatery_id,
                                                 "source": "zomato",
                                                 "time": time.time()
                                                 })
                
                print PictureContentCollection.insert({"url": image_link,
                                                       "contents": image_contents,
                                                       "s3_url": s3_url_original,
                                                       "height": height, 
                                                       "width": width, 
                                                       "image_id": key, 
                                                       "eatery_id":  self.eatery_id,
                                                       "__eatery_id": self.__eatery_id,
                                                       "source": "zomato",
                                                       "time": time.time()
                                                       })

                i += 1
            except Exception as e:
                print terminal.on_red("Error in processing image :"+image_link)
                print terminal.red(str(e))
                pass
        return

    def get_image_urls(self):
        '''
        This function loads the page in the webdriver and loads all the images for the eatery.
        Returns the links extractd from soup object of the page source after loading all the images.
        '''
        try:
            # fire up the webdriver
            if DRIVER_NAME == "PhantomJS":
                driver = webdriver.PhantomJS()
            else:
                driver = webdriver.Chrome(driver_exec_path)
            # load the eatery photo url
            driver.get(self.url)
        except Exception as e:
            driver.close()
            print terminal.red("Failed to load the url <<%s>> \n Error: \
                                <<%s>>"%(self.url, str(e)))
            print_exc()
            return

        # counters to keep track of the errors
        no_such_element_err_count = 0
        err_count  = 0
        while True:
            # keep clicking "Load-more" button until all the pics are loaded;
            # break the loop if NoSuchElementException errors occurs multiple times
            try:
                driver.find_element_by_class_name("picLoadMore").click()
                time.sleep(3)
                no_such_element_err_count = 0
            except NoSuchElementException:
                no_such_element_err_count += 1
                if no_such_element_err_count > 5:
                    # if NoSuchElement err count becomes greater than 5; 
                    # terminate
                    break
            except Exception as e:
                # if page keeps on producing error till 
                # err_count becomes 10; terminate
                err_count += 1
                if err_count > 10:
                    break
                pass

        try:
            # get the page source and convert it into soup object
            # and get the links of the images into the a list
            soup = BeautifulSoup(driver.page_source)
            self.pictures = []

            for link_tag in soup.findAll("a", {"class": "res-info-thumbs"}):
                try:
                    # extract the url from the element and fix its url string;
                    # e.g, the initial url string will be
                    #   https://b.zmtcdn.com/data/pictures/6/3466/0325f528f8bea045ef6155d94bb24e6a.jpg?\
                    #   fit=around%7C200%3A200&crop=200%3A200%3B%2A%2C%2A&output-format=webp
                    # the upper part will be the real url and needs to be fixed before it is appended
                    # in the list
                    link = link_tag.find("img")['data-original']
                    self.pictures.append(link[:link.rfind(".jpg")+len(".jpg")])
                except Exception as e:
                    print terminal.on_red("pic failed <<"+str(link_tag)+">>\nError: "+str(e))
                    pass

            time.sleep(5)
            return True
        except Exception as e:
            print terminal.red("Failed to get image urls from url <<%s>> \n Error: \
                                <<%s>>"%(self.url, str(e)))

    def each_image(self, image_link):
        # print "Image link is %s\n\n"%image_link
        try:
            if config.getboolean("proxy", "use_proxy"):
                # setting the proxy if use_proxy flag is enabled
                proxy_dict = {"http": config.get("proxy", "proxy_addr"),
                              "https": config.get("proxy", "proxy_addr")
                              }
                proxy = urllib.ProxyHandler(proxy_dict)
                opener = urllib.build_opener(proxy)
                urllib.install_opener(opener)

                # opening the icanhazip.com to check the ip genered with the proxy
                try:
                    response = urllib.urlopen("http://www.icanhazip.com")
                    source = response.read()
                    print terminal.red("From proxy %s"%source)
                except Exception as e:
                    print terminal.red("Could scrape icanhazip")
                    pass

            # opening the image url and downlaod the image content
            response = urllib.urlopen(image_link)
            source = response.read()
            # converting the image content into 'Image' object
            img = Image.open(StringIO(source))

            # if not os.path.exists(os.getcwd()+"/temp_images"):
            #     os.mkdir('temp_images')
            # img.save("temp_images/image_"+str(image_num)+".jpg")
            # return True

        except Exception as e:
            print terminal.red(str(e))
            return None
        print terminal.yellow("This is the image object %s for eatery_id <<%s>>"%(img, self.eatery_id))
        return self.generate_link(img, image_link)


    def generate_link(self, eatery_image, image_link):
        wpercent = (self.basewidth/float(eatery_image.size[0]))
        hsize = int((float(eatery_image.size[1])*float(wpercent)))
        
        ##resizing an pil image according to the basewidth wihch happend to be 400
        resized_img = eatery_image.resize((self.basewidth, hsize), PIL.Image.ANTIALIAS)

        output = StringIO()
        
        ##saving the resized image to output string io string
        resized_img.save(output, self.image_format)
        
        ##contents of the image 
        ###saving original image to a stringIO
        original_image = StringIO()
        eatery_image.save(original_image, self.image_format)
        eatery_image_contents = original_image.getvalue()

        ##generateing a unique key for the image
        __key = "%s_zcdn_%s"%(self.eatery_id, hashlib.sha224(eatery_image_contents).hexdigest())
        s3_key = self.bucket.new_key(__key)
        s3_key.set_metadata('Content-Type', 'image/jpg')
        s3_key.set_contents_from_string(output.getvalue())
        s3_key.set_canned_acl('public-read')
        s3_image_url = s3_key.generate_url(0, query_auth=False, force_http=True)
       
        ##generateing a unique key for the image
        __key_original = "%s_zcdn_%s_original"%(self.eatery_id, hashlib.sha224(eatery_image_contents).hexdigest())
        s3_key = self.bucket.new_key(__key_original)
        s3_key.set_metadata('Content-Type', 'image/jpg')
        s3_key.set_contents_from_string(eatery_image_contents)
        s3_key.set_canned_acl('public-read')
        s3_image_url_original = s3_key.generate_url(0, query_auth=False, force_http=True)

        print terminal.yellow("This is the url for the image %s for eatery_id <<%s>>"%(s3_image_url, self.eatery_id))
        print terminal.yellow("This is the url for the image original %s for eatery_id <<%s>>"%(s3_image_url_original, self.eatery_id))
        return (__key, s3_image_url, s3_image_url_original, eatery_image_contents, eatery_image.height, eatery_image.width)

'''
if __name__ == "__main__":
    obj = GoogleNPics("300716", "bbf", "https://www.zomato.com/ncr/off-campus-satyaniketan-new-delhi/photos")
    obj.run()
'''