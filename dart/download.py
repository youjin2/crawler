# -*- coding: utf-8 -*-

from selenium import webdriver

import subprocess
import os
import logging

import pandas as pd


def srcAttribute(trTag):
    """srcAttribute

    Parameters
    ----------

    trTag : tag
        selenium tag object

    Returns
    -------
    """

    # finantial report column
    fr = trTag.find_elements_by_tag_name('td')[3]

    # covered by div tag
    src = trTag.find_elements_by_tag_name('div')[0]

    # outer download link
    aTag = src.find_elements_by_tag_name('a')[0]

    # java-script download link
    jsLink = aTag.get_attribute('onclick')

    startIndex = jsLink.index('http')
    endIndex = jsLink.index('zip') + 3

    return jsLink[startIndex:endIndex]


def setLogger(logLevel=logging.DEBUG):
    """setLogger

    Parameters
    ----------

    logLevel: logging.level
        logging level object

    Returns
    -------
    """
    from importlib import reload
    reload(logging)

    logger = logging.getLogger('Logger')
    fomatter = logging.Formatter('[%(levelname)s] > %(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(fomatter)
    logger.addHandler(streamHandler)

    if logLevel is not None:
        logger.setLevel(level=logLevel)

    return logger


def download(url, logger):
    """download

    Parameters
    ----------

    url : str
    logger : logger
        output of setLogger

    Returns
    -------
    """

    logger.info('======'*10)
    logger.info('URL: {}'.format(url))
    logger.info('======'*10)

    # unzip fille name
    fileName = url.split('/')[-1]
    # save dir
    saveDir = '_'.join(fileName.split('_')[:-1])

    # download
    state = subprocess.call(['wget', '-nc', url])
    if state == 0:
        logger.debug('download finished!')
    else:
        logger.debug('download failed!')

    # unzip
    state = subprocess.call(['unzip', '-O', 'euc-kr', fileName, '-d', saveDir])
    if state == 0:
        logger.debug('unzip finished!')
    else:
        logger.debug('unzip failed!')

    # root dir
    prevDir = os.getcwd()
    # change to save dir
    os.chdir(saveDir)
    # find Consolidated Financial Statements
    cfsName = [f for f in os.listdir(os.getcwd()) if '연결' in f][0]
    # save file name (after converting encoding to utf-8)
    saveName = cfsName.split('_')[-1]
    # convert encoding from euc-kr to utf-8
    state = subprocess.call(['iconv', '-f', 'euc-kr', '-t', 'utf-8', cfsName, '-o', saveName])
    if state == 0:
        logger.debug('encoding finished!')
    else:
        logger.debug('encoding failed!')

    # change to previous dir
    os.chdir(prevDir)

    logger.info('process succesfully finisihed!')


if __name__ == '__main__':

    # make data root directory if not exists
    rootDir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(rootDir):
        os.mkdir(rootDir)
    os.chdir(rootDir)

    # set logging level
    logger = setLogger(logging.DEBUG)

    # main url
    URL = 'http://dart.fss.or.kr/dsext002/main.do'

    # open browser
    driver = webdriver.PhantomJS()
    driver.get(URL)

    # get main table
    table = driver.find_elements_by_class_name('table_list')[0]
    # tbody tag in table
    body = table.find_elements_by_tag_name('tbody')[0]
    # each rows in table
    trTags = body.find_elements_by_tag_name('tr')

    # url list to download
    downloadURLs = [srcAttribute(tag) for tag in trTags]

    # iter over urls
    for url in downloadURLs:
        download(url, logger)

    # example data
    df = pd.read_table('2015_4Q_BS/20160531.txt')
    print(df.head())

