# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import re

import os
import logging

from collections import namedtuple

import tqdm


class ExtractVideoList(object):
    """ExtractVideoList
    Extract title/url from youtube channel video list
    """

    def __init__(self, url, n=30):
        """__init__

        Parameters
        ----------

        url : str
        n : int
            the number of scroll down trials

        Returns
        -------
        """

        self.url = url

        # pagedown for PhantomJS does not works..
        # driver = webdriver.PhantomJS()
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        time.sleep(1)

        self.nPageDown = n

        self.video = namedtuple('video', ['title', 'url'])

    def __call__(self):
        """__call__"""

        bodyTag = self.driver.find_element_by_tag_name("body")

        # scroll down for searching more videos
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


class DownloadSoundFile(object):
    """DownloadSoundFile
    extract and save sound file from video link
    """

    def __init__(self, artistName, waitTime=20):
        """__init__

        Parameters
        ----------

        artistName : str
            video channel name

        Returns
        -------
        """

        # TODO: sometimes title name does not assigned appropriately:w
        # guess it related to the max length of title
        self.maxLen = 10
        self.waitTime = waitTime

        self.artistName = artistName
        self.downloadDir = '/home/ygene/다운로드'

        self.baseURL = 'http://convert2mp3.net/index.php'
        # empirically determined
        self.blockIdentifier = 'style="position: absolute !important; ' +\
            'height: 20px !important; width: 20px !important; top: 3px ' +\
            '!important; left: 3px !important; background: '

        self.driver = webdriver.Chrome()

    def openMainBrowser(self):
        """openMainBrowser
        open main browser
        """
        # TODO: sometimes takes too much time for loading main browser
        # don't have any idea..
        self.driver.get(self.baseURL)
        WebDriverWait(self.driver, self.waitTime).\
            until(EC.presence_of_element_located([By.CLASS_NAME, 'span9']))
        # wait few seconds in case of appearing block image
        time.sleep(5)

        self.removeBlockImage()

    def removeBlockImage(self):
        """removeBlockImage
        there sometimes appears block image
        which prevents passing video url
        """

        if self.blockIdentifier in self.driver.page_source:
            endIdx = self.driver.page_source.find(self.blockIdentifier)
            startIdx = self.driver.page_source.split(self.blockIdentifier)[0].\
                rfind('id=')

            # id randomly generated
            # so one should extract this random value
            # to removing the block image
            idValue = self.driver.page_source[startIdx:endIdx].strip('').\
                split('"')[1]

            xButton = self.driver.find_element_by_id(idValue)
            xButton.click()
            WebDriverWait(self.driver, self.waitTime).until(
                EC.presence_of_element_located(
                    [By.XPATH,
                     "//button[contains(text(), 'umwandeln')]"]
                )
            )
            time.sleep(2)

    def passVideoInfo(self, title):
        """passVideoInfo
        pass video title and artist name
        change to next step for download

        Parameters
        ----------

        title : str

        Returns
        -------
        """
        buttons = self.driver.find_elements_by_class_name('btn')

        clearInterpret, clearTitle = [
            b for b in buttons if 'bearbeiten' in b.text
        ]
        nextStep = [b for b in buttons if 'Weiter' in b.text][0]

        clearInterpret.click()
        inputArtist = self.driver.find_element_by_id('inputArtist')
        inputArtist.clear()
        inputArtist.send_keys(self.artistName)

        clearTitle.click()
        inputTitle = self.driver.find_element_by_id('inputTitle')
        inputTitle.clear()

        # _title = re.sub('[^가-힣a-z|_0-9]', ' ', title).lstrip(' ')
        _title = re.sub('[^가-힣a-z|]', ' ', title).lstrip(' ')
        _title = _title.replace('|', ' ').replace(' ', '')
        print(_title[:self.maxLen])
        inputTitle.send_keys(_title[:self.maxLen])

        nextStep.click()
        WebDriverWait(self.driver, self.waitTime).until(
            EC.presence_of_element_located([By.CLASS_NAME, 'icon-download']))

    def download(self, title, url):
        """download

        Parameters
        ----------

        title : str
        url : str

        Returns
        -------
        """

        urlInput = self.driver.find_element_by_name('url')
        urlInput.clear()
        urlInput.send_keys(url)

        button = self.driver.find_elements_by_xpath(
            "//button[contains(text(), 'umwandeln')]")[0]
        button.click()
        WebDriverWait(self.driver, self.waitTime).until(
            EC.presence_of_element_located([By.CLASS_NAME,
                                            'form-horizontal']))
        self.passVideoInfo(title)

        buttons = self.driver.find_elements_by_class_name('btn')
        download = [b for b in buttons if 'Download starten' in b.text][0]
        download.click()
        time.sleep(5)

    def closePopUpBrowser(self):
        """closePopUpBrowser
        close unintentionally opened browser
        which is result of passing video url (first step)
        """

        if len(self.driver.window_handles) > 1:
            for window in self.driver.window_handles[1:]:
                self.driver.switch_to_window(window)
                self.driver.close()
                time.sleep(0.5)

        self.driver.switch_to_window(self.driver.window_handles[0])

    def __call__(self, videos):
        """__call__

        Parameters
        ----------

        videos : list
            returns of ExtractVideoList()

        Returns
        -------
        """

        digits = len(str(len(videos)))
        for i, video in tqdm.tqdm(enumerate(videos, 1)):
            suffix = '{}_'.format(str(i).zfill(digits))
            self.openMainBrowser()
            self.download(suffix + video.title, video.url)
            self.closePopUpBrowser()

        while True:
            files = os.listdir(self.downloadDir)
            finished = all([
                not bool(re.search('^{}.*crdownload$'.format(self.artistName),
                                   f))
                for f in files
            ])

            if not finished:
                print('Downloading Files..')
                time.sleep(10)
            else:
                print('Download Completed!')
                break

        for window in self.driver.window_handles:
            self.driver.switch_to_window(window)
            self.driver.close()


if __name__ == '__main__':

    # url = 'https://www.youtube.com/channel/UCGDA1e6qQSAH0R9hoip9VrA/videos'
    # videoList = ExtractVideoList(url)()

    # video = videoList[100]
    # print(video)

    # time.sleep(1)

    import pickle
    video = namedtuple('video', ['title', 'url'])
    with open('videoList.pkl', 'rb') as f:
        videoList = pickle.load(f)

    downloader = DownloadSoundFile('convs')
    downloader(videoList)

