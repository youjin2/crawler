# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import os

import time

from collections import namedtuple

import tqdm


class ExtractVideoList(object):

    def __init__(self, url, n=20):

        self.url = url

        # pagedown for PhantomJS does not works..
        # driver = webdriver.PhantomJS()
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        time.sleep(1)

        self.nPageDown = n

        self.video = namedtuple('video', ['title', 'url'])

    def __call__(self):

        bodyTag = self.driver.find_element_by_tag_name("body")

        while self.nPageDown:
            bodyTag.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)
            self.nPageDown -= 1

        aTags = bodyTag.find_elements_by_xpath('//div/h3/a')

        videoList = []
        for a in aTags:
            title = a.get_attribute('title')
            url = a.get_attribute('href')
            videoList.append(self.video(title, url))

        self.driver.close()

        return videoList


if __name__ == '__main__':

    url = 'https://www.youtube.com/channel/UCGDA1e6qQSAH0R9hoip9VrA/videos'
    videoList = ExtractVideoList(url)()
    print(videoList)
