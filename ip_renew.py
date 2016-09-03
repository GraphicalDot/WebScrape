#!/usr/bin/env python

from TorCtl import TorCtl
import urllib2
from selenium import webdriver
import re
from selenium.webdriver.common.proxy import Proxy, ProxyType
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read("zomato_dom.cfg")








user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent}
def request(url):
        def _set_urlproxy():
                proxy_support = urllib2.ProxyHandler({"http" : "localhost:8118"})
                opener = urllib2.build_opener(proxy_support)
                urllib2.install_opener(opener)
        _set_urlproxy()
        request=urllib2.Request(url, None, headers)
        return urllib2.urlopen(request).read()

def selenium_request(url):
        proxy_address = "localhost:8118"
        proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': proxy_address,})

        service_args = [
                    '--proxy=localhost:8118',
                    ]

        driver = webdriver.PhantomJS(service_args=service_args)
        driver.get(url)
        html = driver.page_source
        driver.close()
        ip = re.findall("\d+.\d+.\d+.\d+", html)

        return ip[0]

def renew_connection():
        conn = TorCtl.connect(controlAddr="localhost", controlPort=9051)
        conn.send_signal("NEWNYM")
        conn.close()
for i in range(0, 100):
        renew_connection()
        print selenium_request("http://icanhazip.com/")



def generate_new_proxy():
        """
        if proxy os True in zomato_dom.cfg then it connects to tor and privoxy and find a new proxy
            and redirects all the selenium requests through this proxy
        if False, return the true ip of the server
        """
        print "Called generate_new_proxy"
        def renew_connection():
                conn = TorCtl.connect(controlAddr="localhost", controlPort=9051)
                conn.send_signal("NEWNYM")
                conn.close()

        def selenium_request(url, use_proxy):
                if use_proxy:
                        service_args =[config.get("proxy", "service_args")]
                        driver = webdriver.PhantomJS(service_args=service_args)
                else:
                        driver = webdriver.PhantomJS()

                driver.get(url)
                html = driver.page_source
                driver.close()
                ip = re.findall("\d+.\d+.\d+.\d+", html)
                return ip[0]

        if config.getboolean("proxy", "use_proxy"):
                        renew_connection()
                        ##__ip = selenium_request("http://ifconfig.me/ip", use_proxy=True)
                        __ip = selenium_request("http://icanhazip.com/", use_proxy=True)

        else:
            __ip = selenium_request("http://icanhazip.com/", use_proxy=False)
            print "The new ip being allocated is %s"%__ip
        return __ip

